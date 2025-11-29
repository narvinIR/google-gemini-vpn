@echo off
chcp 65001 >nul
title Ozon Parser API Server

echo ================================================
echo   OZON PARSER API SERVER
echo   Запуск FastAPI + Cloudflare Tunnel
echo ================================================
echo.

REM Проверяем Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python не найден!
    pause
    exit /b 1
)

REM Переходим в директорию скрипта
cd /d "%~dp0"

echo [1/3] Проверка зависимостей...
pip show fastapi >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INSTALL] Устанавливаю FastAPI и uvicorn...
    pip install fastapi uvicorn
)

echo [2/3] Запуск API сервера на порту 8080...
echo.
echo ================================================
echo   API доступен: http://localhost:8080
echo   Документация: http://localhost:8080/docs
echo ================================================
echo.
echo   Endpoints:
echo   - GET  /health         - статус
echo   - GET  /parse/{sku}    - парсинг SKU
echo   - POST /parse/batch    - batch парсинг
echo   - POST /restart        - перезапуск браузера
echo ================================================
echo.
echo   Для Cloudflare Tunnel откройте второй терминал:
echo   cloudflared tunnel run ozon-parser
echo ================================================
echo.

python -m uvicorn api_server:app --host 0.0.0.0 --port 8080 --reload

pause
