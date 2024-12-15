#!/bin/bash

# 激活虚拟环境（如果有的话）
source windsurf_venv/bin/activate

# 启动应用
uvicorn main:app --reload --host 0.0.0.0 --port 8000