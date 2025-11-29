@echo off
chcp 65001 >nul
title [2] Cloudflare Tunnel

echo ================================================
echo   [2] CLOUDFLARE QUICK TUNNEL
echo ================================================
echo.
echo   Создаёт публичный URL для API сервера
echo   URL будет типа: https://xxx.trycloudflare.com
echo.
echo   ВАЖНО: Сначала запусти 1_START_API.bat !
echo.
echo ================================================
echo.

REM Проверяем cloudflared
where cloudflared >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] cloudflared не найден!
    echo.
    echo Установи его командой:
    echo   winget install Cloudflare.cloudflared
    echo.
    pause
    exit /b 1
)

echo [START] Создаю туннель к localhost:8080...
echo.
echo ================================================
echo   СКОПИРУЙ URL КОТОРЫЙ ПОЯВИТСЯ НИЖЕ!
echo   (что-то типа https://xxx.trycloudflare.com)
echo ================================================
echo.

cloudflared tunnel --url http://localhost:8080

pause
