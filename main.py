from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS & Analysis Service", description="Text-to-Speech and Analysis API using Alibaba Cloud DashScope")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许OPTIONS方法
    allow_headers=["*"],  # 允许所有头部
)

# # API配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
FRONTEND_API_KEY = os.getenv("FRONTEND_API_KEY")
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
DASHSCOPE_CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# 验证环境变量
if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY not found in environment variables")
if not FRONTEND_API_KEY:
    raise ValueError("FRONTEND_API_KEY not found in environment variables")

class TTSRequest(BaseModel):
    text: str
    voice: str = "Cherry"
    language_type: str = "Chinese"

class ChatRequest(BaseModel):
    user_text: str

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    authorization: str = Header(..., description="前端API密钥，格式: Bearer your_key")
):
    """
    文本转语音API

    Args:
        request: 包含text、voice和language_type的请求体
        authorization: 请求头中的密钥，格式为Bearer your_key

    Returns:
        直接返回阿里云TTS API的响应
    """
    # 验证前端密钥
    if authorization != f"Bearer {FRONTEND_API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 准备发送到阿里云的数据
    payload = {
        "model": "qwen3-tts-flash",
        "input": {
            "text": request.text,
            "voice": request.voice,
            "language_type": request.language_type
        }
    }

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(DASHSCOPE_URL, json=payload, headers=headers)
            response.raise_for_status()

            # 直接返回阿里云的响应
            return JSONResponse(content=response.json(), status_code=response.status_code)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from DashScope: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TTS service error: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=500, detail=f"Request to TTS service failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/ttt")
async def text_to_analysis(
    request: ChatRequest,
    authorization: str = Header(..., description="前端API密钥，格式: Bearer your_key")
):
    """
    文本分析API，用于分析数学题并给出总结

    Args:
        request: 包含user_text的请求体
        authorization: 请求头中的密钥，格式为Bearer your_key

    Returns:
        返回阿里云Chat API的响应
    """
    # 验证前端密钥
    if authorization != f"Bearer {FRONTEND_API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 系统提示词，用于分析数学题
    system_prompt = "你是一个专业的数学老师，擅长分析初中数学题的去括号运算。请根据学生做的5道题，分析答题的正确率、错误类型，并给出50字左右的总结评价。"

    # 准备发送到阿里云的数据
    payload = {
        "model": "qwen-flash",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": request.user_text
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(DASHSCOPE_CHAT_URL, json=payload, headers=headers)
            response.raise_for_status()

            # 直接返回阿里云的响应
            return JSONResponse(content=response.json(), status_code=response.status_code)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from DashScope: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Chat service error: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=500, detail=f"Request to chat service failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "TTS Service is running", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host="0.0.0.0", port=8890, reload=True)
    uvicorn.run(app, host="0.0.0.0", port=8890)

