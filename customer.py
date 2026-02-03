from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Optional
from app.database import get_db
from app.models import CrmCustomer, SysUser, SysDept, SysRole, CrmProduct, SysOperationLog, CrmFollowRecord
from app.schemas import CustomerCreate, CustomerUpdate, CustomerResponse, LogResponse, FollowCreate, FollowResponse, CustomerTransfer
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- 辅助函数: 获取当前登录用户 ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效凭证")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")
    
    user = db.query(SysUser).filter(SysUser.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

# --- 辅助函数: 记录操作日志 ---
def add_log(db: Session, ref_id: int, operator: str, action: str, content: str):
    log = SysOperationLog(
        ref_id=ref_id,
        operator_name=operator,
        action_type=action,
        content=content
    )
    db.add(log)
    db.commit()

# --- 1. 获取客户列表 (带权限控制) ---
@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    status: Optional[str] = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(CrmCustomer)
    
    # 权限逻辑
    user_role = db.query(SysRole).filter(SysRole.id == current_user.role_id).first()
    is_admin = user_role and ('管理员' in user_role.role_name or 'admin' in user_role.role_code.lower())
    
    if not is_admin:
        if current_user.dept_id:
            query = query.filter(CrmCustomer.dept_id == current_user.dept_id)
            if current_user.post == '导购':
                query = query.filter(CrmCustomer.owner_id == current_user.id)
    
    # 筛选条件
    if name:
        query = query.filter(CrmCustomer.customer_name.like(f"%{name}%"))
    if phone:
        query = query.filter(CrmCustomer.phone.like(f"%{phone}%"))
    if status:
        query = query.filter(CrmCustomer.follow_status == status)
        
    customers = query.order_by(CrmCustomer.create_time.desc()).all()
    
    # 填充关联显示的名称
    result = []
    for c in customers:
        res = CustomerResponse.from_orm(c)
        if c.dept_id:
            d = db.query(SysDept).filter(SysDept.id == c.dept_id).first()
            if d: res.dept_name = d.dept_name
        if c.owner_id:
            u = db.query(SysUser).filter(SysUser.id == c.owner_id).first()
            if u: res.owner_name = u.username
        if c.intent_product_id:
            p = db.query(CrmProduct).filter(CrmProduct.id == c.intent_product_id).first()
            if p: res.intent_product_name = p.product_name
        result.append(res)
        
    return result

# --- 2. 新增客户 ---
@router.post("/", response_model=CustomerResponse)
def create_customer(
    item: CustomerCreate, 
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if db.query(CrmCustomer).filter(CrmCustomer.phone == item.phone).first():
        raise HTTPException(status_code=400, detail="手机号已存在")
        
    db_item = CrmCustomer(**item.dict())
    
    if not db_item.owner_id:
        db_item.owner_id = current_user.id
    if not db_item.dept_id:
        db_item.dept_id = current_user.dept_id
    if not db_item.follow_status:
        db_item.follow_status = "待分配"
    
    # 初始化统计字段
    db_item.follow_count = 0
        
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    add_log(db, db_item.id, current_user.username, "新增客户", f"创建了客户: {item.customer_name}")
    return db_item

# --- 3. 修改客户 ---
@router.put("/{id}", response_model=CustomerResponse)
def update_customer(
    id: int, 
    item: CustomerUpdate, 
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_item = db.query(CrmCustomer).filter(CrmCustomer.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="客户不存在")
        
    changes = []
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        old_val = getattr(db_item, field)
        if str(old_val) != str(value):
            changes.append(f"{field}: {old_val} -> {value}")
            setattr(db_item, field, value)
            
    db.commit()
    db.refresh(db_item)
    
    if changes:
        add_log(db, id, current_user.username, "修改客户", "; ".join(changes))
        
    return db_item

# --- 4. 客户跟进人批量转移 ---
@router.post("/transfer")
def transfer_customer(
    transfer_data: CustomerTransfer,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_role = db.query(SysRole).filter(SysRole.id == current_user.role_id).first()
    is_admin = user_role and ('管理员' in user_role.role_name or 'admin' in user_role.role_code.lower())
    is_leader = current_user.post == '店长' or (user_role and '店长' in user_role.role_name)
    
    if not is_admin and not is_leader:
        raise HTTPException(status_code=403, detail="权限不足：只有管理员或店长可以批量转移客户")

    new_owner = db.query(SysUser).filter(SysUser.id == transfer_data.new_owner_id).first()
    if not new_owner:
        raise HTTPException(status_code=404, detail="目标跟进人不存在")

    transferred_count = 0
    new_owner_name = new_owner.username
    
    for customer_id in transfer_data.customer_ids:
        customer = db.query(CrmCustomer).filter(CrmCustomer.id == customer_id).first()
        if not customer:
            continue

        if not is_admin:
            if customer.dept_id != current_user.dept_id:
                continue 

        old_owner_name = "公海/未知"
        if customer.owner_id:
            old_u = db.query(SysUser).filter(SysUser.id == customer.owner_id).first()
            if old_u: old_owner_name = old_u.username
            
        customer.owner_id = transfer_data.new_owner_id
        if new_owner.dept_id:
            customer.dept_id = new_owner.dept_id
            
        add_log(
            db, 
            customer_id, 
            current_user.username, 
            "转移客户", 
            f"跟进人由 [{old_owner_name}] 转移至 [{new_owner_name}]"
        )
        transferred_count += 1
            
    db.commit()
    return {"msg": f"成功转移 {transferred_count} 个客户给 {new_owner_name}"}

# --- 5. 获取操作日志 ---
@router.get("/{id}/logs", response_model=List[LogResponse])
def get_customer_logs(id: int, db: Session = Depends(get_db)):
    return db.query(SysOperationLog).filter(SysOperationLog.ref_id == id).order_by(SysOperationLog.create_time.desc()).all()

# --- 6. 获取跟进记录 ---
@router.get("/{id}/follows", response_model=List[FollowResponse])
def get_customer_follows(id: int, db: Session = Depends(get_db)):
    return db.query(CrmFollowRecord).filter(CrmFollowRecord.customer_id == id).order_by(CrmFollowRecord.create_time.desc()).all()

# --- 7. 创建跟进记录 (核心功能：自动累加次数和更新时间) ---
@router.post("/{id}/follows", response_model=FollowResponse)
def create_customer_follow(
    id: int, 
    item: FollowCreate, 
    current_user: SysUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    customer = db.query(CrmCustomer).filter(CrmCustomer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    # 1. 保存记录
    follow_data = item.dict()
    follow_data['customer_id'] = id
    
    follow = CrmFollowRecord(**follow_data)
    follow.follower_name = current_user.username
    db.add(follow)
    
    # 2. 更新客户状态
    if item.follow_tag:
        customer.follow_status = item.follow_tag 
    
    # 3. 更新最后跟进时间 (Now)
    customer.update_time = func.now()
    customer.last_follow_time = func.now()
    
    # 4. 自动累加跟进次数
    current_count = customer.follow_count or 0
    customer.follow_count = current_count + 1
        
    # 5. 写入操作日志
    add_log(
        db, 
        id, 
        current_user.username, 
        "跟进客户", 
        f"第{customer.follow_count}次跟进: [{item.follow_tag}] {item.follow_detail}"
    )
    
    db.commit()
    db.refresh(follow)
    return follow