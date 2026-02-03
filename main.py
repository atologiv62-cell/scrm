import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from sqlalchemy.orm import Session

# 导入内部模块
from app.database import engine, Base, get_db, SessionLocal
from app.services.import_service import ImportService
from app.core.file_storage import FileStorage
from app.core.security import get_password_hash
import app.models as models

# --- 导入所有 API 模块 ---
from app.api import auth
from app.api import dept
from app.api import role
from app.api import user
from app.api import product
from app.api import customer
from app.api import allocation
from app.api import order
from app.api import ai
from app.api import report  # ✅ 核心修复：导入报表模块

# --- 1. 初始化数据库表 ---
models.Base.metadata.create_all(bind=engine)

# --- 2. 初始化 FastAPI 应用 ---
app = FastAPI(
    title="门店SCRM系统 API",
    description="基于 Python FastAPI 的 CRM 后端服务",
    version="1.0.0",
    docs_url=None,   
    redoc_url=None   
)

# --- 3. 配置 CORS ---
origins = ["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. 注册所有路由 ---
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(dept.router, prefix="/api/depts", tags=["门店管理"])
app.include_router(role.router, prefix="/api/roles", tags=["角色管理"])
app.include_router(user.router, prefix="/api/users", tags=["用户管理"])
app.include_router(product.router, prefix="/api/products", tags=["商品资料"])
app.include_router(customer.router, prefix="/api/customers", tags=["客户列表"])
app.include_router(allocation.router, prefix="/api/allocations", tags=["客资分配"])
app.include_router(order.router, prefix="/api/orders", tags=["订单管理"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI助手"])
app.include_router(report.router, prefix="/api/report", tags=["数据报表"]) # ✅ 核心修复：注册报表路由

# --- 5. 启动事件: 创建默认管理员 ---
@app.on_event("startup")
def create_or_reset_admin():
    db = SessionLocal()
    try:
        admin = db.query(models.SysUser).filter(models.SysUser.username == "admin").first()
        hashed_pwd = get_password_hash("123456")
        
        if not admin:
            print(">>> [系统初始化] 正在创建默认管理员账号: admin / 123456")
            new_admin = models.SysUser(
                username="admin",
                password=hashed_pwd,
                phone="13800000000",
                status=1,
                role_id=1,
                dept_id=0
            )
            db.add(new_admin)
            db.commit()
        else:
            print(">>> [系统初始化] 检查管理员账号...OK")
            # 如果需要强制重置密码，可在此处开启
            # admin.password = hashed_pwd
            # admin.status = 1
            # db.commit()
            
    except Exception as e:
        print(f">>> [系统初始化] 管理员账号维护失败: {str(e)}")
    finally:
        db.close()

# --- 6. 文档与静态资源 ---
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.staticfile.org/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.org/swagger-ui/5.1.0/swagger-ui.min.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

# --- 7. 通用业务路由 ---
@app.get("/")
def read_root():
    return {"message": "SCRM System is running!", "status": "active"}

# 图片上传接口
@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    upload_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    base_url = os.getenv("IMG_BASE_URL", "") 
    storage = FileStorage(upload_dir)
    try:
        file_content = await file.read()
        new_filename = storage.save_file(file_content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    full_url = f"/uploads/{new_filename}"
    if base_url:
        full_url = f"{base_url.rstrip('/')}/{new_filename}"
        
    return {"code": 200, "message": "上传成功", "url": full_url, "filename": new_filename}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)