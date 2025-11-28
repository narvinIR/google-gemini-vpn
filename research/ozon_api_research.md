# Ozon API Research — Синтез мнений AI моделей

**Дата:** Ноябрь 2025
**Модели:** Grok 4.1, GPT-5.1, Claude Sonnet 4.5, Gemini 3 Pro

## Проблема
Антибот Ozon блокирует прямой парсинг. Нужны альтернативные методы получения данных (цены, остатки).

---

## КОНСЕНСУС (все модели согласны)

### 1. Ozon Seller API (Официальный)
**Применение:** СВОИ товары
**URL:** `https://api-seller.ozon.ru`

**Headers:**
```
Client-Id: <your_client_id>
Api-Key: <your_api_key>
Content-Type: application/json
```

**Endpoints:**
| Метод | Endpoint | Описание |
|-------|----------|----------|
| Инфо о товарах | `POST /v2/product/info` | product_id, offer_id, sku |
| Цены | `POST /v5/product/info/prices` | текущая, до скидки, Ozon карта |
| Остатки | `POST /v3/product/info/stocks` | FBO/FBS склады |
| Транзакции | `POST /v3/finance/transaction/list` | продажи, комиссии |
| Поисковые запросы | `POST /v1/search-queries/text` | аналитика спроса (Oct 2025) |

**Пример запроса:**
```bash
curl -X POST https://api-seller.ozon.ru/v2/product/info \
  -H 'Client-Id: 12345' \
  -H 'Api-Key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"product_id": [123456789]}'
```

---

### 2. SSR Data (NEXT_DATA)
**Применение:** ЧУЖИЕ товары
**Метод:** Headless browser (Playwright/Puppeteer)

**Где искать в HTML:**
- `<script id="__NEXT_DATA__" type="application/json">...</script>`
- `window.__INITIAL_STATE__` или `window.__STATE__`

**Парсинг (Python):**
```python
import re, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://ozon.ru/product/...')
    html = page.content()

    match = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
    if match:
        data = json.loads(match.group(1))
        # data['props']['pageProps']['initialState']...
```

**Плюсы:** Не нужно гадать endpoints, данные уже в HTML
**Минусы:** Требует browser, ресурсоёмко, нужны прокси

---

### 3. Внутренний Composer API
**Применение:** Web-парсинг без browser
**Риск:** Может меняться, требует поддержки

**Endpoint:**
```
GET/POST https://api.ozon.ru/composer-api.bx/page/json/v2?url=/product/<product_id>/
```

**Headers:**
```
User-Agent: Chrome/120.0.0.0 (desktop)
X-O3-App-Name: dweb_client (или web)
x-o3-app-version: release_...
Cookie: ozon_route, ozon_uid, __Secure-access-token
Content-Type: application/json
```

**Формат ответа:**
```json
{
  "widgetStates": {
    "webPrice-123456-default-1": {...},
    "webProductMain-...": {...}
  }
}
```

---

### 4. Mobile API
**Применение:** Reverse engineering
**Сложность:** Высокая (SSL pinning, gRPC, подписи)

**Endpoints:**
```
POST https://api.ozon.ru/commerce-pub/catalog/api/v2/product
POST https://api.ozon.ru/commerce-pub/catalog/api/v2/search
```

**Headers:**
```
User-Agent: Ozon/Android/10.0.0
Client-Id: android-app
Authorization: Bearer <access_token>
X-Device-Id: ...
X-Platform: android
```

**Инструменты:** Mitmproxy, Charles Proxy, эмулятор Android

**Вердикт Gemini:** В 2025 году мобильное API использует gRPC и требует реверса нативных `.so` библиотек. Не рекомендуется для быстрой разработки.

---

## УНИКАЛЬНЫЕ НАХОДКИ ПО МОДЕЛЯМ

| Модель | Находка |
|--------|---------|
| **Grok 4.1** | Cookies: `ozon_route`, `ozon_uid`; Headers: `X-O3-App`, `X-Requested-With: XMLHttpRequest` |
| **GPT-5.1** | Новые методы Oct 2025: `/v1/search-queries/text`, `/v1/search-queries/top`; cookies `ozon_route`, `ozon_uid` |
| **Claude Sonnet 4.5** | Точный endpoint: `composer-api.bx/page/json/v2?url=/product/<id>/`; таблица методов |
| **Gemini 3 Pro** | Mobile API = gRPC в 2025; требует реверс `.so`; Composer использует widget-based архитектуру |

---

## РЕКОМЕНДАЦИИ (приоритет)

### Для СВОИХ товаров:
**Seller API** — единственный правильный путь
- Легально, стабильно, документировано
- Лимиты: ~80 запросов/мин

### Для ЧУЖИХ товаров (мониторинг конкурентов):
1. **Playwright + SSR** (`__NEXT_DATA__`) — надёжнее
   - Требует: резидентные прокси, ротация IP
   - Плюс: сложнее детектировать

2. **Composer API** — быстрее, но менее стабильно
   - Требует: актуальные cookies, поддержка при изменениях

### НЕ рекомендуется:
- Mobile API (слишком сложный реверс)
- Прямой скрапинг HTML (блокируется антиботом)

---

---

## ПРАКТИЧЕСКАЯ ВЕРИФИКАЦИЯ (Playwright)

**Дата проверки:** Ноябрь 2025

### Результат теста:
- Прямой запрос → **403 Antibot Challenge Page**
- После прохождения challenge → страница загружается

### Подтверждённые рабочие endpoints (Network tab):

```
✅ GET /api/entrypoint-api.bx/page/json/v2?url=...
   — Основной endpoint для загрузки страниц
   — Параметры: url, layout_container, layout_page_index, start_page_id

✅ GET /api/composer-api.bx/_action/summary
   — Summary данные сессии

✅ POST /api/composer-api.bx/widget/json/v2?widgetStateId=...
   — Загрузка отдельных виджетов

✅ POST /api/composer-api.bx/_action/v2/getSearchTapTags
   — Поисковые теги

✅ POST /api/composer-api.bx/_action/v2/shellHorizontalMenuGetChildV1
   — Данные меню
```

### Antibot механизм:
1. Первый запрос возвращает 403
2. Загружается `/abt/result` (antibot challenge)
3. После прохождения — редирект с `?abt_att=1`
4. Далее API работают нормально

### Вывод:
**Модели были правы!** Для обхода антибота нужен:
- Headless browser с stealth-плагином
- Или резидентные прокси с ротацией
- Cookies после прохождения challenge обязательны
