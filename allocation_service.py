from sqlalchemy.orm import Session
from app.models import SysRegionAllocation
from typing import Tuple, Optional

class AllocationService:
    def __init__(self, db: Session):
        self.db = db

    def auto_allocate(self, address: str) -> Tuple[Optional[int], Optional[int]]:
        """
        根据地址自动匹配分配规则
        :param address: 客户地址
        :return: (dept_id, owner_id)
        """
        if not address:
            return None, None
            
        # 获取所有启用的分配规则 (按创建时间倒序，优先匹配最新的规则)
        rules = self.db.query(SysRegionAllocation).order_by(SysRegionAllocation.create_time.desc()).all()
        
        for rule in rules:
            # 1. 匹配天淘系地址 (省+市)
            if rule.tiantao_province and rule.tiantao_province in address:
                # 如果规则定义了市，则必须同时匹配市
                if rule.tiantao_city:
                    if rule.tiantao_city in address:
                        return rule.target_dept_id, rule.target_leader_id
                else:
                    # 如果规则只定义了省，则匹配省即可
                    return rule.target_dept_id, rule.target_leader_id
            
            # 2. 匹配抖音系地址 (省+市 或 组合字段)
            if rule.douyin_province and rule.douyin_province in address:
                if rule.douyin_city:
                    if rule.douyin_city in address:
                        return rule.target_dept_id, rule.target_leader_id
                else:
                    return rule.target_dept_id, rule.target_leader_id
            
            # 3. 匹配抖音聚合字段 (如 "广东省广州市")
            if rule.douyin_province_city and rule.douyin_province_city in address:
                return rule.target_dept_id, rule.target_leader_id

        # 如果没有匹配到任何规则，返回空
        return None, None