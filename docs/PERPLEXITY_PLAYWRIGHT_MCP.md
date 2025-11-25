# Playwright MCP для Perplexity Pro

Автоматизация доступа к моделям Perplexity Pro (GPT-5.1, Claude, Gemini, Grok, Kimi K2) через Playwright MCP.

## Что это?

Playwright MCP позволяет Claude Code автоматизировать браузер для работы с Perplexity.ai. Это даёт доступ ко **всем моделям Pro подписки**, которые недоступны через API.

## Доступные модели

| Модель | Описание | Скорость |
|--------|----------|----------|
| **Sonar** | Базовый поиск Perplexity | Быстрый |
| **GPT-5.1** | OpenAI, отлично для кода | Средний |
| **Claude Sonnet 4.5** | Anthropic, баланс качества | Средний |
| **Gemini 3 Pro** | Google, новая модель | Средний |
| **Grok 4.1** | xAI, свежие данные | Средний |
| **Kimi K2 Thinking** | Reasoning модель | Медленный |
| **Claude Opus 4.5** | Топ модель Anthropic (Max) | Медленный |
| **o3-pro** | OpenAI reasoning (Max) | Очень медленный |

## Установка

### 1. MCP сервер (уже установлен глобально)

```bash
claude mcp add playwright-global -s user -- npx @playwright/mcp@latest --user-data-dir ~/.mcp/perplexity-profile
```

### 2. Разрешения (без подтверждений)

В `~/.claude/settings.json` добавлено:
```json
"mcp__playwright-global"
```

### 3. Первичная авторизация

При первом использовании:
1. Попросить Claude: "Открой perplexity.ai"
2. В браузере залогиниться в Perplexity Pro
3. Cookies сохранятся автоматически

## Slash Commands

Созданы глобальные команды в `~/.claude/commands/`:

| Команда | Описание |
|---------|----------|
| `/perplexity-search` | Поиск с текущей моделью |
| `/ask-gpt5` | Вопрос к GPT-5.1 |
| `/ask-claude-perplexity` | Вопрос к Claude Sonnet 4.5 |
| `/ask-space` | **Запрос в Space с контекстом файлов** |
| `/ask-with-files` | Запрос с локальными файлами |
| `/deep-research` | Глубокое исследование (Research mode) |

## Perplexity Spaces (Projects)

Spaces — это проекты в Perplexity с постоянным контекстом (как Projects в Claude Desktop).

### Возможности Space:
- **Files** — загрузка файлов проекта (txt, pdf, код)
- **Instructions** — системные инструкции (как CLAUDE.md)
- **Links** — URL документации как источники
- **Threads** — история разговоров

### Использование Space:

```
/ask-space marketplaceai Как работает авторизация?
/ask-space unify-os gpt5 Объясни архитектуру
```

### Создание Space для проекта:
1. Открой https://www.perplexity.ai/spaces
2. Кликни "Create a Space"
3. Загрузи CLAUDE.md, README, ключевые файлы
4. Добавь инструкции в Instructions
5. Используй `/ask-space [имя] вопрос`

### Преимущества:
- Файлы загружены один раз
- Контекст сохраняется между сессиями
- Можно шарить с командой

## Использование

### Через slash commands

```
/perplexity-search Что такое квантовые вычисления?
/ask-gpt5 Напиши функцию сортировки на Python
/ask-claude-perplexity Объясни архитектуру микросервисов
/deep-research Анализ рынка AI стартапов в 2025
```

### Напрямую

```
Открой perplexity.ai, выбери модель Gemini 3 Pro и спроси: "Как работает transformer?"
```

### Программно через MCP инструменты

```
1. browser_navigate → https://www.perplexity.ai
2. browser_click → выбор модели
3. browser_type → ввод запроса
4. browser_press_key → Enter
5. browser_wait_for → ожидание ответа
6. browser_snapshot → извлечение результата
```

## Примеры

### Быстрый вопрос

```
Спроси GPT-5.1 через Perplexity: какой самый быстрый алгоритм сортировки?
```

### Сравнение моделей

```
Задай один вопрос разным моделям в Perplexity и сравни ответы:
- GPT-5.1
- Claude Sonnet 4.5
- Gemini 3 Pro
```

### Глубокое исследование

```
Проведи deep research через Perplexity на тему: "Тренды в AI инфраструктуре 2025"
```

## Troubleshooting

### Браузер не открывается

```bash
# Проверить MCP статус
claude mcp list | grep playwright
```

### Требуется повторная авторизация

```bash
# Очистить профиль и залогиниться заново
rm -rf ~/.mcp/perplexity-profile/*
```

### Модели недоступны (Pro Search disabled)

- Проверить что залогинен в Pro аккаунт
- Подождать 2-3 секунды после загрузки страницы

### Медленная работа

- Research mode занимает 2-10 минут
- Используй Sonar для быстрых запросов
- GPT-5.1 и Claude быстрее чем o3-pro

## Архитектура

```
Claude Code
    ↓
Playwright MCP (@playwright/mcp)
    ↓
Chromium Browser (persistent profile)
    ↓
Perplexity.ai (авторизован)
    ↓
GPT-5.1 / Claude / Gemini / Grok / etc.
```

## Преимущества

1. **Все модели Pro** — GPT-5.1, Claude, Gemini, Grok, Kimi K2, o3-pro
2. **Без API лимитов** — используешь свою подписку
3. **Deep Research** — полноценные исследования
4. **Портативность** — работает в любом проекте
5. **Автоматизация** — без ручных действий

## Ограничения

- Медленнее чем API (10-60 сек на запрос)
- Требует Pro подписку Perplexity
- Браузер должен быть виден (не headless)
