from fastapi import APIRouter, HTTPException
from app.schemas import AIRequest
import json
import requests

router = APIRouter()

# --- 硅基流动 DeepSeek 配置 ---
# ⚠️ 核心问题：401 错误意味着这个 Key 必须更换！
# 请登录 https://cloud.siliconflow.cn/ 注册并创建一个新的 API Key
# 替换下方双引号中的内容
SILICONFLOW_API_KEY = "sk-mfsovpqqaenrxqnqvbvgvhprblfvzqamiwjnfknonxtrftqf"

# 使用更稳定的模型名称 (V2.5 也是免费/低价且稳定的)
SILICONFLOW_MODEL = "deepseek-ai/DeepSeek-V2.5" 
SILICONFLOW_URL = "https://api.siliconflow.cn/v1/chat/completions"

@router.post("/generate")
def generate_ai_content(req: AIRequest):
    # 基础检查
    if not SILICONFLOW_API_KEY or "YOUR_KEY" in SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="AI Key 未配置，请在 backend/app/api/ai.py 中填入有效的 Key")
        
    try:
        # 构造请求体
        payload = {
            "model": SILICONFLOW_MODEL, 
            "messages": [
                {"role": "system", "content": "你是一个专业的家居行业金牌销售助手，擅长客户心理分析和话术生成。请直接输出话术内容，不要包含Markdown格式。"},
                {"role": "user", "content": req.prompt}
            ],
            "stream": False,
            "max_tokens": 512,
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 发送请求 (设置 30秒 超时)
        response = requests.post(SILICONFLOW_URL, headers=headers, json=payload, timeout=30)
        
        # 详细的错误诊断
        if response.status_code != 200:
            error_body = response.text
            print(f"AI API Error: {response.status_code} - {error_body}")
            
            if response.status_code == 401:
                raise Exception("API Key 无效或已过期 (401)。请检查 backend/app/api/ai.py 中的 Key 是否正确。")
            elif response.status_code == 402:
                raise Exception("API Key 余额不足 (402)。请充值或更换 Key。")
            elif response.status_code == 429:
                raise Exception("请求过于频繁 (429)。请稍后再试。")
            else:
                raise Exception(f"服务商返回错误 ({response.status_code})")

        result = response.json()
        
        if 'choices' not in result or len(result['choices']) == 0:
            raise Exception("服务商返回了空结果")
            
        content = result['choices'][0]['message']['content']
        return {"result": content}
            
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI 服务连接超时，请检查服务器网络")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="无法连接到 AI 服务商，请检查 DNS 或防火墙")
    except Exception as e:
        print(f"AI 模块异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))