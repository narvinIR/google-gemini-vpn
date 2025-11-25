@echo off
REM Скрипт для запуска Chrome с английской локалью для обхода блокировок Google AI Studio (Windows)
REM Двойной клик или cmd: gemini-browser.bat
REM Требования: Google Chrome установлен

REM Установка английской локали
set LANG=en_US.UTF-8
set LANGUAGE=en_US
set LC_ALL=en_US.UTF-8

REM Директория профиля
set PROFILE_DIR=%USERPROFILE%\ChromeGemini

REM Параметры запуска для маскировки (без warning флага)
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --user-data-dir="%PROFILE_DIR%" ^
  --lang=en-US ^
  --accept-lang=en-US,en;q=0.9 ^
  --disable-features=WebRtcHideLocalIpsWithMdns ^
  --webrtc-ip-handling-policy=disable_non_proxied_udp ^
  --disable-web-security ^
  --no-first-run ^
  --disable-background-timer-throttling ^
  https://aistudio.google.com

pause
echo.
echo Браузер запущен с английской локалью.
echo 1. Проверьте chrome://settings/languages - удалите RU полностью!
echo 2. Очистите cookies: chrome://settings/clearBrowserData (All time)
echo 3. Создайте новый Google аккаунт (Estonia, proton.me email).