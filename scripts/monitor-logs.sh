#!/bin/bash

NEKOBOX_LOG="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/neko.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Мониторинг NekoBox (Tallinn 89.169.15.11) ===${NC}"
echo -e "${YELLOW}Фильтры: ERROR, WARN, google, gemini, anthropic${NC}"
echo -e "${YELLOW}Ctrl+C для выхода${NC}"
echo ""

if [[ ! -f "$NEKOBOX_LOG" ]]; then
  echo -e "${RED}Ошибка: Лог файл не найден: $NEKOBOX_LOG${NC}"
  echo "Проверьте путь к NekoBox"
  exit 1
fi

tail -f "$NEKOBOX_LOG" | grep --line-buffered -iE "ERROR|WARN|google|gemini|anthropic|fail|timeout" | while read line; do
  timestamp=$(date '+%H:%M:%S')

  if echo "$line" | grep -qi "error"; then
    echo -e "${RED}[$timestamp]${NC} $line"
  elif echo "$line" | grep -qi "warn"; then
    echo -e "${YELLOW}[$timestamp]${NC} $line"
  elif echo "$line" | grep -qi "google\|gemini"; then
    echo -e "${GREEN}[$timestamp]${NC} $line"
  else
    echo -e "[$timestamp] $line"
  fi
done
