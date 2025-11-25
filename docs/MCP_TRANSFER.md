# Перенос MCP инфраструктуры в другой проект

> **Для агента:** Этот документ описывает как перенести полную MCP-инфраструктуру (Perplexity, Playwright, GitHub, etc.) в новый проект.

## Быстрый чеклист

```
□ Скопировать slash commands → ~/.claude/commands/
□ Смержить settings.json → ~/.claude/settings.json
□ Скопировать .mcp.json.example → новый_проект/.mcp.json
□ Заполнить API ключи в .mcp.json
□ Добавить .mcp.json в .gitignore
□ Перезапустить Claude Code
```

---

## 1. Slash Commands (копировать в ~/.claude/commands/)

### Исходная директория:
```
~/.claude/commands/
```

### Файлы для копирования:
| Файл | Назначение | Модель |
|------|-----------|--------|
| `architect.md` | Проектирование архитектуры | GPT-5.1 |
| `audit.md` | Аудит кода/архитектуры | Claude Opus 4.5 |
| `frontend.md` | UI компоненты | Gemini 3 Pro |
| `trends.md` | Актуальная информация | Grok 4.1 |
| `deep-analyze.md` | Глубокий анализ | Kimi K2 |
| `deep-research.md` | Deep Research | Perplexity Research |
| `ask-gpt5.md` | Запрос к GPT-5.1 | GPT-5.1 |
| `ask-claude-perplexity.md` | Запрос к Claude | Claude Sonnet |
| `ask-space.md` | Perplexity Space | Любая |
| `ask-with-files.md` | С файлами проекта | Любая |
| `perplexity-search.md` | Быстрый поиск | Sonar |

### Команда копирования:
```bash
# Все команды уже в ~/.claude/commands/ — они глобальные!
# Если нужно скопировать в другую систему:
scp -r ~/.claude/commands/ user@host:~/.claude/
```

---

## 2. Settings (смержить с ~/.claude/settings.json)

### Критичные permissions для MCP:
```json
{
  "permissions": {
    "allow": [
      "mcp__sequential-thinking",
      "mcp__perplexity",
      "mcp__memory",
      "mcp__playwright-global__browser_navigate",
      "mcp__playwright-global__browser_snapshot",
      "mcp__playwright-global__browser_click",
      "mcp__playwright-global__browser_type",
      "mcp__playwright-global__browser_press_key",
      "mcp__playwright-global__browser_wait_for",
      "mcp__playwright-global__browser_close",
      "mcp__playwright-global__browser_tabs",
      "mcp__playwright-global__browser_resize",
      "mcp__playwright-global__browser_hover",
      "mcp__playwright-global__browser_select_option",
      "mcp__playwright-global__browser_handle_dialog",
      "mcp__playwright-global__browser_file_upload",
      "mcp__playwright-global__browser_evaluate"
    ]
  }
}
```

### Как смержить:
```bash
# Открыть существующий settings.json
code ~/.claude/settings.json

# Добавить permissions.allow из списка выше
# НЕ заменять весь файл — только добавить в массив allow!
```

---

## 3. MCP конфиг (создать в корне проекта)

### Шаблон `.mcp.json.example`:
```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "YOUR_PERPLEXITY_API_KEY",
        "PERPLEXITY_TIMEOUT_MS": "600000"
      }
    },
    "github-new": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./research/memory.json"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}
```

### Настройка:
```bash
# 1. Скопировать шаблон
cp .mcp.json.example .mcp.json

# 2. Заполнить API ключи
# - PERPLEXITY_API_KEY: https://www.perplexity.ai/settings/api
# - GITHUB_PERSONAL_ACCESS_TOKEN: https://github.com/settings/tokens

# 3. Добавить в .gitignore
echo ".mcp.json" >> .gitignore
```

---

## 4. Необходимые API ключи

| Сервис | Где получить | Цена |
|--------|-------------|------|
| Perplexity API | perplexity.ai/settings/api | Pro $20/мес (500 запросов/день) |
| GitHub PAT | github.com/settings/tokens | Бесплатно |
| Playwright | — | Бесплатно (browser automation) |

---

## 5. Проверка работоспособности

### После настройки:
```bash
# 1. Перезапустить Claude Code
# Ctrl+Shift+P → "Claude: Restart"

# 2. Проверить MCP серверы
# В Claude Code: /mcp

# 3. Тест Perplexity API
/perplexity-search что такое MCP?

# 4. Тест Playwright
/ask-gpt5 Привет, скажи ОК
```

### Ожидаемый результат:
- ✅ MCP серверы отображаются в списке
- ✅ Perplexity отвечает на запросы
- ✅ Playwright открывает браузер и взаимодействует с Perplexity.ai

---

## 6. Полная команда для нового проекта

```bash
# Создать новый проект с MCP
mkdir my-new-project && cd my-new-project

# Скопировать MCP конфиг
cp /путь/к/google_gemini_vpn/.mcp.json.example ./.mcp.json.example
cp .mcp.json.example .mcp.json

# Настроить gitignore
echo ".mcp.json" >> .gitignore

# Заполнить ключи в .mcp.json
# (вручную или через sed)

# Slash commands уже глобальные в ~/.claude/commands/
# Settings уже глобальные в ~/.claude/settings.json

# Запустить Claude Code
claude
```

---

## Документация

- [AI_WORKFLOW.md](AI_WORKFLOW.md) — Мульти-модельный workflow
- [PERPLEXITY_PLAYWRIGHT_MCP.md](PERPLEXITY_PLAYWRIGHT_MCP.md) — Playwright MCP для Perplexity Pro
