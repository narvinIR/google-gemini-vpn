# Решение проблем Google Gemini VPN

## Быстрая диагностика

```bash
# Запустить полную проверку
./scripts/quick-check.sh

# Проверить статус VPN
./scripts/vpn-status.sh

# Мониторинг логов
./scripts/monitor-logs.sh
```

## Типичные проблемы

### 1. Google AI Studio недоступен

**Симптомы:**
- "Service unavailable in your region"
- Бесконечная загрузка страницы
- Капча при входе

**Решение:**

```bash
# Шаг 1: Проверить VPN
./scripts/vpn-status.sh
# Должно показать: Tallinn (89.169.15.11)

# Шаг 2: Проверить DNS
./scripts/apply-dns-config.sh
# Применить конфигурацию DNS

# Шаг 3: Проверить утечки
./check-leaks.bat  # Windows
# ipleak.net должен показать: Language en-US, IP Estonia

# Шаг 4: Включить WARP (если не помогло)
# Запустить Cloudflare WARP → Connect
```

### 2. Accept-Language всё ещё ru

**Симптомы:**
- ipleak.net показывает Language: ru
- Google распознает русскую локаль

**Решение:**

```bash
# 1. Запустить изолированный браузер
./gemini-browser.sh  # Linux
# или gemini-browser.bat  # Windows

# 2. В браузере:
chrome://settings/languages
# Удалить "русский" ПОЛНОСТЬЮ (не просто переместить вниз!)

# 3. Очистить всё
chrome://settings/clearBrowserData
# All time → Cookies, Cache, History → Clear

# 4. Перезапустить браузер
```

### 3. DNS утечки (провайдер вместо Cloudflare)

**Симптомы:**
- dnsleaktest.com показывает DNS провайдера (не Cloudflare)
- AI Studio определяет регион по DNS

**Решение:**

```bash
# Применить DNS конфигурацию
./scripts/apply-dns-config.sh

# Перезапустить NekoBox (Windows GUI)
# Проверить параметр в GUI:
# Settings → Route → DNS Settings
# - Use DNS Object: ON
# - Remote DNS: https://1.1.1.1/dns-query
# - Hijack DNS: ON
# - FakeDNS: ON
```

### 4. NekoBox не подключается

**Симптомы:**
- Timeout при подключении
- Логи показывают: "dial tcp: timeout"

**Решение:**

```bash
# 1. Проверить сервер Tallinn доступен
ping 89.169.15.11

# 2. Проверить порт открыт
nc -zv 89.169.15.11 38029

# 3. Переключить на резервный сервер (профиль 39)
# В NekoBox GUI → выбрать профиль 39 (31.169.125.118)

# 4. Проверить логи
./scripts/monitor-logs.sh
# Искать ERROR или WARN
```

### 5. AI Studio висит при загрузке

**Симптомы:**
- Страница загружается бесконечно
- Белый экран или spinner

**Решение:**

```bash
# 1. Включить Cloudflare WARP
# Иконка в трее Windows → Connect
# Режим: WARP (не WARP+)

# 2. Очистить DNS кеш (Windows)
ipconfig /flushdns

# 3. Перезапустить браузер
# Закрыть все окна Chrome
# Запустить: ./gemini-browser.bat
```

### 6. Старый Google аккаунт блокируется

**Симптомы:**
- Аккаунт создан в России
- AI Studio недоступен даже с VPN

**Решение:**

```bash
# Создать НОВЫЙ аккаунт через VPN:

# 1. Запустить VPN + изолированный браузер
./scripts/quick-check.sh  # Проверить готовность
./gemini-browser.sh

# 2. Проверить утечки
# https://ipleak.net
# Должно быть: IP Estonia, Language en-US

# 3. Создать аккаунт
# https://accounts.google.com/signup
# Country: Estonia
# Email: проверочный от proton.me (НЕ mail.ru!)
# Без российского телефона

# 4. После создания
# myaccount.google.com/language → English (United States)
# НИКОГДА не добавлять русский язык!
```

