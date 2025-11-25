# Архитектура системы обхода блокировок Google Gemini

## Обзор

Проект реализует многоуровневую систему обхода региональных блокировок Google AI Studio (Gemini API) через комбинацию VPN-туннелирования, DNS-маскировки и подмены языковых настроек браузера.

## Схема компонентов

```mermaid
graph TD
    A[Браузер Chrome/Chromium] -->|Accept-Language: en-US| B[Изолированный профиль]
    B -->|LANG=en_US.UTF-8| C[NekoBox VPN Client]
    C -->|VLESS Reality + XTLS| D[Tallinn Server 89.169.15.11:38029]
    D -->|Encrypted Traffic| E[Cloudflare DoH DNS]
    E -->|DNS Query| F[Google Domains]
    F -->|Response| G[Google AI Studio]

    H[WARP Optional] -.->|Усиление DNS| E

    style A fill:#e1f5ff
    style D fill:#ffe1e1
    style E fill:#e1ffe1
    style G fill:#fff4e1
    style H fill:#f0f0f0,stroke-dasharray: 5 5
```

## Уровни защиты

### 1. Сетевой уровень (NekoBox VPN)

**Протокол:** VLESS Reality + XTLS-RPRX-Vision

**Функции:**
- IP маскировка → Estonia (89.169.15.11)
- TLS fingerprint маскировка → yahoo.com
- XTLS туннелирование → обход DPI

### 2. DNS уровень (Cloudflare DoH)

**Критичный параметр:**
\`\`\`json
"use_dns_object": true  // ДОЛЖЕН быть true!
\`\`\`

### 3. Приложенческий уровень (Браузер)

**Критично:**
- chrome://settings/languages → удалить русский ПОЛНОСТЬЮ
- chrome://settings/clearBrowserData → очистить всё (All time)
- Новый Google аккаунт (создан через VPN, Estonia)

## Компоненты проекта

### Скрипты мониторинга

- scripts/monitor-logs.sh - Логи NekoBox в реальном времени
- scripts/vpn-status.sh - Статус VPN (IP, трафик, сервер)
- scripts/quick-check.sh - Быстрая проверка готовности
- scripts/apply-dns-config.sh - Применение DNS конфигурации

### Ключевые метрики

| Параметр | Проверка | Ожидаемое |
|----------|----------|-----------|
| IP адрес | ipleak.net | 89.169.15.11 (Estonia) |
| DNS | dnsleaktest.com | Cloudflare (1.1.1.1) |
| Language | ipleak.net | en-US (без ru!) |
| WebRTC | browserleaks.com/webrtc | No leaks |

