import request from '@/utils/request'

// 获取数据概览 (顶部卡片)
export const getSummary = () => {
  return request({
    url: '/report/summary',
    method: 'get'
  })
}

// 获取客资来源统计 (饼图/柱状图)
export const getSourceStats = () => {
  return request({
    url: '/report/source_stats',
    method: 'get'
  })
}

// 获取跟进效率报表 (生命周期表)
export const getFollowEfficiency = () => {
  return request({
    url: '/report/efficiency',
    method: 'get'
  })
}