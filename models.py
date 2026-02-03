from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DECIMAL, JSON
from sqlalchemy.sql import func
from .database import Base

# --- 1. 系统用户表 ---
class SysUser(Base):
    __tablename__ = "sys_user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    phone = Column(String(11))
    dept_id = Column(Integer) 
    role_id = Column(Integer) 
    post = Column(String(50)) 
    status = Column(Integer, default=1) 
    create_time = Column(DateTime, default=func.now())

# --- 2. 角色表 ---
class SysRole(Base):
    __tablename__ = "sys_role"
    id = Column(Integer, primary_key=True, index=True)
    role_code = Column(String(50), unique=True) 
    role_name = Column(String(50), nullable=False) 
    permissions = Column(JSON) 
    status = Column(Integer, default=1)
    create_time = Column(DateTime, default=func.now())

# --- 3. 门店表 ---
class SysDept(Base):
    __tablename__ = "sys_dept"
    id = Column(Integer, primary_key=True, index=True)
    dept_code = Column(String(50)) 
    dept_name = Column(String(100))
    leader_id = Column(Integer)
    status = Column(Integer, default=1)
    create_time = Column(DateTime, default=func.now())

# --- 4. 客资分配规则表 ---
class SysRegionAllocation(Base):
    __tablename__ = "sys_region_allocation"
    id = Column(Integer, primary_key=True, index=True)
    tiantao_province = Column(String(50))
    tiantao_city = Column(String(50))
    douyin_province = Column(String(50))
    douyin_city = Column(String(50))
    douyin_province_city = Column(String(100))
    target_dept_id = Column(Integer, nullable=False)
    target_leader_id = Column(Integer)
    create_time = Column(DateTime, default=func.now())

# --- 5. 客户表 (包含所有扩展字段) ---
class CrmCustomer(Base):
    __tablename__ = "crm_customer"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(50))
    phone = Column(String(20), unique=True, nullable=False) 
    source = Column(String(50)) 
    address = Column(String(255)) 
    
    # 归属与状态
    dept_id = Column(Integer) 
    owner_id = Column(Integer) 
    is_deal = Column(Integer, default=0) 
    deal_time = Column(DateTime) 
    follow_status = Column(String(50)) 
    
    # 自动化统计字段
    follow_count = Column(Integer, default=0) 
    last_follow_time = Column(DateTime)       

    # 扩展信息
    wechat = Column(String(50)) 
    age = Column(Integer)
    decision_maker = Column(String(50)) 
    community = Column(String(100)) 
    house_area = Column(String(50)) 
    decoration_progress = Column(String(50)) 
    intent_product_id = Column(Integer) 
    competitor = Column(String(50)) 
    visit_date = Column(DateTime) 
    platform_id = Column(String(50)) 
    
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, onupdate=func.now())

# --- 6. 商品表 ---
class CrmProduct(Base):
    __tablename__ = "crm_product"
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True)
    product_name = Column(String(100), nullable=False)
    status = Column(Integer, default=1)
    create_time = Column(DateTime, default=func.now())

# --- 7. 操作日志表 ---
class SysOperationLog(Base):
    __tablename__ = "sys_operation_log"
    id = Column(Integer, primary_key=True, index=True)
    ref_id = Column(Integer, nullable=False) 
    ref_type = Column(String(20), default='CUSTOMER') 
    operator_name = Column(String(50)) 
    action_type = Column(String(50)) 
    content = Column(Text) 
    create_time = Column(DateTime, default=func.now())

# --- 8. 跟进记录表 ---
class CrmFollowRecord(Base):
    __tablename__ = "crm_follow_record"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    follow_detail = Column(Text)
    follow_tag = Column(String(50))
    next_follow_time = Column(DateTime)
    follower_name = Column(String(50))
    create_time = Column(DateTime, default=func.now())

# --- 9. 订单表 ---
class CrmOrder(Base):
    __tablename__ = "crm_order"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    order_no = Column(String(50), nullable=False)
    product_id = Column(Integer)
    amount = Column(DECIMAL(10, 2))
    order_image_url = Column(String(500)) 
    transaction_type = Column(String(50))
    is_cash_back = Column(Integer, default=0)
    cash_back_amount = Column(DECIMAL(10, 2))
    delivery_remark = Column(String(50))
    delivery_date = Column(DateTime)
    is_trade_in = Column(Integer, default=0)
    trade_in_no = Column(String(50))
    maker_id = Column(Integer)
    create_time = Column(DateTime, default=func.now())