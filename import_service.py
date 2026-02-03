import pandas as pd
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import CrmCustomer, SysRegionAllocation, SysDept, CrmProduct, SysUser, SysRole
from app.core.security import get_password_hash
from app.services.allocation_service import AllocationService
from datetime import datetime

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def _read_excel(self, file_contents: bytes) -> pd.DataFrame:
        try:
            df = pd.read_excel(file_contents)
            df = df.dropna(how='all') 
            # 统一转为字符串并去除空格
            df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else None)
            return df
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Excel 解析失败: {str(e)}")

    # --- 1. 客户导入 ---
    def process_customer_import(self, file_contents: bytes, current_user_id: int, current_dept_id: int):
        df = self._read_excel(file_contents)
        column_map = {
            '客户名称': 'customer_name', '姓名': 'customer_name',
            '手机号': 'phone', '电话': 'phone',
            '地址': 'address', '详细地址': 'address',
            '来源': 'source', '微信号': 'wechat',
        }
        df.rename(columns=column_map, inplace=True)
        
        results = {"total": len(df), "success": 0, "failed": 0, "skipped": 0, "errors": []}
        alloc_service = AllocationService(self.db) # 引入自动分配服务
        
        for index, row in df.iterrows():
            try:
                phone = row.get('phone')
                if not phone: continue
                
                if self.db.query(CrmCustomer).filter(CrmCustomer.phone == phone).first():
                    results['skipped'] += 1
                    continue

                address = row.get('address') or ''
                
                # 自动分配
                target_dept_id, target_owner_id = alloc_service.auto_allocate(address)
                
                # 未匹配则归属导入人
                if not target_dept_id:
                    target_dept_id = current_dept_id
                    target_owner_id = current_user_id
                
                customer = CrmCustomer(
                    customer_name=row.get('customer_name', '未知'),
                    phone=phone,
                    source=row.get('source', 'Excel导入'),
                    address=address,
                    wechat=row.get('wechat'),
                    dept_id=target_dept_id,
                    owner_id=target_owner_id,
                    follow_status="待分配",
                    follow_count=0 
                )
                self.db.add(customer)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"第{index+2}行: {str(e)}")
        
        self.db.commit()
        return results

    # --- 2. 门店导入 ---
    def process_dept_import(self, file_contents: bytes):
        df = self._read_excel(file_contents)
        column_map = {'门店名称': 'dept_name', '店长': 'leader_name'}
        df.rename(columns=column_map, inplace=True)
        results = {"total": len(df), "success": 0, "failed": 0, "errors": []}
        prefix = datetime.now().strftime('%Y%m%d')
        
        for index, row in df.iterrows():
            try:
                dept_name = row.get('dept_name')
                if not dept_name: continue
                if self.db.query(SysDept).filter(SysDept.dept_name == dept_name).first(): continue
                
                leader_id = None
                leader_name = row.get('leader_name')
                if leader_name:
                    user = self.db.query(SysUser).filter(SysUser.username == leader_name).first()
                    if user: leader_id = user.id
                
                count = self.db.query(SysDept).filter(SysDept.dept_code.like(f"{prefix}%")).count()
                code = f"{prefix}{count + 1 + index:04d}"
                dept = SysDept(dept_code=code, dept_name=dept_name, leader_id=leader_id, status=1)
                self.db.add(dept)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"第{index+2}行: {str(e)}")
        self.db.commit()
        return results

    # --- 3. 商品导入 ---
    def process_product_import(self, file_contents: bytes):
        df = self._read_excel(file_contents)
        column_map = {'商品名称': 'product_name', '商品编码': 'product_code'}
        df.rename(columns=column_map, inplace=True)
        results = {"total": len(df), "success": 0, "failed": 0, "errors": []}
        
        for index, row in df.iterrows():
            try:
                name = row.get('product_name')
                code = row.get('product_code')
                if not name: continue
                if code and self.db.query(CrmProduct).filter(CrmProduct.product_code == code).first(): continue
                prod = CrmProduct(product_name=name, product_code=code, status=1)
                self.db.add(prod)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"第{index+2}行: {str(e)}")
        self.db.commit()
        return results

    # --- 4. 用户导入 ---
    def process_user_import(self, file_contents: bytes):
        df = self._read_excel(file_contents)
        column_map = {'用户名称': 'username', '手机号': 'phone', '密码': 'password', '门店': 'dept_name', '角色': 'role_name', '岗位': 'post'}
        df.rename(columns=column_map, inplace=True)
        results = {"total": len(df), "success": 0, "failed": 0, "errors": []}
        
        for index, row in df.iterrows():
            try:
                username = row.get('username')
                if not username: continue
                if self.db.query(SysUser).filter(SysUser.username == username).first(): continue
                
                dept_id = None
                if row.get('dept_name'):
                    dept = self.db.query(SysDept).filter(SysDept.dept_name == row.get('dept_name')).first()
                    if dept: dept_id = dept.id
                role_id = None
                if row.get('role_name'):
                    role = self.db.query(SysRole).filter(SysRole.role_name == row.get('role_name')).first()
                    if role: role_id = role.id
                
                pwd = str(row.get('password') or '123456')
                user = SysUser(username=username, password=get_password_hash(pwd), phone=row.get('phone'), dept_id=dept_id, role_id=role_id, post=row.get('post'), status=1)
                self.db.add(user)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"第{index+2}行: {str(e)}")
        self.db.commit()
        return results

    # --- 5. 分配规则导入 (核心更新) ---
    def process_allocation_import(self, file_contents: bytes):
        df = self._read_excel(file_contents)
        # 映射需求文档中的列名
        column_map = {
            '天淘省': 'tiantao_province', 
            '天淘市': 'tiantao_city',
            '抖音省': 'douyin_province', 
            '抖音市': 'douyin_city',
            '抖音省+市': 'douyin_province_city', # 支持组合字段
            '门店': 'dept_name', 
            '门店名称': 'dept_name',
            '店长': 'leader_name',
            '店长名称': 'leader_name'
        }
        df.rename(columns=column_map, inplace=True)
        results = {"total": len(df), "success": 0, "failed": 0, "errors": []}
        
        for index, row in df.iterrows():
            try:
                # 必须匹配到门店
                target_dept_id = None
                target_leader_id = None
                
                dept_name = row.get('dept_name')
                if dept_name:
                    dept = self.db.query(SysDept).filter(SysDept.dept_name == dept_name).first()
                    if dept: target_dept_id = dept.id
                
                if not target_dept_id:
                    raise Exception(f"找不到门店: {dept_name}")
                
                leader_name = row.get('leader_name')
                if leader_name:
                    user = self.db.query(SysUser).filter(SysUser.username == leader_name).first()
                    if user: target_leader_id = user.id
                
                rule = SysRegionAllocation(
                    tiantao_province=row.get('tiantao_province'),
                    tiantao_city=row.get('tiantao_city'),
                    douyin_province=row.get('douyin_province'),
                    douyin_city=row.get('douyin_city'),
                    douyin_province_city=row.get('douyin_province_city'),
                    target_dept_id=target_dept_id,
                    target_leader_id=target_leader_id
                )
                self.db.add(rule)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"第{index+2}行: {str(e)}")
        self.db.commit()
        return results