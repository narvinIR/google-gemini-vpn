# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Назначение проекта

Набор скриптов и конфигураций для обхода региональных блокировок Google AI Studio (Gemini) через VPN-туннелирование с маскировкой языковых настроек браузера.

## Архитектура системы

```
NekoBox VPN (VLESS Reality, Estonia)
    ↓
DNS Hijacking → Cloudflare DoH (1.1.1.1/dns-query)
    ↓
Изолированный браузер (LANG=en_US, --lang=en-US)
    ↓
Google AI Studio (новый аккаунт, Estonia)
```

**Критичные компоненты:**
- `neko-routing-sample.json` — DNS-маршрутизация через Cloudflare для всех Google-доменов
- `gemini-browser.{sh,bat}` — запуск браузера с английской локалью в изолированном профиле
- Accept-Language заголовок должен быть **en-US** (не ru!) для обхода блокировки

## MCP Серверы для исследований

**Установленные серверы:**
- **Perplexity MCP** (sonar-pro) - быстрые запросы (500/день)
- **GitHub MCP** - работа с репозиториями
- **Playwright MCP** - автоматизация браузера для Perplexity Pro (GPT-5.1, Claude, Gemini, Grok)
- **Sequential Thinking MCP** - сложные рассуждения
- **Memory MCP** - сохранение контекста (./research/research_memory.json)
- **Filesystem MCP** - доступ к файлам проекта

**Документация:**
- [README_MCP.md](README_MCP.md) - общая документация MCP
- [docs/PERPLEXITY_PLAYWRIGHT_MCP.md](docs/PERPLEXITY_PLAYWRIGHT_MCP.md) - **доступ ко всем моделям Perplexity Pro**

**Workflow:**
- Быстрые факты → Perplexity MCP API (5-10 сек)
- Frontier модели → Playwright MCP + Perplexity UI (GPT-5.1, Claude, Gemini, Grok)
- Deep Research → Playwright MCP (5-15 мин, без API лимитов)
- Работа с кодом → GitHub MCP + Filesystem

## Основные команды

### Команды запуска

```bash
# Запуск браузера
./gemini-browser.sh             # Linux/WSL
gemini-browser.bat              # Windows

# Проверка утечек
check-leaks.bat                 # Windows (IP, DNS, Language)
```

### Linux/WSL
```bash
# Запуск Chromium с маскировкой локали
chmod +x gemini-browser.sh
./gemini-browser.sh

# После запуска в браузере:
# 1. chrome://settings/languages → удалить ru полностью
# 2. chrome://settings/clearBrowserData → очистить всё
```

### Windows
```cmd
# Проверка утечек (VPN должен быть включен)
check-leaks.bat

# Поиск установки NekoBox/Nekoray
find-nekoray.bat

# Запуск Chrome с английской локалью
gemini-browser.bat
```

## Конфигурация NekoBox

Файл `config/routing.json` в директории NekoBox:
- DNS-серверы: Cloudflare DoH через прокси + fallback direct
- Routing rules: все `*.google.com`, `*.googleapis.com` через proxy
- GUI настройки: Hijack DNS ON, Fake DNS ON, Remote DNS: `https://1.1.1.1/dns-query`

**Критично:** Перезапустить NekoBox после изменения routing.json

## Проверка корректности настройки

Запустить `check-leaks.bat`, проверить:
1. **ipleak.net** → Language: en-US (не ru!), IP: Estonia
2. **dnsleaktest.com** → только Cloudflare DNS
3. **browserleaks.com/webrtc** → WebRTC IP не утекает

## Важные детали реализации

### Параметры запуска браузера
```bash
--user-data-dir      # Изолированный профиль (не загрязняет основной)
--lang=en-US         # Принудительная локаль UI
--accept-lang=en-US,en;q=0.9  # Accept-Language заголовок
--disable-features=WebRtcHideLocalIpsWithMdns  # Отключить WebRTC утечки
--webrtc-ip-handling-policy=disable_non_proxied_udp
```

### Переменные окружения (Linux)
```bash
LANG=en_US.UTF-8
LANGUAGE=en_US
LC_ALL=en_US.UTF-8
```

### Relay API (уже работает)
- Endpoint: `gemini-api-relay.schmidvili1.workers.dev` (Cloudflare Workers)
- Модель: `gemini-2.5-pro` (бесплатно)
- **Не показывать API ключи в выводе** (замаскированы в исходниках как **_СКРЫТО_**)

## Структура проекта

```
google_gemini_vpn/
├── configs/
│   ├── nekobox/
│   │   └── routing-google.json # DNS маршрутизация
│   └── warp/
│       └── settings.md         # Руководство WARP
├── docs/
│   ├── AI_WORKFLOW.md          # Мульти-модельный AI workflow
│   ├── ARCHITECTURE.md         # Архитектура системы
│   ├── PERPLEXITY_PLAYWRIGHT_MCP.md  # Playwright MCP
│   └── TROUBLESHOOTING.md      # Решение проблем
├── gemini-browser.{sh,bat}     # Запуск браузера
├── check-leaks.bat             # Проверка утечек
├── .mcp.json.example           # Шаблон MCP конфига
└── CLAUDE.md                   # Этот файл
```

## Решение проблем

**Полное руководство**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

**AI Studio висит при загрузке:**
- Включить Cloudflare WARP (1.1.1.1 app) поверх NekoBox
- WARP ускоряет DNS-резолвинг и шифрует трафик дополнительно
- См. [configs/warp/settings.md](configs/warp/settings.md)

**"No API key" в AI Studio:**
- Создать новый Google-аккаунт через изолированный браузер (VPN ON)
- Country: Estonia, Email: proton.me (без RU телефона)
- Генерировать ключ в aistudio.google.com

**Accept-Language всё ещё ru:**
- Очистить `chrome://settings/clearBrowserData` → All time
- В `chrome://settings/languages` удалить русский язык физически (не просто переместить)
- Перезапустить браузер

**DNS не работает (use_dns_object: false):**
- Скопировать `configs/nekobox/routing-google.json` в директорию NekoBox
- Перезапустить NekoBox
