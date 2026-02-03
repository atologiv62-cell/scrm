/**
 * 系统权限树定义
 * id: 权限标识符 (存入数据库)
 * label: 显示名称
 * children: 子权限
 */
export const PERMISSION_TREE = [
  {
    id: 'system',
    label: '系统管理',
    children: [
      {
        id: 'dept',
        label: '门店管理',
        children: [
          { id: 'dept:list', label: '查看列表' },
          { id: 'dept:add', label: '新增门店' },
          { id: 'dept:edit', label: '修改门店' },
          { id: 'dept:delete', label: '删除门店' },
          { id: 'dept:status', label: '启用/禁用' }
        ]
      },
      {
        id: 'role',
        label: '角色管理',
        children: [
          { id: 'role:list', label: '查看列表' },
          { id: 'role:add', label: '新增角色' },
          { id: 'role:edit', label: '修改角色' },
          { id: 'role:delete', label: '删除角色' }
        ]
      },
      {
        id: 'user',
        label: '用户管理',
        children: [
          { id: 'user:list', label: '查看列表' },
          { id: 'user:add', label: '新增用户' },
          { id: 'user:edit', label: '修改用户' },
          { id: 'user:delete', label: '删除用户' },
          { id: 'user:status', label: '启用/禁用' }
        ]
      }
    ]
  },
  {
    id: 'product',
    label: '商品资料',
    children: [
      { id: 'product:list', label: '查看列表' },
      { id: 'product:add', label: '新增商品' },
      { id: 'product:edit', label: '修改商品' },
      { id: 'product:delete', label: '删除商品' },
      { id: 'product:status', label: '启用/禁用' }
    ]
  },
  {
    id: 'customer',
    label: '客户管理',
    children: [
      { id: 'customer:list', label: '查看列表' },
      { id: 'customer:add', label: '新增客户' },
      { id: 'customer:edit', label: '编辑/详情' },
      { id: 'customer:transfer', label: '批量转移' },
      { id: 'customer:import', label: '导入客户' }, // 预留
      { id: 'customer:follow', label: '写跟进' },
      { id: 'customer:order', label: '录订单' }
    ]
  },
  {
    id: 'allocation',
    label: '客资分配',
    children: [
      { id: 'allocation:list', label: '查看规则' },
      { id: 'allocation:add', label: '新增规则' },
      { id: 'allocation:edit', label: '修改规则' },
      { id: 'allocation:delete', label: '删除规则' }
    ]
  }
]