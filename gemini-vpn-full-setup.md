# Полная выжимка сессии: Настройка VPN для Google AI Studio

**Дата:** 23 ноября 2025  
**Проблема:** Google AI Studio блокирует доступ по языку браузера (Accept-Language: ru), несмотря на VPN (NekoBox, IP Estonia, DNS Cloudflare).  
**Цель:** Полный обход для веб-интерфейса + API (уже работает через relay).

## 🎯 Архитектура системы

```mermaid
graph TD
    A[NekoBox VPN<br/>VLESS Reality Estonia] --> B[Hijack DNS<br/>Cloudflare DoH<br/>https://1.1.1.1/dns-query]
    B --> C[Browser скрипт<br/>LANG=en_US<br/>--lang=en-US<br/>Удалить ru язык]
    C --> D[Новый Google аккаунт<br/>Страна: Estonia<br/>Email: proton.me<br/>Без RU телефона]
    D --> E[Google AI Studio<br/>aistudio.google.com]
    E --> F[API Relay<br/>Cloudflare Workers<br/>gemini-2.5-pro]
    style A fill:#f9f
    style E fill:#bbf
```

## ✅ Что уже работает
- **API Gemini:** Через relay `https://gemini-api-relay.schmidvili1.workers.dev`  
  Ключ: `AIzaSyCSfBuzJRya9X5LymMTlsyqvo8ZAhykSLw`  
  Модель: `gemini-2.5-pro` (бесплатно)  
  MCP сервер в Claude Desktop.
- **VPN:** IP 89.169.15.11 (Estonia), DNS Cloudflare.

## ❌ Основная проблема
```
Accept-Language: ru, en;q=0.9 ← Google видит русский как основной!
```
Решение: Изолированный браузер с английской локалью + новый аккаунт.

## 📋 Пошаговый план настройки

### 1. NekoBox DNS (routing.json)
```json
{
  "dns": {
    "servers": [
      {"tag": "cloudflare", "address": "https://1.1.1.1/dns-query", "detour": "proxy"}
    ],
    "rules": [
      {"domain": ["google.com", "googleapis.com"], "server": "cloudflare"}
    ]
  }
}
```
GUI: Hijack DNS ON, Remote DNS: https://1.1.1.1/dns-query.

### 2. Скрипт браузера (Linux: chromium)
Создать `gemini-browser.sh`:
```bash
#!/bin/bash
export LANG=en_US.UTF-8
export LANGUAGE=en_US
chromium-browser \
  --user-data-dir=$HOME/.chrome-gemini \
  --lang=en-US \
  --accept-lang=en-US,en;q=0.9 \
  --disable-features=WebRtcHideLocalIpsWithMdns \
  --webrtc-ip-handling-policy=disable_non_proxied_udp
```
```bash
chmod +x gemini-browser.sh
./gemini-browser.sh
```

**В браузере:**
- chrome://settings/languages → Удалить ru, оставить en-US.
- Очистить cookies/cache.

### 3. Проверки утечек
- [ipleak.net](https://ipleak.net) → Accept-Language: en-US
- [dnsleaktest.com](https://dnsleaktest.com) → Только Cloudflare
- [browserleaks.com/geo](https://browserleaks.com/geo) → Estonia

### 4. Новый Google аккаунт
- Incognito + VPN.
- accounts.google.com/signup → Country: Estonia, proton.me email.

### 5. Альтернативы (Windows)

#### Cloudflare WARP - бесплатный VPN/DNS от Cloudflare (решает тормоза)
1. Скачай app: https://1.1.1.1/
2. Установи, запусти.
3. Режим "WARP" (не +).
4. **Включи поверх NekoBox** - ускоряет, шифрует DNS.
5. AI Studio перестанет висеть.

#### Residential proxy
- IPRoyal Residential Proxies
- Mysterium VPN (децентрализованный)

#### Дополнительно: Очистка DNS (Windows)
```cmd
ipconfig /flushdns
```

## 🧪 Тестирование
1. Запустить VPN + скрипт браузера.
2. Проверить утечки.
3. Создать/войти аккаунт → aistudio.google.com.

## 🔗 Ресурсы
- Relay: https://gemini-api-relay.schmidvili1.workers.dev
- Проверки: ipleak.net, dnsleaktest.com
- WARP: https://1.1.1.1/

**Статус:** API ✅, Веб - после настроек языка ✅