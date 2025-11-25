# Интеграция Perplexity Pro в Claude Code

## Архитектура

```
Claude Code (VS Code)
    ↓
┌─────────────────────────────────────┐
│  MCP Perplexity                     │  ← Быстрые запросы
│  (server-perplexity-ask)            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Perplexity API                     │  ← Pro подписка
│  (pplx-**_СКРЫТО_**)                │
└─────────────────────────────────────┘

Claude Code
    ↓
┌─────────────────────────────────────┐
│  Comet Browser                      │  ← Глубокие исследования
│  (автозапуск через скрипт)          │
└─────────────────────────────────────┘
```

## 1. MCP Perplexity (уже работает)

### Использование в Claude Code

Я могу вызывать Perplexity API напрямую:

```typescript
// Пример использования (внутри Claude Code)
mcp__perplexity__perplexity_ask({
  messages: [{
    role: "user",
    content: "Глубокий анализ архитектуры React 19"
  }]
})
```

### Возможности
- ✅ Веб-поиск в реальном времени
- ✅ Цитирование источников
- ✅ Быстрые ответы (< 10 сек)
- ❌ НЕ подходит для глубоких исследований (как в Comet)

## 2. Comet Browser для глубоких исследований

### Что такое Comet
Perplexity Comet - браузер для:
- Многоэтапные исследования
- Анализ 50+ источников
- Визуализация данных
- Экспорт результатов

### Автоматический запуск

Создан скрипт `scripts/research-comet.sh`:

```bash
#!/bin/bash
# Запуск Comet для исследования темы

TOPIC="$1"
COMET_PATH="/путь/к/comet.exe"  # TODO: найти путь

if [ -z "$TOPIC" ]; then
  echo "Использование: ./research-comet.sh 'тема исследования'"
  exit 1
fi

# Запуск Comet с темой
powershell.exe -Command "Start-Process '$COMET_PATH' -ArgumentList '--query','$TOPIC'"

echo "Comet запущен для темы: $TOPIC"
echo "После завершения исследования скопируйте результат в проект"
```

## 3. Workflow для больших исследований

### Сценарий 1: Быстрый поиск
```bash
# Через MCP Perplexity (автоматически в Claude Code)
Пример: "Найди последние новости по React 19"
→ Я использую mcp__perplexity__perplexity_ask
→ Результат через 5-10 сек
```

### Сценарий 2: Глубокое исследование
```bash
# Через Comet Browser
1. Запускаю: ./scripts/research-comet.sh "React 19 архитектура и breaking changes"
2. Comet проводит исследование (5-10 мин)
3. Экспорт результата в research/comet-export.md
4. Импорт в Claude Code для анализа
```

### Сценарий 3: Комбинированный
```bash
# 1. MCP Perplexity - быстрый обзор
# 2. Comet Browser - глубокий анализ
# 3. Claude Code - синтез и написание кода
```

## 4. Настройка .mcp.json для проекта

Файл `.mcp.json` в корне проекта:

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "server-perplexity-ask"],
      "env": {
        "PERPLEXITY_API_KEY": "**_СКРЫТО_**"
      }
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./research_memory.json"
      }
    }
  }
}
```

## 5. Лимиты Perplexity Pro

### API лимиты (Pro подписка)
- **Sonar Online** (с поиском):
  - 500 запросов/день
  - $5 за 1000 дополнительных запросов

- **Sonar Turbo** (быстрый):
  - Безлимит запросов
  - Ограничение: 100 req/min

### Как использовать максимально эффективно

1. **Частые запросы** → MCP Perplexity (автоматически в Claude Code)
2. **Глубокий анализ** → Comet Browser (ручной запуск)
3. **Сохранение контекста** → MCP Memory (автоматически)

## 6. Примеры команд в Claude Code

### Быстрый поиск
```
"Найди через Perplexity последние новости по Gemini 3 Pro API"
→ Я автоматически использую MCP Perplexity
```

### Глубокое исследование
```
"Проведи глубокое исследование архитектуры Gemini 3 Pro через Comet"
→ Я запускаю Comet Browser через скрипт
→ После завершения импортирую результаты
```

### Комбинированный подход
```
"Изучи конкурентов Gemini: сначала быстрый обзор через Perplexity,
затем глубокий анализ топ-3 через Comet"
→ Шаг 1: MCP Perplexity (список конкурентов)
→ Шаг 2: Comet Browser (глубокий анализ каждого)
→ Шаг 3: Синтез результатов
```

## 7. Экспорт результатов Comet

### Формат экспорта
Comet может экспортировать в:
- Markdown (.md)
- PDF
- JSON (структурированные данные)

### Автоматический импорт
```bash
# После экспорта из Comet
cp ~/Downloads/comet-research-*.md ./research/

# Claude Code автоматически прочитает
```

## 8. Хранение истории исследований

```
google_gemini_vpn/
├── research/
│   ├── comet-exports/          # Экспорты из Comet
│   ├── perplexity-cache/       # Кеш MCP Perplexity
│   └── research_memory.json    # MCP Memory
├── scripts/
│   ├── research-comet.sh       # Запуск Comet
│   └── import-research.sh      # Импорт результатов
└── .mcp.json                   # Конфигурация MCP
```

## 9. Оптимизация затрат

### Бесплатно
- ✅ MCP Sequential Thinking (рассуждения)
- ✅ MCP Memory (контекст)

### Платно (Perplexity Pro)
- ⚠️ MCP Perplexity API (500 запросов/день)
- ⚠️ Comet Browser (включен в Pro)

### Рекомендации
1. Использовать MCP Perplexity для быстрых фактов
2. Comet - только для глубоких исследований (1-2 раза в день)
3. Sequential Thinking - для сложных рассуждений БЕЗ веб-поиска

## 10. Troubleshooting

### MCP Perplexity не отвечает
```bash
# Проверить ключ API
echo $PERPLEXITY_API_KEY

# Переустановить сервер
npx -y server-perplexity-ask
```

### Comet не запускается
```bash
# Найти путь к установке
find /mnt/c/Users -name "*comet*.exe" 2>/dev/null

# Обновить путь в скрипте
vim scripts/research-comet.sh
```

### Превышен лимит API
```
Error: Rate limit exceeded (500/day)
→ Подождать до следующего дня
→ Или использовать Comet Browser (не считается в API лимит)
```
