from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models import CrmCustomer, CrmFollowRecord, SysOperationLog, SysUser
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# --- 1. 客资来源转化统计 ---
@router.get("/source_stats")
def get_source_stats(db: Session = Depends(get_db)):
    # 聚合查询：按 source 分组，统计总数和成交数
    stats = db.query(
        CrmCustomer.source,
        func.count(CrmCustomer.id).label('total'),
        func.sum(case((CrmCustomer.is_deal == 1, 1), else_=0)).label('deal_count')
    ).group_by(CrmCustomer.source).all()
    
    result = []
    for s in stats:
        total = s.total or 0
        deal = s.deal_count or 0
        rate = 0
        if total > 0:
            rate = round((deal / total * 100), 2)
            
        result.append({
            "name": s.source or "未知来源",
            "total": total,
            "deal_count": deal,
            "rate": rate
        })
    return result

# --- 2. 客资跟进效率明细 (最近 50 条) ---
@router.get("/efficiency")
def get_follow_efficiency(db: Session = Depends(get_db)):
    # 查询最近的 50 个客户
    customers = db.query(CrmCustomer).order_by(CrmCustomer.create_time.desc()).limit(50).all()
    
    result = []
    for c in customers:
        # 1. 进线时间 (创建时间)
        t1 = c.create_time
        
        # 2. 分配时间 (查询日志中最后一次“转移客户”的操作时间)
        log = db.query(SysOperationLog).filter(
            SysOperationLog.ref_id == c.id,
            SysOperationLog.action_type == '转移客户'
        ).order_by(SysOperationLog.create_time.desc()).first()
        
        # 优化逻辑：如果有转移记录，用转移时间；如果没有(说明是自动分配或直接录入)，用创建时间作为分配时间
        t2 = log.create_time if log else t1
        
        # 3. 首次跟进 (查询跟进记录表中最早的一条)
        first_follow = db.query(CrmFollowRecord).filter(
            CrmFollowRecord.customer_id == c.id
        ).order_by(CrmFollowRecord.create_time.asc()).first()
        t3 = first_follow.create_time if first_follow else None
        
        # 4. 成交时间
        t4 = c.deal_time
        
        # 计算响应时效 (首次跟进 - 分配时间)
        response_hours = 0
        if t3 and t2:
            diff = t3 - t2
            # 如果是负数(可能是数据误差)，归零
            seconds = max(0, diff.total_seconds())
            response_hours = round(seconds / 3600, 1)

        owner_name = "未知"
        if c.owner_id:
            u = db.query(SysUser).filter(SysUser.id == c.owner_id).first()
            if u: owner_name = u.username

        result.append({
            "customer_name": c.customer_name,
            "owner_name": owner_name,
            "time_enter": t1,          # 进线
            "time_assign": t2,         # 分配 (优化后)
            "time_first_follow": t3,   # 跟进
            "time_deal": t4,           # 成交
            "response_hours": response_hours
        })
        
    return result

# --- 3. 首页顶部汇总数据 ---
@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total_customer = db.query(CrmCustomer).count()
    total_deal = db.query(CrmCustomer).filter(CrmCustomer.is_deal == 1).count()
    # 注意：这里依赖服务器时区，Docker 默认为 UTC。如果发现“今日新增”不准，需调整容器时区。
    today_new = db.query(CrmCustomer).filter(func.date(CrmCustomer.create_time) == datetime.now().date()).count()
    
    rate = 0
    if total_customer > 0:
        rate = round((total_deal / total_customer * 100), 2)
    
    return {
        "total_customer": total_customer,
        "total_deal": total_deal,
        "today_new": today_new,
        "conversion_rate": rate
    }