@echo off
chcp 65001 >nul
title OZON Parser - Локальная версия

echo ============================================================
echo   OZON PARSER - Запуск на Windows
echo ============================================================
echo.

REM Путь к Python (изменить если нужно)
set PYTHON=python

REM Проверяем Python
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден! Установи Python 3.10+
    pause
    exit /b 1
)

REM Проверяем зависимости
%PYTHON% -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Устанавливаем зависимости...
    pip install playwright playwright-stealth gspread google-auth
    playwright install chromium
)

REM Переходим в директорию проекта
cd /d "%~dp0"

echo.
echo Режимы запуска:
echo   1. Полный парсинг (все SKU из Google Sheets)
echo   2. Тест (первые 5 SKU)
echo   3. Свой список SKU
echo   4. Выход
echo.

set /p choice="Выбери режим (1-4): "

if "%choice%"=="1" (
    echo.
    echo [START] Запуск полного парсинга...
    %PYTHON% auto_parser.py
)

if "%choice%"=="2" (
    echo.
    echo [START] Тестовый режим (5 SKU)...
    %PYTHON% auto_parser.py --limit 5
)

if "%choice%"=="3" (
    echo.
    set /p skus="Введи SKU через пробел: "
    %PYTHON% auto_parser.py --skus %skus%
)

if "%choice%"=="4" (
    exit /b 0
)

echo.
echo ============================================================
echo   Готово! Результаты записаны в Google Sheets
echo ============================================================
pause
