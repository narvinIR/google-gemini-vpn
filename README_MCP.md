# MCP Серверы - Руководство по использованию

## Установленные MCP серверы

### 1. **Perplexity MCP** (jaacob/perplexity-mcp)
**Назначение:** API доступ к Perplexity с поддержкой моделей sonar, sonar-pro, sonar-reasoning

**Использование:**
```
Я могу использовать: @perplexity для быстрых запросов
Пример: "Найди через Perplexity последние новости по Gemini 3 Pro"
```

**Модели:**
- `sonar` - базовая (быстрая)
- `sonar-pro` - продвинутая (текущая, установлена по умолчанию)
- `sonar-reasoning` - с рассуждениями

**Лимиты Pro подписки:**
- 500 запросов/день (sonar online)
- Безлимит (sonar turbo, 100 req/min)

---

### 2. **GitHub MCP** (@modelcontextprotocol/server-github)
**Назначение:** Работа с GitHub репозиториями, issues, pull requests

**Использование:**
```
Я могу:
- Читать файлы из репозиториев
- Создавать/обновлять issues
- Работать с PR
- Искать код

Пример: "Найди в GitHub репозитории jaacob/perplexity-mcp файл README"
```

---

### 3. **Playwright MCP** (@playwright/mcp)
**Назначение:** Автоматизация браузера для глубоких исследований

**Использование:**
```
Для автоматизации Comet Browser:
1. Запускает /mnt/c/.../Comet/Application/comet.exe
2. Автоматизирует исследование
3. Извлекает результаты

Пример: "Используй Playwright для запуска Comet и исследования темы X"
```

**Путь к Comet:** `/mnt/c/Users/Пользователь/AppData/Local/Perplexity/Comet/Application/comet.exe`

---

### 4. **Sequential Thinking MCP**
**Назначение:** Сложные рассуждения и анализ

**Использование:**
```
Автоматически для сложных задач с цепочкой рассуждений
```

---

### 5. **Memory MCP**
**Назначение:** Сохранение контекста между сессиями

**Файл:** `./research/research_memory.json`

---

### 6. **Filesystem MCP**
**Назначение:** Доступ к файлам проекта

**Корень:** `/home/dimas/projects/google_gemini_vpn`

---

## Workflow для больших исследований

### Сценарий 1: Быстрый факт-чекинг
```
Пользователь: "Проверь актуальность информации по Gemini 3 Pro"
Claude Code: → использует Perplexity MCP
Результат: через 5-10 секунд
```

### Сценарий 2: Глубокое исследование
```
Пользователь: "Проведи глубокое исследование конкурентов Gemini"
Claude Code:
  1. Perplexity MCP → список конкурентов (30 сек)
  2. Playwright MCP → запуск Comet (15 мин глубокий анализ каждого)
  3. Memory MCP → сохранение результатов
```

### Сценарий 3: Работа с кодом
```
Пользователь: "Изучи архитектуру jaacob/perplexity-mcp"
Claude Code:
  1. GitHub MCP → клонирование репозитория
  2. Filesystem MCP → анализ файлов
  3. Sequential Thinking → синтез архитектуры
```

---

## Команды

### Проверка конфигурации
```bash
# Проверить .mcp.json
cat .mcp.json

# Проверить установку Perplexity MCP
ls -la mcp-servers/perplexity-mcp/build/index.js

# Проверить путь к Comet
ls "/mnt/c/Users/Пользователь/AppData/Local/Perplexity/Comet/Application/comet.exe"
```

### Переустановка Perplexity MCP
```bash
cd mcp-servers/perplexity-mcp
npm install
npm run build
```

### Обновление GitHub токена
```bash
# Обновить в .mcp.json:
# "GITHUB_PERSONAL_ACCESS_TOKEN": "новый_токен"
```

---

## Troubleshooting

### Perplexity MCP не отвечает
```bash
# Проверить сборку
cd mcp-servers/perplexity-mcp
npm run build

# Проверить API ключ
echo $PERPLEXITY_API_KEY
```

### GitHub MCP ошибка авторизации
```bash
# Проверить токен (должен иметь scope: repo, read:org)
# Создать новый: https://github.com/settings/tokens
```

### Playwright не находит Comet
```bash
# Обновить путь к comet.exe в .mcp.json
find /mnt/c/Users/Пользователь -name "comet.exe" 2>/dev/null
```

---

## Лимиты и оптимизация

### Бесплатно (безлимит)
- Sequential Thinking
- Memory
- Filesystem
- GitHub MCP
- Playwright MCP (локальная автоматизация)

### Платно (Perplexity Pro подписка)
- Perplexity MCP: 500 запросов/день (sonar online)
- Альтернатива: Playwright + Comet (безлимит, но медленнее)

### Рекомендации
1. **Быстрые факты** → Perplexity MCP (5-10 сек)
2. **Глубокий анализ** → Playwright + Comet (5-15 мин)
3. **Работа с кодом** → GitHub MCP + Filesystem
4. **Сложные рассуждения** → Sequential Thinking (без веб-поиска)

---

## Примеры использования

### Пример 1: Исследование технологии
```
Пользователь: "Изучи архитектуру Gemini 3 Pro и сравни с Claude 3.5"

Claude Code:
1. @perplexity → обзор Gemini 3 Pro (30 сек)
2. @perplexity → обзор Claude 3.5 (30 сек)
3. @sequential-thinking → сравнительный анализ
4. @memory → сохранение результатов
```

### Пример 2: Анализ репозитория
```
Пользователь: "Изучи код jaacob/perplexity-mcp и объясни архитектуру"

Claude Code:
1. @github → чтение README
2. @github → анализ package.json
3. @github → изучение src/index.ts
4. @sequential-thinking → объяснение архитектуры
```

### Пример 3: Глубокое исследование + код
```
Пользователь: "Найди лучшие практики VPN для обхода блокировок и реализуй"

Claude Code:
1. @playwright → Comet глубокое исследование (10 мин)
2. @memory → сохранение результатов
3. @filesystem → чтение текущего кода
4. @github → поиск примеров в репозиториях
5. Реализация кода с учетом найденных практик
```

---

## Структура проекта

```
google_gemini_vpn/
├── .mcp.json                    # Конфигурация MCP серверов
├── mcp-servers/
│   └── perplexity-mcp/          # Локальный Perplexity MCP
│       ├── build/index.js       # Собранный сервер
│       └── package.json
├── research/
│   ├── research_memory.json     # Memory MCP хранилище
│   ├── comet-exports/           # Экспорты из Comet
│   └── perplexity-cache/        # Кеш Perplexity
├── scripts/
│   ├── research-perplexity.sh   # Прямой вызов API
│   └── research-comet.sh        # Запуск Comet вручную
└── docs/
    ├── PERPLEXITY_INTEGRATION.md
    └── README_MCP.md            # Этот файл
```

---

## Обновление

### Perplexity MCP
```bash
cd mcp-servers/perplexity-mcp
git pull
npm install
npm run build
```

### Другие MCP серверы (через npx)
```bash
# Автоматически используют latest версию
# Обновление при каждом запуске
```
