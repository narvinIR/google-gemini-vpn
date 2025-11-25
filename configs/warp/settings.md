# Cloudflare WARP - Руководство

## Что такое WARP

Cloudflare WARP - бесплатный VPN/DNS сервис от Cloudflare. Используется как усилитель поверх NekoBox для обхода блокировок Google.

## Расположение

```
C:\Program Files\Cloudflare\Cloudflare WARP\
├── Cloudflare WARP.exe    # GUI приложение (иконка в трее)
├── warp-cli.exe           # CLI управление
└── warp-svc.exe           # Системный сервис
```

## Зачем нужен WARP

### Основные функции:

1. **Двойной туннель**: NekoBox → WARP → Google
   - NekoBox скрывает реальный IP (Estonia)
   - WARP шифрует DNS через 1.1.1.1
   - Google видит Cloudflare сеть (меньше подозрений)

2. **Ускорение DNS**:
   - Резолвинг через оптимизированные Cloudflare серверы
   - Устраняет "висяки" AI Studio при загрузке

3. **Обход детекции датацентровых IP**:
   - VPN серверы часто в blacklist Google
   - WARP добавляет слой резидентности
   - Снижает вероятность капчи

## Когда использовать

### ✅ Включать WARP:

- AI Studio виснет при загрузке страницы
- DNS резолвинг медленный (проверить: dnsleaktest.com)
- Google показывает капчу при входе
- Блокировка сохраняется даже с правильной локалью

### ❌ НЕ нужен WARP:

- NekoBox один справляется (быстрая загрузка)
- AI Studio работает стабильно
- Нет проблем с DNS

## Как использовать

### Запуск:

1. Найти иконку "Cloudflare WARP" в трее Windows
2. Клик → Connect
3. Режим: **WARP** (НЕ WARP+, платный)
4. **Важно**: NekoBox должен быть запущен ДО WARP

### Проверка:

```bash
# Открыть в браузере (с включенным NekoBox + WARP):
https://ipleak.net
```

**Ожидаемый результат:**
- IP: Estonia (от NekoBox)
- DNS: Cloudflare (от WARP)
- Language: en-US (от изолированного браузера)

### Отключение:

1. Иконка в трее → Disconnect
2. Или автоматически при закрытии

## CLI управление (опционально)

```cmd
# Проверка статуса
"C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe" status

# Подключение
warp-cli connect

# Отключение
warp-cli disconnect

# Режим (warp или warp+)
warp-cli mode warp
```

## Настройки

### Рекомендуемая конфигурация:

1. Открыть GUI → Settings (шестеренка)
2. **Preferences**:
   - Mode: WARP
   - Exclude local network: OFF (отключить)
   - Auto-connect: OFF (вручную)
3. **Privacy**:
   - No logs ✅ (по умолчанию)

## Диагностика проблем

### WARP не подключается:

```bash
# Проверить сервис
sc query WarpSvc

# Перезапустить
sc stop WarpSvc
sc start WarpSvc
```

### Конфликт с NekoBox:

- Сначала запускать NekoBox
- Потом WARP
- Если не работает - отключить WARP, перезапустить NekoBox

### DNS утечки:

```bash
# Проверить:
https://dnsleaktest.com (Extended test)

# Должен показывать только Cloudflare
# Если видны DNS провайдера - WARP не работает
```

## Архитектура туннеля

```
Браузер (Chrome en-US)
    ↓
NekoBox VPN (Estonia IP: 89.169.15.11)
    ↓
WARP (Cloudflare шифрование DNS)
    ↓
Google AI Studio (видит: Estonia + Cloudflare + en-US)
```

## FAQ

**Q: Всегда ли нужен WARP?**
A: Нет, только если NekoBox один не справляется.

**Q: Замедляет ли интернет?**
A: Незначительно. DNS даже ускоряется.

**Q: Можно ли использовать без NekoBox?**
A: Да, но WARP один не меняет IP на Estonia (Google поймет что Россия).

**Q: WARP+ стоит покупать?**
A: Нет, бесплатного WARP достаточно для Gemini.

## Ссылки

- Скачать: https://1.1.1.1/
- Документация: https://developers.cloudflare.com/warp-client/
- Статус сервиса: https://www.cloudflarestatus.com/
