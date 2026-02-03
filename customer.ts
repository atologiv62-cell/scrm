import request from '@/utils/request'

// 获取客户列表
export const getCustomerList = (params?: any) => {
  return request({ 
    url: '/customers/', 
    method: 'get', 
    params 
  })
}

// 获取客户详情
// 注意：目前复用列表接口或预留，如果后端支持 ID 过滤则生效
export const getCustomerDetail = (id: number) => {
  return request({ 
    url: '/customers/', 
    method: 'get', 
    params: { id } 
  })
}

// 新增客户
export const createCustomer = (data: any) => {
  return request({ 
    url: '/customers/', 
    method: 'post', 
    data 
  })
}

// 修改客户
export const updateCustomer = (id: number, data: any) => {
  return request({ 
    url: `/customers/${id}`, 
    method: 'put', 
    data 
  })
}

// 获取操作日志
export const getCustomerLogs = (id: number) => {
  return request({ 
    url: `/customers/${id}/logs`, 
    method: 'get' 
  })
}

// --- 跟进记录相关 ---

// 获取跟进记录列表
export const getCustomerFollows = (id: number) => {
  return request({ 
    url: `/customers/${id}/follows`, 
    method: 'get' 
  })
}

// 创建新的跟进记录
export const createCustomerFollow = (id: number, data: any) => {
  return request({ 
    url: `/customers/${id}/follows`, 
    method: 'post', 
    data 
  })
}

// --- AI 功能 ---

// AI 调用 (走后端代理 /api/ai/generate)
export const callAI = (prompt: string) => {
  return request({ 
    url: '/ai/generate', 
    method: 'post', 
    data: { prompt } 
  })
}

// --- 批量操作 ---

// 批量转移跟进人
export const transferCustomers = (data: { customer_ids: number[], new_owner_id: number, new_dept_id?: number }) => {
  return request({
    url: '/customers/transfer',
    method: 'post',
    data
  })
}

// 导入客户
export const importCustomers = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/customers/import',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}