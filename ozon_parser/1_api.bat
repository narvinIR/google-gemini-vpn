@echo off
chcp 65001 >nul
cd /d "C:\ozon_parser"
pip install fastapi uvicorn --quiet
python -m uvicorn api_server:app --host 0.0.0.0 --port 8080
pause
