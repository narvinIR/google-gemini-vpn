@echo off
chcp 65001 >nul
title [1] Ozon Parser API Server

echo ================================================
echo   [1] OZON PARSER API SERVER
echo ================================================
echo.
echo   Порт: 8080
echo   Документация: http://localhost:8080/docs
echo.
echo   Endpoints:
echo   - GET  /health         - статус
echo   - GET  /parse/{sku}    - парсинг SKU
echo   - POST /parse/batch    - batch парсинг
echo ================================================
echo.

cd /d "%~dp0"

REM Проверяем зависимости
pip show fastapi >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INSTALL] Устанавливаю FastAPI...
    pip install fastapi uvicorn
)

echo [START] Запуск API сервера...
echo.
python -m uvicorn api_server:app --host 0.0.0.0 --port 8080

pause
