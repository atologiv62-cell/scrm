import request from '@/utils/request'

/**
 * AI 内容生成请求体
 * @param prompt 用户的输入提示词
 */
interface AIRequest {
  prompt: string
}

/**
 * 调用后端 AI 接口生成内容 (例如客户画像分析、话术生成等)
 * @param data 包含 prompt 的请求体
 * @returns 包含生成结果的 Promise
 */
export const generateAI = (data: AIRequest) => request({ 
  url: '/ai/generate', 
  method: 'post', 
  data 
})