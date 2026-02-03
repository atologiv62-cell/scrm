import request from '@/utils/request'

// 获取商品列表
export const getProductList = (params?: any) => {
  return request({
    url: '/products/',
    method: 'get',
    params
  })
}

// 新增商品
export const createProduct = (data: any) => {
  return request({
    url: '/products/',
    method: 'post',
    data
  })
}

// 修改商品信息
export const updateProduct = (id: number, data: any) => {
  return request({
    url: `/products/${id}`,
    method: 'put',
    data
  })
}

// 删除商品
export const deleteProduct = (id: number) => {
  return request({
    url: `/products/${id}`,
    method: 'delete'
  })
}

// 更新商品状态 (启用/禁用)
export const updateProductStatus = (id: number, status: number) => {
  return request({
    url: `/products/${id}/status`,
    method: 'put',
    params: { status }
  })
}

// 导入商品数据
export const importProducts = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/products/import',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}