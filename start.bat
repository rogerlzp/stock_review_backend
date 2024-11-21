@echo off
:: 激活虚拟环境
call venv\Scripts\activate

:: 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000 