@echo off
REM Antigravity Launcher - Windows version
REM Запуск с проверкой VPN

echo ==========================================
echo   Google Antigravity Launcher
echo ==========================================
echo.

REM Проверка IP
echo [1/3] Проверка IP адреса...
for /f "tokens=*" %%i in ('curl -s "https://ipapi.co/country_code/"') do set COUNTRY=%%i

if "%COUNTRY%"=="RU" (
    echo [ERROR] Регион RU заблокирован для Antigravity!
    echo Включите VPN с сервером в поддерживаемой стране
    pause
    exit /b 1
)

if "%COUNTRY%"=="CN" (
    echo [ERROR] Регион CN заблокирован для Antigravity!
    pause
    exit /b 1
)

echo [OK] Регион: %COUNTRY% - поддерживается
echo.

REM Проверка Antigravity
echo [2/3] Поиск Antigravity...

set "ANTIGRAVITY_PATH="

REM Стандартные пути
if exist "%LOCALAPPDATA%\Programs\antigravity\Antigravity.exe" (
    set "ANTIGRAVITY_PATH=%LOCALAPPDATA%\Programs\antigravity\Antigravity.exe"
)

if exist "%PROGRAMFILES%\Antigravity\Antigravity.exe" (
    set "ANTIGRAVITY_PATH=%PROGRAMFILES%\Antigravity\Antigravity.exe"
)

if exist "%USERPROFILE%\AppData\Local\Programs\antigravity\Antigravity.exe" (
    set "ANTIGRAVITY_PATH=%USERPROFILE%\AppData\Local\Programs\antigravity\Antigravity.exe"
)

if "%ANTIGRAVITY_PATH%"=="" (
    echo [ERROR] Antigravity не найден!
    echo Скачайте с: https://antigravity.google/download
    pause
    exit /b 1
)

echo [OK] Найден: %ANTIGRAVITY_PATH%
echo.

REM Запуск
echo [3/3] Запуск Antigravity...
start "" "%ANTIGRAVITY_PATH%"

echo [OK] Antigravity запущен
