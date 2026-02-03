from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import SysUser, SysDept, SysRole
from app.schemas import UserCreate, UserUpdate, UserResponse, UserPasswordReset
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_users(
    username: str = None, 
    dept_id: int = None,
    phone: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(SysUser)
    if username:
        query = query.filter(SysUser.username.like(f"%{username}%"))
    if dept_id:
        query = query.filter(SysUser.dept_id == dept_id)
    if phone:
        query = query.filter(SysUser.phone.like(f"%{phone}%"))
        
    users = query.all()
    
    # 填充关联信息 (门店名、角色名)
    result = []
    for u in users:
        u_data = UserResponse.from_orm(u)
        if u.dept_id:
            dept = db.query(SysDept).filter(SysDept.id == u.dept_id).first()
            if dept: u_data.dept_name = dept.dept_name
        if u.role_id:
            role = db.query(SysRole).filter(SysRole.id == u.role_id).first()
            if role: u_data.role_name = role.role_name
        result.append(u_data)
    return result

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 查重
    if db.query(SysUser).filter(SysUser.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if user.phone and db.query(SysUser).filter(SysUser.phone == user.phone).first():
        raise HTTPException(status_code=400, detail="手机号已存在")
        
    db_user = SysUser(
        username=user.username,
        password=get_password_hash(user.password), # 密码加密存储
        phone=user.phone,
        dept_id=user.dept_id,
        role_id=user.role_id,
        post=user.post,
        status=user.status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    # 更新基本信息
    db_user.username = user.username
    db_user.phone = user.phone
    db_user.dept_id = user.dept_id
    db_user.role_id = user.role_id
    db_user.post = user.post
    db_user.status = user.status
    
    # 如果请求中包含密码，则修改密码
    if user.password:
        db_user.password = get_password_hash(user.password)
        
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 保护超级管理员账号
    if db_user.username == 'admin':
        raise HTTPException(status_code=400, detail="超级管理员不允许删除")
        
    db.delete(db_user)
    db.commit()
    return {"msg": "删除成功"}

@router.put("/{user_id}/status")
def toggle_status(user_id: int, status: int, db: Session = Depends(get_db)):
    if status not in [0, 1]:
        raise HTTPException(status_code=400, detail="状态值错误")
    
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    if db_user.username == 'admin':
        raise HTTPException(status_code=400, detail="超级管理员不允许禁用")
        
    db_user.status = status
    db.commit()
    return {"msg": "状态更新成功"}

# --- 新增：重置密码接口 ---
@router.put("/{user_id}/password")
def reset_password(user_id: int, item: UserPasswordReset, db: Session = Depends(get_db)):
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if db_user.username == 'admin':
        # 实际上管理员可以重置自己的，但为了安全通常建议走个人中心修改，这里暂不限制
        pass

    # 强制更新密码
    db_user.password = get_password_hash(item.new_password)
    db.commit()
    
    return {"msg": "密码重置成功"}