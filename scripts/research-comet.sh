#!/bin/bash

# Запуск Perplexity Comet Browser для глубокого исследования
# Использование: ./research-comet.sh "тема исследования"

TOPIC="$1"

# TODO: Обновить путь после поиска
COMET_PATH=""

# Попытка найти Comet автоматически
if [ -z "$COMET_PATH" ]; then
  echo "🔍 Поиск Perplexity Comet Browser..."

  # Поиск в типичных местах Windows
  SEARCH_PATHS=(
    "/mnt/c/Program Files/Perplexity"
    "/mnt/c/Program Files (x86)/Perplexity"
    "/mnt/c/Users/Пользователь/AppData/Local/Perplexity"
    "/mnt/c/Users/Пользователь/AppData/Local/Programs/Perplexity"
  )

  for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
      FOUND=$(find "$path" -name "*.exe" -iname "*comet*" -o -name "*.exe" -iname "*perplexity*" 2>/dev/null | head -1)
      if [ ! -z "$FOUND" ]; then
        COMET_PATH="$FOUND"
        echo "✅ Найдено: $COMET_PATH"
        break
      fi
    fi
  done
fi

if [ -z "$COMET_PATH" ]; then
  echo "❌ Comet Browser не найден."
  echo ""
  echo "Установите Comet Browser:"
  echo "1. Откройте https://www.perplexity.ai/hub/blog/introducing-comet"
  echo "2. Скачайте и установите"
  echo "3. Обновите путь в этом скрипте"
  echo ""
  echo "Или используйте веб-версию: https://www.perplexity.ai/comet"
  exit 1
fi

if [ -z "$TOPIC" ]; then
  echo "Использование: ./research-comet.sh 'тема исследования'"
  echo ""
  echo "Примеры:"
  echo "  ./research-comet.sh 'Gemini 3 Pro API архитектура и лимиты'"
  echo "  ./research-comet.sh 'VPN обход Google региональных блокировок'"
  exit 1
fi

echo "🚀 Запуск Comet Browser..."
echo "📋 Тема: $TOPIC"
echo ""

# Запуск Comet с темой (если поддерживается CLI)
powershell.exe -Command "Start-Process '$COMET_PATH'"

echo "✅ Comet Browser запущен"
echo ""
echo "📝 Инструкции:"
echo "1. В Comet введите запрос: $TOPIC"
echo "2. Дождитесь завершения исследования (5-15 мин)"
echo "3. Нажмите 'Export' → выберите Markdown"
echo "4. Сохраните в: $(pwd)/research/comet-exports/"
echo ""
echo "📁 После экспорта результаты будут доступны в Claude Code"
