# GitHub Actions для парсинга Ozon

## Архитектура

```
GitHub Actions (2000 мин/мес бесплатно)
    ↓
Camoufox (anti-detect browser)
    ↓
Ozon.ru
    ↓
Supabase (competitor_prices таблица)
```

## Настройка

### 1. GitHub Secrets

Перейди в **Settings → Secrets and variables → Actions** и добавь:

| Secret | Описание | Где взять |
|--------|----------|-----------|
| `SUPABASE_URL` | URL проекта | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_KEY` | Service Role Key | Supabase Dashboard → Settings → API → service_role |
| `GOOGLE_SHEET_ID` | ID таблицы | URL таблицы: `/d/[ID]/` |
| `GOOGLE_SERVICE_ACCOUNT` | JSON credentials | Google Cloud Console |

### 2. Supabase URL

```
https://krxoilmjmcbqpuyzhwja.supabase.co
```

### 3. Таблица в Supabase

Уже создана автоматически:

```sql
CREATE TABLE competitor_prices (
  id uuid PRIMARY KEY,
  sku text UNIQUE,
  name text,
  price numeric(10,2),
  currency text DEFAULT 'RUB',
  brand text,
  rating numeric(3,2),
  reviews integer,
  availability text,
  parsed_at timestamptz,
  created_at timestamptz,
  updated_at timestamptz
);
```

## Запуск

### Автоматический (по расписанию)

Workflow запускается каждый день в 9:00 MSK (6:00 UTC).

### Ручной запуск

1. Перейди в **Actions → Parse Ozon Competitors**
2. Нажми **Run workflow**
3. Укажи параметры:
   - `limit` — ограничить количество SKU (0 = все)
   - `test_mode` — тестовый режим (не сохраняет в БД)

## Файлы

- `.github/workflows/parse-ozon.yml` — workflow definition
- `ozon_parser/github_actions_parser.py` — скрипт парсера

## Ограничения GitHub Actions

- **2000 минут/месяц** бесплатно (Linux runners)
- Один запуск ~5-10 минут для 100 SKU
- IP runner'а меняется каждый раз

## Если Ozon блокирует

GitHub Actions IP могут быть в базах датацентров. Если парсер показывает много `ANTIBOT_DETECTED`:

1. **Вариант A**: Использовать домашний ПК + Cloudflare Tunnel (см. `CLOUDFLARE_SETUP.md`)
2. **Вариант B**: Добавить residential proxy (Smartproxy, Bright Data)
3. **Вариант C**: Использовать Browserless.io (1000 бесплатных запросов)
