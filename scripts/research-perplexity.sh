#!/bin/bash

# Быстрое исследование через Perplexity API
# Использование: ./research-perplexity.sh "тема исследования"

TOPIC="$1"
API_KEY="${PERPLEXITY_API_KEY:-YOUR_PERPLEXITY_API_KEY}"

if [ -z "$TOPIC" ]; then
  echo "Использование: ./research-perplexity.sh 'тема исследования'"
  exit 1
fi

echo "🔍 Исследование через Perplexity API: $TOPIC"
echo ""

# Вызов Perplexity API
RESPONSE=$(curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{
    \"model\": \"sonar\",
    \"messages\": [
      {
        \"role\": \"system\",
        \"content\": \"Ты исследователь. Проводи глубокий анализ с цитированием источников.\"
      },
      {
        \"role\": \"user\",
        \"content\": \"$TOPIC\"
      }
    ],
    \"temperature\": 0.2,
    \"max_tokens\": 4000,
    \"return_citations\": true,
    \"search_recency_filter\": \"month\"
  }")

# Сохранить результат
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="research/perplexity-${TIMESTAMP}.json"

mkdir -p research
echo "$RESPONSE" > "$OUTPUT_FILE"

# Извлечь текст ответа
ANSWER=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null)

if [ -z "$ANSWER" ] || [ "$ANSWER" == "null" ]; then
  echo "❌ Ошибка API:"
  echo "$RESPONSE" | jq '.'
  exit 1
fi

echo "✅ Результат:"
echo ""
echo "$ANSWER"
echo ""
echo "📁 Сохранено в: $OUTPUT_FILE"

# Извлечь источники
CITATIONS=$(echo "$RESPONSE" | jq -r '.citations[]?' 2>/dev/null)
if [ ! -z "$CITATIONS" ]; then
  echo ""
  echo "📚 Источники:"
  echo "$CITATIONS"
fi
