@echo off
REM Найти Nekoray/NekoBox на диске C:
echo Ищем Nekoray/NekoBox...

dir /s /b "C:\*nekoray.exe" 2>nul
dir /s /b "C:\*nekobox.exe" 2>nul
dir /s /b "C:\*neko*.exe" 2>nul

echo.
echo Найдите папку из списка выше, config/routing.json внутри неё.
echo Если нет - скачайте Nekoray: https://github.com/MatsuriDayo/nekoray/releases
pause