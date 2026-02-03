from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import SysRegionAllocation, SysDept, SysUser
from app.schemas import AllocationCreate, AllocationUpdate, AllocationResponse

router = APIRouter()

@router.get("/", response_model=List[AllocationResponse])
def get_allocations(
    dept_id: Optional[int] = None,
    province: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SysRegionAllocation)
    if dept_id:
        query = query.filter(SysRegionAllocation.target_dept_id == dept_id)
    if province:
        # 简单模糊搜索任意省份字段
        query = query.filter(
            (SysRegionAllocation.tiantao_province.like(f"%{province}%")) |
            (SysRegionAllocation.douyin_province.like(f"%{province}%"))
        )
        
    items = query.order_by(SysRegionAllocation.create_time.desc()).all()
    
    # 填充名称
    result = []
    for item in items:
        res = AllocationResponse.from_orm(item)
        if item.target_dept_id:
            dept = db.query(SysDept).filter(SysDept.id == item.target_dept_id).first()
            if dept: res.dept_name = dept.dept_name
        if item.target_leader_id:
            user = db.query(SysUser).filter(SysUser.id == item.target_leader_id).first()
            if user: res.leader_name = user.username
        result.append(res)
    return result

@router.post("/", response_model=AllocationResponse)
def create_allocation(item: AllocationCreate, db: Session = Depends(get_db)):
    # 简单的重复校验逻辑可在此添加
    db_item = SysRegionAllocation(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{id}", response_model=AllocationResponse)
def update_allocation(id: int, item: AllocationUpdate, db: Session = Depends(get_db)):
    db_item = db.query(SysRegionAllocation).filter(SysRegionAllocation.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
        
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{id}")
def delete_allocation(id: int, db: Session = Depends(get_db)):
    db_item = db.query(SysRegionAllocation).filter(SysRegionAllocation.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(db_item)
    db.commit()
    return {"msg": "删除成功"}