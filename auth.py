from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SysUser
from app.schemas import LoginData, Token
from app.core.security import verify_password, create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: LoginData, db: Session = Depends(get_db)):
    # 1. 查询用户
    user = db.query(SysUser).filter(SysUser.username == form_data.username).first()
    
    # 2. 校验账号是否存在及密码是否正确
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 校验状态
    if user.status != 1:
        raise HTTPException(status_code=400, detail="该账号已被禁用")

    # 4. 生成 Token
    access_token_expires = timedelta(minutes=60 * 24) # 1天过期
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}