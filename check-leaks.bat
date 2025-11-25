@echo off
REM Скрипт проверки утечек для VPN/Google AI Studio (Windows)
REM Запускать с VPN включенным

echo === Очистка DNS кеша ===
ipconfig /flushdns

echo.
echo === DNS для google.com ===
nslookup google.com

echo.
echo === IP config DNS ===
ipconfig /all | findstr DNS

echo.
echo === Открываем сайты проверки ===
start https://ipleak.net
start https://dnsleaktest.com
start https://browserleaks.com/webrtc
start https://whoer.net

echo.
echo Проверьте:
echo 1. ipleak.net: IP Estonia, Language en-US (без ru!), DNS Cloudflare
echo 2. dnsleaktest.com: Только Cloudflare (Extended test)
echo 3. browserleaks.com: Geolocation Estonia
echo.
echo Если OK - запускайте gemini-browser.bat!
pause