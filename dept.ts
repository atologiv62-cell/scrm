import request from '@/utils/request'

// 获取门店列表
export const getDeptList = (params?: any) => {
  return request({
    url: '/depts/',
    method: 'get',
    params
  })
}

// 新增门店
export const createDept = (data: any) => {
  return request({
    url: '/depts/',
    method: 'post',
    data
  })
}

// 修改门店信息
export const updateDept = (id: number, data: any) => {
  return request({
    url: `/depts/${id}`,
    method: 'put',
    data
  })
}

// 删除门店
export const deleteDept = (id: number) => {
  return request({
    url: `/depts/${id}`,
    method: 'delete'
  })
}

// 更新门店状态 (启用/禁用)
export const updateDeptStatus = (id: number, status: number) => {
  return request({
    url: `/depts/${id}/status`,
    method: 'put',
    params: { status }
  })
}

// 导入门店数据
export const importDepts = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/depts/import',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}