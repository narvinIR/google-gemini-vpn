@echo off
chcp 65001 >nul
title Ozon Parser + Cloudflare Tunnel

echo.
echo ================================================
echo   OZON PARSER API + CLOUDFLARE TUNNEL
echo ================================================
echo.
echo   Этот скрипт:
echo   1. Запустит FastAPI сервер (порт 8080)
echo   2. Создаст публичный URL через Cloudflare
echo.
echo   URL будет типа: https://xxx.trycloudflare.com
echo   Его можно использовать из Unify!
echo.
echo ================================================
echo.

cd /d "%~dp0"

REM Запускаем PowerShell скрипт
powershell -ExecutionPolicy Bypass -File "start_with_tunnel.ps1"

pause
