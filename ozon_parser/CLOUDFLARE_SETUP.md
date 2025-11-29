# Настройка Cloudflare Tunnel для Ozon Parser

## 1. Установка cloudflared (Windows)

```powershell
# Вариант 1: через winget
winget install Cloudflare.cloudflared

# Вариант 2: скачать вручную
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

## 2. Авторизация в Cloudflare

```bash
cloudflared tunnel login
```
Откроется браузер → выбери домен → авторизуйся.

## 3. Создание туннеля

```bash
# Создать туннель
cloudflared tunnel create ozon-parser

# Проверить что создался
cloudflared tunnel list
```

## 4. Настройка DNS

```bash
# Добавить DNS запись (заменить YOUR-DOMAIN.COM на свой домен)
cloudflared tunnel route dns ozon-parser ozon-parser.YOUR-DOMAIN.COM
```

Или вручную в Cloudflare Dashboard:
1. DNS → Add Record
2. Type: CNAME
3. Name: ozon-parser
4. Target: <TUNNEL_ID>.cfargotunnel.com

## 5. Конфигурация туннеля

Создать файл `~/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: C:\Users\<USERNAME>\.cloudflared\<TUNNEL_ID>.json

ingress:
  - hostname: ozon-parser.YOUR-DOMAIN.COM
    service: http://localhost:8080
  - service: http_status:404
```

## 6. Запуск

### Терминал 1: API сервер
```bash
cd ozon_parser
run_server.bat
# или: python -m uvicorn api_server:app --host 0.0.0.0 --port 8080
```

### Терминал 2: Cloudflare Tunnel
```bash
cloudflared tunnel run ozon-parser
```

## 7. Проверка

```bash
# Локально
curl http://localhost:8080/health

# Через туннель
curl https://ozon-parser.YOUR-DOMAIN.COM/health
```

## 8. Автозапуск (Windows Service)

```bash
# Установить как Windows Service
cloudflared service install

# Запустить сервис
sc start cloudflared
```

---

## Альтернатива: ngrok (проще, но URL меняется)

```bash
# Установка
winget install ngrok

# Авторизация
ngrok config add-authtoken YOUR_TOKEN

# Запуск
ngrok http 8080
```

URL будет типа: `https://abc123.ngrok-free.app`

---

## Использование из Unify

```typescript
const PARSER_URL = "https://ozon-parser.YOUR-DOMAIN.COM";

// Парсинг одного SKU
const result = await fetch(`${PARSER_URL}/parse/1234567`);
const data = await result.json();
// { sku: "1234567", price: 1500, name: "...", ... }

// Batch парсинг
const batch = await fetch(`${PARSER_URL}/parse/batch`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ skus: ["123", "456", "789"] })
});
```
