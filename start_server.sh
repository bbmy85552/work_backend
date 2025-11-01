#!/bin/bash

# 创建虚拟环境
echo "Creating virtual environment..."
uv venv

# 激活虚拟环境
echo "Activating virtual environment..."
source .venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
uv pip install -e .

# 启动服务器
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload