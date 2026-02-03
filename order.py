from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CrmOrder, CrmProduct, SysUser, CrmCustomer
from app.schemas import OrderCreate, OrderUpdate, OrderResponse

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
def get_orders(customer_id: int, db: Session = Depends(get_db)):
    # 订单通常是依附于客户的，所以必传 customer_id
    query = db.query(CrmOrder).filter(CrmOrder.customer_id == customer_id)
    orders = query.order_by(CrmOrder.create_time.desc()).all()
    
    result = []
    for o in orders:
        res = OrderResponse.from_orm(o)
        # 填充商品名
        if o.product_id:
            p = db.query(CrmProduct).filter(CrmProduct.id == o.product_id).first()
            if p: res.product_name = p.product_name
        # 填充做单人
        if o.maker_id:
            u = db.query(SysUser).filter(SysUser.id == o.maker_id).first()
            if u: res.maker_name = u.username
        result.append(res)
    return result

@router.post("/", response_model=OrderResponse)
def create_order(item: OrderCreate, db: Session = Depends(get_db)):
    # 校验客户是否存在
    cust = db.query(CrmCustomer).filter(CrmCustomer.id == item.customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="关联客户不存在")
        
    db_order = CrmOrder(**item.dict())
    db.add(db_order)
    
    # 自动更新客户状态为“已成交”
    cust.is_deal = 1
    cust.follow_status = "已成交"
    cust.deal_time = db_order.create_time
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
    order = db.query(CrmOrder).filter(CrmOrder.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    db.delete(order)
    db.commit()
    return {"msg": "删除成功"}