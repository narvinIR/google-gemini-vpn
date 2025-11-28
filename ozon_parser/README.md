# Ozon Competitor Parser

Автоматический парсинг цен конкурентов с Ozon по списку SKU.

## ВАЖНО: Где запускать

**Ozon блокирует VPS/датацентры!** Парсер работает только:
- На **домашнем ПК** (Windows/Linux с дисплеем)
- С **residential proxy** ($30+/месяц)

## Быстрый старт (Windows)

### 1. Установка
```cmd
pip install playwright playwright-stealth gspread google-auth
playwright install chromium
```

### 2. Запуск
```cmd
run_parser.bat
```

Или напрямую:
```cmd
python auto_parser.py --limit 5   # Тест (5 SKU)
python auto_parser.py              # Все SKU из Google Sheets
```

## Конфигурация по умолчанию

| Параметр | Значение |
|----------|----------|
| Google Sheets | `1la2mK1DpL6KvnQ5t4oRDvUietTMhgS2ZWfNnS1H4EgQ` |
| Лист | "Парсинг товаров" |
| Credentials | `../credentials/service-account.json` |

## Параметры командной строки

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--csv` | CSV файл со SKU | - |
| `--output`, `-o` | Выходной CSV | results.csv |
| `--sheet` | ID Google Sheets | (конфиг) |
| `--creds` | Файл credentials | (конфиг) |
| `--headless` | Фоновый режим | False |
| `--delay` | Задержка между запросами | 2.5 сек |
| `--limit` | Ограничить кол-во SKU | 0 (все) |
| `--skus` | SKU через пробел | - |

## Примеры использования

```bash
# Из Google Sheets (по умолчанию)
python auto_parser.py

# Первые 10 SKU
python auto_parser.py --limit 10

# Конкретные SKU
python auto_parser.py --skus 2047250383 1852645518

# Из CSV файла
python auto_parser.py --csv input.csv --output results.csv

# Другая таблица Google Sheets
python auto_parser.py --sheet "1abc...xyz"
```

## Структура данных

**Входные данные (колонка A):**
```
SKU
2047250383
1852645518
```

**Выходные данные (колонки B-I):**
| B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|
| Name | Price | Brand | Rating | Reviews | Availability | Date | Error |

## Как работает

```
1. Читает SKU из Google Sheets (колонка A)
2. Открывает браузер с сохранённым профилем
3. Для каждого SKU:
   - Переходит на ozon.ru/product/{SKU}/
   - Ждёт загрузку + случайная задержка
   - Извлекает JSON-LD Schema (SEO разметка)
4. Записывает результаты в Google Sheets (колонки B-I)
```

## Защита от бана

| Рекомендация | Значение |
|--------------|----------|
| Задержка между запросами | 2.5-4 сек |
| Максимум за сессию | 100-200 SKU |
| Перерыв между сессиями | 10-30 мин |
| Время парсинга 100 SKU | ~8-10 мин |

**Встроенные механизмы:**
- playwright-stealth для маскировки автоматизации
- Случайные задержки между запросами
- Сохранённый профиль браузера (обходит повторный антибот)
- Русская локаль и московский часовой пояс

## Troubleshooting

**"JSON-LD not found"**
- Ozon заблокировал - перезапусти БЕЗ `--headless`
- Пройди антибот вручную один раз

**Браузер не открывается**
- Установи Chromium: `playwright install chromium`

**Google Sheets не работает**
- Проверь credentials файл
- Убедись что сервисный аккаунт имеет доступ к таблице
