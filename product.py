from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CrmProduct
from app.schemas import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def get_products(name: str = None, db: Session = Depends(get_db)):
    query = db.query(CrmProduct)
    if name:
        query = query.filter(CrmProduct.product_name.like(f"%{name}%"))
    return query.order_by(CrmProduct.create_time.desc()).all()

@router.post("/", response_model=ProductResponse)
def create_product(item: ProductCreate, db: Session = Depends(get_db)):
    if item.product_code:
        exists = db.query(CrmProduct).filter(CrmProduct.product_code == item.product_code).first()
        if exists:
            raise HTTPException(status_code=400, detail="商品编码已存在")
            
    db_item = CrmProduct(
        product_name=item.product_name,
        product_code=item.product_code,
        status=item.status
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{id}", response_model=ProductResponse)
def update_product(id: int, item: ProductUpdate, db: Session = Depends(get_db)):
    db_item = db.query(CrmProduct).filter(CrmProduct.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    db_item.product_name = item.product_name
    db_item.product_code = item.product_code
    db_item.status = item.status
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_item = db.query(CrmProduct).filter(CrmProduct.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(db_item)
    db.commit()
    return {"msg": "删除成功"}

@router.put("/{id}/status")
def toggle_status(id: int, status: int, db: Session = Depends(get_db)):
    db_item = db.query(CrmProduct).filter(CrmProduct.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="商品不存在")
    db_item.status = status
    db.commit()
    return {"msg": "状态更新成功"}