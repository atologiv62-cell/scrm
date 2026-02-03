from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import SysDept, SysUser
from app.schemas import DeptCreate, DeptUpdate, DeptResponse

router = APIRouter()

# 生成门店编号 (YYYYMMDD + 4位流水)
def generate_dept_code(db: Session) -> str:
    today_str = datetime.now().strftime('%Y%m%d')
    last_dept = db.query(SysDept).filter(
        SysDept.dept_code.like(f"{today_str}%")
    ).order_by(SysDept.dept_code.desc()).first()
    
    if not last_dept:
        return f"{today_str}0001"
    
    try:
        last_seq = int(last_dept.dept_code[-4:])
        new_seq = last_seq + 1
        return f"{today_str}{new_seq:04d}"
    except:
        return f"{today_str}0001"

@router.get("/", response_model=List[DeptResponse])
def get_depts(name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SysDept)
    if name:
        query = query.filter(SysDept.dept_name.like(f"%{name}%"))
    
    depts = query.all()
    result = []
    for dept in depts:
        dept_data = DeptResponse.from_orm(dept)
        if dept.leader_id:
            leader = db.query(SysUser).filter(SysUser.id == dept.leader_id).first()
            if leader:
                dept_data.leader_name = leader.username
        result.append(dept_data)
    return result

@router.post("/", response_model=DeptResponse)
def create_dept(dept: DeptCreate, db: Session = Depends(get_db)):
    new_code = generate_dept_code(db)
    db_dept = SysDept(
        dept_code=new_code,
        dept_name=dept.dept_name,
        leader_id=dept.leader_id,
        status=dept.status
    )
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.put("/{dept_id}", response_model=DeptResponse)
def update_dept(dept_id: int, dept: DeptUpdate, db: Session = Depends(get_db)):
    db_dept = db.query(SysDept).filter(SysDept.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="门店不存在")
    
    db_dept.dept_name = dept.dept_name
    db_dept.leader_id = dept.leader_id
    db_dept.status = dept.status
    
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.delete("/{dept_id}")
def delete_dept(dept_id: int, db: Session = Depends(get_db)):
    db_dept = db.query(SysDept).filter(SysDept.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="门店不存在")
    db.delete(db_dept)
    db.commit()
    return {"msg": "删除成功"}

@router.put("/{dept_id}/status")
def toggle_status(dept_id: int, status: int, db: Session = Depends(get_db)):
    db_dept = db.query(SysDept).filter(SysDept.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="门店不存在")
    db_dept.status = status
    db.commit()
    return {"msg": "状态更新成功"}