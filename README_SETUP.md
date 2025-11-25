# ✅ Проект настроен! Быстрый старт

## Что готово

Проект полностью настроен для управления VPN и обхода блокировок Google Gemini через Claude Code.

### Структура проекта

```
google_gemini_vpn/
├── scripts/               # Управление VPN
│   ├── monitor-logs.sh    # Логи Tallinn в реальном времени
│   ├── vpn-status.sh      # Диагностика VPN (сервер, трафик)
│   ├── quick-check.sh     # Проверка готовности для Gemini
│   └── apply-dns-config.sh # Применение DNS конфигурации
├── configs/
│   ├── nekobox/
│   │   └── routing-google.json # DNS маршрутизация
│   └── warp/
│       └── settings.md    # Руководство WARP
├── docs/
│   ├── ARCHITECTURE.md    # Архитектура системы
│   └── TROUBLESHOOTING.md # Решение проблем
└── CLAUDE.md             # Инструкции для Claude Code
```

## Быстрые команды

### 1. Проверка состояния

```bash
# Полная проверка готовности
./scripts/quick-check.sh

# Статус VPN (сервер, трафик, настройки)
./scripts/vpn-status.sh
```

### 2. Мониторинг

```bash
# Логи Tallinn в реальном времени (цветной вывод)
./scripts/monitor-logs.sh
```

### 3. Настройка DNS

```bash
# Применить конфигурацию DNS для Google доменов
./scripts/apply-dns-config.sh

# После применения - перезапустить NekoBox!
```

### 4. Запуск браузера

```bash
# Linux/WSL
./gemini-browser.sh

# Windows
gemini-browser.bat
```

## Что нужно сделать (первый запуск)

### Шаг 1: Применить DNS конфигурацию

```bash
./scripts/apply-dns-config.sh
```

**Важно:** После применения перезапустите NekoBox!

### Шаг 2: Проверить готовность

```bash
./scripts/quick-check.sh
```

Скрипт проверит:
- ✅ NekoBox активен (Tallinn)
- ✅ DNS объект активирован
- ✅ FakeDNS включен
- ⚠️ Локаль браузера (требует ручной настройки)
- ⚠️ Google аккаунт (требует создания нового)

### Шаг 3: Запустить браузер

```bash
./gemini-browser.sh
```

В браузере выполнить:
1. `chrome://settings/languages` → удалить русский ПОЛНОСТЬЮ
2. `chrome://settings/clearBrowserData` → All time
3. Проверить: https://ipleak.net → Language: en-US (без ru!)

### Шаг 4: Создать новый Google аккаунт

1. VPN ON + изолированный Chrome
2. https://accounts.google.com/signup
3. Country: Estonia, Email: proton.me
4. БЕЗ российского телефона

### Шаг 5: Доступ к Gemini

1. https://aistudio.google.com
2. Войти новым аккаунтом
3. Get API key → Create key
4. ✅ Gemini 2.5 Pro доступен!

## Cloudflare WARP (если нужно)

Если AI Studio виснет при загрузке:

1. Запустить "Cloudflare WARP.exe" (иконка в трее)
2. Connect → Режим WARP
3. Проверить: ipleak.net → DNS Cloudflare

Подробнее: [configs/warp/settings.md](configs/warp/settings.md)

## Решение проблем

**Полное руководство:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

### Типичные проблемы:

**DNS не работает:**
```bash
./scripts/apply-dns-config.sh
# Перезапустить NekoBox
```

**Accept-Language всё ещё ru:**
```bash
./gemini-browser.sh
# chrome://settings/languages → удалить русский
# chrome://settings/clearBrowserData → All time
```

**AI Studio висит:**
```bash
# Включить WARP (см. configs/warp/settings.md)
```

## Мониторинг и диагностика

```bash
# Статус VPN
./scripts/vpn-status.sh

# Логи в реальном времени
./scripts/monitor-logs.sh

# Полная проверка
./scripts/quick-check.sh

# Проверка утечек (Windows)
./check-leaks.bat
```

## Документация

- [CLAUDE.md](CLAUDE.md) - Инструкции для Claude Code
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Архитектура системы
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Решение проблем
- [configs/warp/settings.md](configs/warp/settings.md) - Руководство WARP
- [gemini-vpn-full-setup.md](gemini-vpn-full-setup.md) - Полная документация

## Важные ссылки

- Проверка IP: https://ipleak.net
- DNS leak test: https://dnsleaktest.com
- WebRTC leak: https://browserleaks.com/webrtc
- Google AI Studio: https://aistudio.google.com

## Текущая конфигурация VPN

- **Сервер**: Tallinn (89.169.15.11:38029)
- **Протокол**: VLESS Reality + XTLS-RPRX-Vision
- **DNS**: Cloudflare DoH (https://1.1.1.1/dns-query)
- **FakeDNS**: Включен
- **Трафик**: ~30 GB DL / 3.6 GB UL

Проверить статус: `./scripts/vpn-status.sh`
