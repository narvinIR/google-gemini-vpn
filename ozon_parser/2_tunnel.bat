@echo off
chcp 65001 >nul
cloudflared tunnel --url http://localhost:8080
pause
