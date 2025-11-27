# Деплой Ozon Parser на Northflank

## Шаг 1: Google Service Account

1. Перейди: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Создай проект или выбери существующий
3. **Create Service Account**:
   - Name: `ozon-parser`
   - Role: `Editor` (или просто "Basic > Editor")
4. **Keys** → Add Key → Create new key → JSON → Download
5. Сохрани JSON (не коммить!)

### Выдать доступ к таблице:

1. Открой скачанный JSON
2. Найди `client_email` (например: `ozon-parser@my-project.iam.gserviceaccount.com`)
3. Открой Google Sheet: https://docs.google.com/spreadsheets/d/1la2mK1DpL6KvnQ5t4oRDvUietTMhgS2ZWfNnS1H4EgQ
4. **Share** → вставь `client_email` → Editor → Share

## Шаг 2: Деплой на Northflank

### Вариант A: Через Web UI

1. https://app.northflank.com → New Service
2. **Source**: Git → подключи репозиторий `google_gemini_vpn`
3. **Build**:
   - Context: `/` (корень)
   - Dockerfile path: `Dockerfile`
4. **Resources**:
   - vCPU: 1
   - Memory: 1024 MB
5. **Networking**:
   - Port: 8000
   - Public: Yes
6. **Environment Variables**:
   ```
   GOOGLE_CREDENTIALS_JSON=<весь JSON из service account одной строкой>
   PARSER_DELAY=2.5
   LOG_LEVEL=INFO
   ```

### Вариант B: Через CLI

```bash
# Установи Northflank CLI
npm install -g @northflank/cli

# Логин
northflank login

# Деплой
northflank apply -f northflank.json
```

## Шаг 3: Apps Script в Google Sheets

1. Открой таблицу: https://docs.google.com/spreadsheets/d/1la2mK1DpL6KvnQ5t4oRDvUietTMhgS2ZWfNnS1H4EgQ
2. **Расширения** → **Apps Script**
3. Скопируй код из `scripts/apps_script.js`
4. **Обнови URL** на строке 13:
   ```javascript
   const API_URL = "https://ozon-parser-api--<твой-проект>.code.run";
   ```
   URL найдёшь в Northflank после деплоя.
5. Сохрани (Ctrl+S)
6. Закрой Apps Script
7. Перезагрузи таблицу

## Шаг 4: Тестирование

1. В таблице появится меню **🔍 Ozon Parser**
2. Добавь SKU в колонку A (например: `2047250383`)
3. **🔍 Ozon Parser** → **▶️ Запустить парсинг**
4. Результаты появятся в колонках B-I

## Проверка работы API

```bash
# Health check
curl https://ozon-parser-api--<project>.code.run/api/health

# Тест одного SKU
curl -X POST "https://ozon-parser-api--<project>.code.run/api/parse/test?sku=2047250383"
```

## Troubleshooting

**"Permission denied" в логах:**
- Проверь что Service Account имеет доступ к таблице (Share → Editor)

**Antibot блокирует:**
- Ozon иногда блокирует VPS IP. Решения:
  1. Добавить прокси
  2. Увеличить PARSER_DELAY до 5 секунд
  3. Использовать residential proxy

**"No SKUs found":**
- Проверь что SKU в колонке A, начиная со 2 строки
- Первая строка - заголовки
