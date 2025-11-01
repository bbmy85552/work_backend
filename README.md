nohup python main.py > output.log 2>&1 &

# TTS Backend Service

基于FastAPI的文本转语音后端服务，封装阿里云DashScope TTS API。

## 功能特性

- 提供RESTful API接口进行文本转语音
- 支持密钥认证保护
- 直接返回阿里云TTS API响应
- 支持中文语音合成

## 环境要求

- Python 3.8+
- uv (Python包管理器)

## 快速开始

### 1. 配置环境变量

编辑 `.env` 文件：

```env
# 阿里云TTS API密钥
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 前端访问密钥
FRONTEND_API_KEY=your_frontend_secret_key_here
```

### 2. 安装依赖并启动服务

使用提供的启动脚本：

```bash
./start_server.sh
```

或者手动执行：

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
uv pip install -e .

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档

服务启动后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API使用

### POST /tts

**请求头：**
```
Authorization: Bearer your_frontend_secret_key_here
Content-Type: application/json
```

**请求体：**
```json
{
    "text": "你好，这是一段测试文本",
    "voice": "Cherry",
    "language_type": "Chinese"
}
```

**响应：**
直接返回阿里云DashScope API的完整响应，包含音频文件的URL等信息。

**示例请求：**
```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Authorization: Bearer your_frontend_secret_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好加上运算步骤的结果等于世界",
    "voice": "Cherry",
    "language_type": "Chinese"
  }'
```

## 健康检查

### GET /health

检查服务状态：

```bash
curl http://localhost:8000/health
```

## 项目结构

```
backend/
├── .env                    # 环境变量配置
├── main.py                 # FastAPI应用主文件
├── pyproject.toml         # 项目配置和依赖
├── start_server.sh        # 启动脚本
└── README.md              # 项目文档
```

## 错误处理

- 401: API密钥无效
- 500: 服务器内部错误或TTS服务异常
- 其他: 阿里云API返回的错误

## 注意事项

1. 请妥善保管API密钥，不要提交到版本控制系统
2. 确保`.env`文件中的密钥配置正确
3. 服务默认监听8000端口，可根据需要修改