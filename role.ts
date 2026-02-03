import request from '@/utils/request'

// 获取角色列表
export const getRoleList = (params?: any) => {
  return request({
    url: '/roles/',
    method: 'get',
    params
  })
}

// 创建角色
export const createRole = (data: any) => {
  return request({
    url: '/roles/',
    method: 'post',
    data
  })
}

// 更新角色信息
export const updateRole = (id: number, data: any) => {
  return request({
    url: `/roles/${id}`,
    method: 'put',
    data
  })
}

// 删除角色
export const deleteRole = (id: number) => {
  return request({
    url: `/roles/${id}`,
    method: 'delete'
  })
}

// 更新角色状态 (启用/禁用)
export const updateRoleStatus = (id: number, status: number) => {
  return request({
    url: `/roles/${id}/status`,
    method: 'put',
    params: { status }
  })
}