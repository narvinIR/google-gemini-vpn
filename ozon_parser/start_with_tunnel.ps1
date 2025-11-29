# Ozon Parser API + Cloudflare Quick Tunnel
# Запускает FastAPI сервер и создаёт публичный URL без настройки домена

$ErrorActionPreference = "Stop"
$host.UI.RawUI.WindowTitle = "Ozon Parser API"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  OZON PARSER API + CLOUDFLARE TUNNEL" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Переходим в директорию скрипта
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Проверяем Python
Write-Host "[1/4] Проверка Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python не найден!" -ForegroundColor Red
    Read-Host "Нажми Enter для выхода"
    exit 1
}
Write-Host "  OK: Python найден" -ForegroundColor Green

# Проверяем cloudflared
Write-Host "[2/4] Проверка cloudflared..." -ForegroundColor Yellow
$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    Write-Host "[INSTALL] Устанавливаю cloudflared..." -ForegroundColor Yellow
    winget install Cloudflare.cloudflared
    $cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
    if (-not $cloudflared) {
        Write-Host "[ERROR] Не удалось установить cloudflared!" -ForegroundColor Red
        Read-Host "Нажми Enter для выхода"
        exit 1
    }
}
Write-Host "  OK: cloudflared найден" -ForegroundColor Green

# Устанавливаем зависимости Python
Write-Host "[3/4] Проверка зависимостей Python..." -ForegroundColor Yellow
pip show fastapi 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Устанавливаю FastAPI и uvicorn..." -ForegroundColor Yellow
    pip install fastapi uvicorn
}
Write-Host "  OK: Зависимости установлены" -ForegroundColor Green

# Запускаем сервер и туннель
Write-Host "[4/4] Запуск сервера и туннеля..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Запускаю два процесса:" -ForegroundColor White
Write-Host "  1. FastAPI сервер на порту 8080" -ForegroundColor White
Write-Host "  2. Cloudflare Quick Tunnel" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Запускаем FastAPI в фоне
$apiJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python -m uvicorn api_server:app --host 0.0.0.0 --port 8080
} -ArgumentList $scriptPath

Write-Host "[API] FastAPI сервер запущен (Job ID: $($apiJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 3

# Запускаем cloudflared tunnel
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  CLOUDFLARE TUNNEL ЗАПУСКАЕТСЯ..." -ForegroundColor Green
Write-Host "  Скопируй URL который появится ниже!" -ForegroundColor Yellow
Write-Host "  (будет что-то типа https://xxx.trycloudflare.com)" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

try {
    cloudflared tunnel --url http://localhost:8080
}
finally {
    # Останавливаем API сервер при выходе
    Write-Host ""
    Write-Host "[STOP] Останавливаю API сервер..." -ForegroundColor Yellow
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -ErrorAction SilentlyContinue
    Write-Host "[OK] Сервер остановлен" -ForegroundColor Green
}
