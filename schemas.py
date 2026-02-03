from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime, date

# --- 1. 认证 ---
class Token(BaseModel):
    access_token: str
    token_type: str
class LoginData(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role_name: Optional[str] = None
    permissions: List[str] = [] 

# --- 2. 角色 ---
class RoleBase(BaseModel):
    role_name: str
    permissions: Optional[List[str]] = []
    status: Optional[int] = 1
class RoleCreate(RoleBase): pass
class RoleUpdate(RoleBase): pass
class RoleResponse(RoleBase):
    id: int
    role_code: str
    create_time: datetime
    class Config: from_attributes = True

# --- 3. 用户 ---
class UserBase(BaseModel):
    username: str
    phone: Optional[str] = None
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    post: Optional[str] = None
    status: Optional[int] = 1
class UserCreate(UserBase): password: str
class UserUpdate(UserBase): password: Optional[str] = None
class UserPasswordReset(BaseModel): new_password: str
class UserResponse(UserBase):
    id: int
    create_time: datetime
    dept_name: Optional[str] = None
    role_name: Optional[str] = None
    class Config: from_attributes = True

# --- 4. 门店 ---
class DeptBase(BaseModel):
    dept_name: str
    leader_id: Optional[int] = None
    status: Optional[int] = 1
class DeptCreate(DeptBase): pass 
class DeptUpdate(DeptBase): pass
class DeptResponse(DeptBase):
    id: int
    dept_code: str
    create_time: datetime
    leader_name: Optional[str] = None 
    class Config: from_attributes = True

# --- 5. 商品 ---
class ProductBase(BaseModel):
    product_name: str
    product_code: Optional[str] = None
    status: Optional[int] = 1
class ProductCreate(ProductBase): pass
class ProductUpdate(ProductBase): pass
class ProductResponse(ProductBase):
    id: int
    create_time: datetime
    class Config: from_attributes = True

# --- 6. 客户 ---
class CustomerBase(BaseModel):
    customer_name: str
    phone: str
    source: Optional[str] = None
    address: Optional[str] = None
    dept_id: Optional[int] = None
    owner_id: Optional[int] = None
    wechat: Optional[str] = None
    age: Optional[int] = None
    decision_maker: Optional[str] = None
    community: Optional[str] = None
    house_area: Optional[str] = None
    decoration_progress: Optional[str] = None
    intent_product_id: Optional[int] = None
    competitor: Optional[str] = None
    visit_date: Optional[datetime] = None
    platform_id: Optional[str] = None

class CustomerCreate(CustomerBase): pass
class CustomerUpdate(CustomerBase):
    is_deal: Optional[int] = None
    follow_status: Optional[str] = None
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None
    age: Optional[int] = None
    decision_maker: Optional[str] = None
    community: Optional[str] = None
    house_area: Optional[str] = None
    decoration_progress: Optional[str] = None
    intent_product_id: Optional[int] = None
    competitor: Optional[str] = None
    visit_date: Optional[datetime] = None
    platform_id: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    is_deal: int
    follow_status: Optional[str] = None
    deal_time: Optional[datetime] = None
    create_time: datetime
    follow_count: int = 0
    last_follow_time: Optional[datetime] = None
    dept_name: Optional[str] = None
    owner_name: Optional[str] = None
    intent_product_name: Optional[str] = None
    class Config: from_attributes = True

class CustomerTransfer(BaseModel):
    customer_ids: List[int]
    new_owner_id: int
    new_dept_id: Optional[int] = None 

# --- 7. 客资分配 (核心完善) ---
class AllocationBase(BaseModel):
    tiantao_province: Optional[str] = None
    tiantao_city: Optional[str] = None
    douyin_province: Optional[str] = None
    douyin_city: Optional[str] = None
    douyin_province_city: Optional[str] = None
    target_dept_id: int
    target_leader_id: Optional[int] = None
class AllocationCreate(AllocationBase): pass
class AllocationUpdate(AllocationBase): pass

# 新增：批量更新结构
class AllocationBatchUpdate(BaseModel):
    ids: List[int]
    target_dept_id: Optional[int] = None
    target_leader_id: Optional[int] = None

class AllocationResponse(AllocationBase):
    id: int
    create_time: datetime
    dept_name: Optional[str] = None
    leader_name: Optional[str] = None
    class Config: from_attributes = True

# --- 8. 订单 ---
class OrderBase(BaseModel):
    customer_id: int
    product_id: int
    order_no: str
    amount: float
    order_image_url: Optional[str] = None
    transaction_type: Optional[str] = None
    is_cash_back: Optional[int] = 0
    cash_back_amount: Optional[float] = 0
    delivery_remark: Optional[str] = None
    delivery_date: Optional[date] = None
    is_trade_in: Optional[int] = 0
    trade_in_no: Optional[str] = None
    maker_id: Optional[int] = None
class OrderCreate(OrderBase): pass
class OrderUpdate(OrderBase): pass
class OrderResponse(OrderBase):
    id: int
    create_time: datetime
    product_name: Optional[str] = None
    maker_name: Optional[str] = None
    class Config: from_attributes = True

# --- 9. 跟进记录 ---
class FollowBase(BaseModel):
    customer_id: int
    follow_detail: str
    follow_tag: Optional[str] = None
    next_follow_time: Optional[date] = None
class FollowCreate(FollowBase): pass
class FollowResponse(FollowBase):
    id: int
    create_time: datetime
    follower_name: Optional[str] = None
    class Config: from_attributes = True

# --- 10. 日志 ---
class LogResponse(BaseModel):
    id: int
    operator_name: str
    action_type: str
    content: str
    create_time: datetime
    class Config: from_attributes = True

# --- 11. AI ---
class AIRequest(BaseModel):
    prompt: str

# --- 12. 通用 ---
class ResponseModel(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Optional[Union[dict, list, str, int]] = None