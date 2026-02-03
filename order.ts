import request from '@/utils/request'

export const getOrderList = (customerId: number) => {
  return request({
    url: '/orders/',
    method: 'get',
    params: { customer_id: customerId }
  })
}

export const createOrder = (data: any) => {
  return request({
    url: '/orders/',
    method: 'post',
    data
  })
}

export const deleteOrder = (id: number) => {
  return request({
    url: `/orders/${id}`,
    method: 'delete'
  })
}