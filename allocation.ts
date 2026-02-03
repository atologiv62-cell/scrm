import request from '@/utils/request'

// 获取分配规则列表
export const getAllocationList = (params?: any) => {
  return request({
    url: '/allocations/',
    method: 'get',
    params
  })
}

// 创建分配规则
export const createAllocation = (data: any) => {
  return request({
    url: '/allocations/',
    method: 'post',
    data
  })
}

// 更新分配规则 (单条)
export const updateAllocation = (id: number, data: any) => {
  return request({
    url: `/allocations/${id}`,
    method: 'put',
    data
  })
}

// 批量更新分配规则
export const batchUpdateAllocation = (data: { ids: number[], target_dept_id?: number | null, target_leader_id?: number | null }) => {
  return request({
    url: '/allocations/batch/update',
    method: 'put',
    data
  })
}

// 删除分配规则
export const deleteAllocation = (id: number) => {
  return request({
    url: `/allocations/${id}`,
    method: 'delete'
  })
}

// 导入分配规则
export const importAllocations = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/allocations/import',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}