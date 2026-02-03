# 这是一个逻辑示意，展示如何处理你最关心的两个难点

def process_customer_import(import_data_list, db_session, current_user):
    """
    import_data_list: Excel解析后的字典列表
    """
    results = {"success": 0, "failed": 0, "skipped": 0, "errors": []}

    # 1. 获取所有分配规则 (缓存到内存以提高速度)
    allocation_rules = db_session.query(RegionAllocation).all()

    for row in import_data_list:
        phone = row.get('phone')
        address = row.get('address', '')
        
        # --- A. 撞单机制 (Collision Mechanism) ---
        # 检查手机号是否存在
        existing_customer = db_session.query(Customer).filter_by(phone=phone).first()
        
        if existing_customer:
            # 如果已成交，或者正在被其他人跟进 (这里可以定义更复杂的逻辑)
            # 简单逻辑：如果已存在，拒绝导入，或者只更新非关键字段
            results['skipped'] += 1
            results['errors'].append(f"手机号 {phone} 已存在，跳过导入。")
            continue 

        # --- B. 地址模糊匹配逻辑 (Fuzzy Matching) ---
        # 需求：导入"广西省"，规则库是"广西壮族自治区"，使用包含原则
        matched_rule = None
        for rule in allocation_rules:
            # 逻辑：检查 规则库的字段 是否 包含 导入的地址关键字
            # 或者：检查 导入的地址 是否 包含 规则库的关键字段 (通常规则库会存具体的省市)
            
            # 假设规则库存储的是标准全称 "广西壮族自治区"
            # 导入的是 "广西"
            # 匹配逻辑：if Import_String in Rule_String
            
            # 更加健壮的逻辑：双向包含检测
            db_prov = rule.tiantao_province or ""
            import_prov = row.get('province', '') 
            
            if (import_prov and db_prov) and (import_prov in db_prov or db_prov in import_prov):
                matched_rule = rule
                break
        
        # --- C. 数据组装与入库 ---
        new_customer = Customer(
            phone=phone,
            customer_name=row.get('name'),
            source="Excel导入",
            # 如果匹配到规则，自动分配门店和店长
            dept_id=matched_rule.target_dept_id if matched_rule else None,
            owner_id=matched_rule.target_leader_id if matched_rule else None, 
            # 如果没匹配到，进入公海或保留为空等待手动分配
        )
        db_session.add(new_customer)
        results['success'] += 1
    
    db_session.commit()
    return results