### 7. WebRTC утечки IP

**Симптомы:**
- browserleaks.com/webrtc показывает реальный IP

**Решение:**

Параметры уже добавлены в скрипт [gemini-browser.sh](../gemini-browser.sh):
```bash
--disable-features=WebRtcHideLocalIpsWithMdns
--webrtc-ip-handling-policy=disable_non_proxied_udp
```

Дополнительно в Chrome:
```
chrome://flags/#enable-webrtc-hide-local-ips-with-mdns
# Установить: Disabled
```

### 8. WARP конфликтует с NekoBox

**Симптомы:**
- После включения WARP интернет пропадает
- NekoBox показывает "disconnected"

**Решение:**

```bash
# Порядок запуска КРИТИЧЕН:
# 1. Сначала запустить NekoBox
# 2. Проверить подключение (vpn-status.sh)
# 3. Потом запустить WARP

# Если не работает:
# - Отключить WARP
# - Перезапустить NekoBox
# - Использовать без WARP (NekoBox должен справиться один)
```

### 9. Нет доступа к Gemini 2.5 Pro

**Симптомы:**
- В AI Studio доступна только старая модель
- "Model not available"

**Решение:**

```bash
# 1. Проверить регион аккаунта
# myaccount.google.com → Data & privacy → Location History
# Должно быть: Estonia

# 2. Получить API ключ
# https://aistudio.google.com
# Get API key → Create key
# Модель: gemini-2.5-pro (бесплатно)

# 3. Если не помогает - использовать Relay API
# Уже работает: gemini-api-relay.schmidvili1.workers.dev
```

## Проверочные команды

### Проверка VPN
```bash
./scripts/vpn-status.sh
# Ожидается: Tallinn active, 89.169.15.11
```

### Проверка DNS
```bash
nslookup google.com
# Должен отвечать: 1.1.1.1 (Cloudflare)
```

### Проверка языка
```bash
curl -s https://ipleak.net | grep -i language
# Должно быть: en-US (без ru!)
```

### Мониторинг логов
```bash
./scripts/monitor-logs.sh
# Фильтрация: ERROR, WARN, google, gemini
```

## Логи и диагностика

### Расположение логов NekoBox
```
/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/neko.log
```

### Полезные команды
```bash
# Последние 50 строк
tail -50 neko.log

# Ошибки
grep -i error neko.log

# Google трафик
grep -i google neko.log | tail -20

# Статистика по доменам
grep -oP 'to \K[^:]+' neko.log | sort | uniq -c | sort -rn
```

## Критичные параметры

### NekoBox конфигурация

Файл: `/mnt/c/.../config/routes_box/Default`
```json
{
  "use_dns_object": true,  ← ДОЛЖЕН быть true
  "fakedns": true,         ← ДОЛЖЕН быть true
  "remote_dns": "1.1.1.1"  ← Cloudflare
}
```

### Браузер

Обязательно:
- Accept-Language: en-US,en;q=0.9 (БЕЗ ru!)
- Изолированный профиль (--user-data-dir)
- Очищенные cookies/cache

### Google аккаунт

Обязательно:
- Создан через VPN (Estonia)
- Язык: English (United States)
- БЕЗ русского языка в настройках

## Полезные ссылки

- Проверка IP: https://ipleak.net
- DNS leak test: https://dnsleaktest.com
- WebRTC leak: https://browserleaks.com/webrtc
- Общая анонимность: https://whoer.net
- Google AI Studio: https://aistudio.google.com

## Экстренное восстановление

Если ничего не помогает:

```bash
# 1. Остановить всё
# - Закрыть все браузеры
# - Отключить WARP
# - Остановить NekoBox

# 2. Очистить DNS
ipconfig /flushdns  # Windows

# 3. Перезапустить NekoBox
# GUI → Stop → Start

# 4. Применить DNS конфигурацию
./scripts/apply-dns-config.sh

# 5. Проверка
./scripts/quick-check.sh

# 6. Запустить браузер
./gemini-browser.sh
```
