from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import SysRole
from app.schemas import RoleCreate, RoleUpdate, RoleResponse

router = APIRouter()

def generate_role_code(db: Session) -> str:
    # 格式：YYYYMMDD + 01 (2位流水)
    today_str = datetime.now().strftime('%Y%m%d')
    last_role = db.query(SysRole).filter(SysRole.role_code.like(f"{today_str}%")).order_by(SysRole.role_code.desc()).first()
    if not last_role:
        return f"{today_str}01"
    try:
        last_seq = int(last_role.role_code[-2:])
        new_seq = last_seq + 1
        return f"{today_str}{new_seq:02d}"
    except:
        return f"{today_str}01"

@router.get("/", response_model=List[RoleResponse])
def get_roles(name: str = None, db: Session = Depends(get_db)):
    query = db.query(SysRole)
    if name:
        query = query.filter(SysRole.role_name.like(f"%{name}%"))
    return query.all()

@router.post("/", response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    new_code = generate_role_code(db)
    db_role = SysRole(
        role_code=new_code, 
        role_name=role.role_name, 
        permissions=role.permissions,
        status=role.status # 支持创建时设置状态
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db)):
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    db_role.role_name = role.role_name
    db_role.permissions = role.permissions
    
    # 如果请求中包含 status，则更新
    if role.status is not None:
        db_role.status = role.status
        
    db.commit()
    db.refresh(db_role)
    return db_role

@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    db.delete(db_role)
    db.commit()
    return {"msg": "删除成功"}

# --- 新增：状态切换接口 ---
@router.put("/{role_id}/status")
def toggle_role_status(role_id: int, status: int, db: Session = Depends(get_db)):
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    db_role.status = status
    db.commit()
    return {"msg": "状态更新成功"}