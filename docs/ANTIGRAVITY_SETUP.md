# Google Antigravity - Настройка и обход блокировки

Google Antigravity - бесплатная AI IDE от Google на базе Gemini 3 Pro.

## Что такое Antigravity?

| Характеристика | Описание |
|----------------|----------|
| **Тип** | AI-powered IDE (форк VS Code) |
| **Модель** | Gemini 3 Pro (бесплатно) |
| **Архитектура** | Agent-first (автономные AI агенты) |
| **Платформы** | Windows, macOS, Linux |
| **Цена** | Бесплатно с generous rate limits |

**Возможности:**
- Автономное планирование и выполнение задач
- Доступ к терминалу, редактору, браузеру
- Валидация и итерация кода
- Поддержка Claude Sonnet 4.5 и других моделей

## Заблокированные регионы

Antigravity **НЕ доступен** в:
- Россия
- Китай
- Иран
- Северная Корея
- Сирия
- Куба
- Крым

## Способы обхода блокировки

### Способ 1: Смена региона Google аккаунта (РЕКОМЕНДУЕТСЯ)

1. Перейти: https://policies.google.com/country-association-form
2. Заполнить форму:
   - Целевой регион: **Estonia** / **US** / **Germany**
   - Причина: "Moving to new country" или "Traveling"
3. Отправить заявку
4. Ждать 1-24 часа (обычно ~1 час)
5. После одобрения - войти в Antigravity

### Способ 2: VPN + TUN режим

**Требования:**
- NekoBox/Nekoray с TUN режимом
- VPN сервер в поддерживаемой стране (Estonia работает)

**Настройка:**
1. Включить NekoBox
2. Включить TUN режим (перехват всего трафика)
3. Проверить IP: https://whatismyipaddress.com
4. Запустить Antigravity

### Способ 3: Прокси в настройках Antigravity

1. Запустить Antigravity (с VPN)
2. Settings → Application → Proxy
3. Настроить HTTP/SOCKS прокси
4. Разрешить домены:
   - `open-vsx.org`
   - `*.googleapis.com`
   - `antigravity.google`

## Установка

### Скачивание

Официальный сайт: https://antigravity.google/download

| Платформа | Файл |
|-----------|------|
| Windows | `antigravity-win-x64.exe` |
| macOS Intel | `antigravity-darwin-x64.dmg` |
| macOS ARM | `antigravity-darwin-arm64.dmg` |
| Linux | `antigravity-linux-x64.deb` / `.rpm` |

### Windows

```cmd
# Скачать и установить
# Запуск через VPN:
scripts\antigravity-launcher.bat
```

### Linux/WSL

```bash
# Скачать .deb
sudo dpkg -i antigravity-linux-x64.deb

# Или через launcher
./scripts/antigravity-launcher.sh
```

## Скрипт запуска (с проверкой VPN)

Использовать скрипт `scripts/antigravity-launcher.sh`:

```bash
./scripts/antigravity-launcher.sh
```

Скрипт:
1. Проверяет VPN статус
2. Проверяет регион IP
3. Запускает Antigravity с правильным окружением

## Troubleshooting

### "Your current account is not eligible for Antigravity"

**Решение:**
1. Сменить регион аккаунта: https://policies.google.com/country-association-form
2. Подождать обработки (1-24 часа)
3. Войти заново

### Ошибка подключения / Version mismatch

**Причина:** Сетевая блокировка

**Решение:**
1. Проверить VPN включен
2. Разрешить в прокси: `open-vsx.org`, `*.googleapis.com`
3. Отключить системный firewall временно

### Медленная работа

1. Проверить скорость VPN
2. Попробовать другой VPN сервер
3. Отключить лишние расширения

## Альтернативы

Если Antigravity не работает:

| IDE | AI модель | Цена |
|-----|-----------|------|
| **Cursor** | GPT-4, Claude | $20/мес |
| **Windsurf** | Claude, GPT | $15/мес |
| **GitHub Copilot** | GPT-4 | $10/мес |
| **Cody (Sourcegraph)** | Claude | Бесплатно |

## Ссылки

- [Antigravity Download](https://antigravity.google/download)
- [Смена региона Google](https://policies.google.com/country-association-form)
- [Troubleshooting Guide](https://antigravity.codes/troubleshooting)
- [API Documentation](https://developers.googleblog.com/en/build-with-google-antigravity-our-new-agentic-development-platform/)
