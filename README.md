# 🚀 Простая инструкция: Обход Google AI Studio (Windows + NekoBox)

## Что готово:
- API Gemini работает ✅
- Скрипты для веб: браузер без русского языка

## Как запускать .bat из VSCode (WSL):
1. Ctrl+Shift+` → Terminal → cmd
2. `C:\path\to\gemini-browser.bat` (скопируйте путь)
Или:
1. Правой кнопкой на bat в Explorer → Open with → Command Prompt

**Лучше:** Скопируйте bat/json в C:\Users\Пользователь\Desktop → двойной клик в Проводнике.

## Шаги (5 минут):

### 1. NekoBox config
- Двойной клик [find-nekoray.bat](find-nekoray.bat) → найдёт папку Nekoray
- В папке Nekoray: config/routing.json (создайте папку config если нет)
- Замените содержимое на [neko-routing-sample.json](neko-routing-sample.json)
- В GUI Nekoray: Settings → Route → Hijack DNS ✅, Fake DNS ✅, Remote DNS: https://1.1.1.1/dns-query
- Перезапустите NekoBox

### 2. Проверьте утечки
- Двойной клик [check-leaks.bat](check-leaks.bat)
- **Важно:** ipleak.net должен показать Language: en-US (без ru!)

### 3. Запустите специальный Chrome
- Двойной клик [gemini-browser.bat](gemini-browser.bat)
- В новом Chrome:
  - `chrome://settings/languages` → **Удалите русский полностью**
  - `chrome://settings/clearBrowserData` → Очистить всё

### 4. Новый аккаунт Google
- В этом Chrome (VPN ON!)
- https://accounts.google.com/signup
- Country: Estonia
- Email: proton.me (без RU номера)

### 5. AI Studio
- https://aistudio.google.com → войдите новым аккаунтом
- "Get API key" → Создайте ключ (бесплатно для gemini-2.5-pro)
- ✅ Работает! (если "No API key" - создайте ключ)

### Если висит - WARP (ускоряет)
1. Запустите 1.1.1.1 app (иконка в трее)
2. Connect → WARP ON (поверх NekoBox)
3. Повторите шаги 2-5 - Studio перестанет висеть
- Полная инструкция: [gemini-vpn-full-setup.md](gemini-vpn-full-setup.md)
- Все файлы: [Gemini.md](Gemini.md)

**Готово! Скрипты .bat - двойной клик.**