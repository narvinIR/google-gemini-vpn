#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

NEKOBOX_CONFIG="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/groups/nekobox.json"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Запуск изолированного Chrome для Gemini  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}[Проверка 1/2]${NC} VPN статус..."
if [[ -f "$NEKOBOX_CONFIG" ]]; then
  ACTIVE_ID=$(grep -oP '"remember_id":\s*\K\d+' "$NEKOBOX_CONFIG")
  if [[ "$ACTIVE_ID" == "38" || "$ACTIVE_ID" == "39" ]]; then
    echo -e "              ${GREEN}✓ NekoBox активен${NC}"
  else
    echo -e "              ${RED}✗ NekoBox не подключен${NC}"
    echo -e "              ${YELLOW}Запустите NekoBox и попробуйте снова${NC}\n"
    exit 1
  fi
else
  echo -e "              ${YELLOW}⚠ NekoBox не найден, продолжаем...${NC}"
fi

echo -e "\n${YELLOW}[Проверка 2/2]${NC} Локаль..."
export LANG=en_US.UTF-8
export LANGUAGE=en_US
export LC_ALL=en_US.UTF-8
echo -e "              ${GREEN}✓ Установлена en_US${NC}\n"

PROFILE_DIR="$HOME/.chrome-gemini"

echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${GREEN}Запуск Chromium...${NC}\n"

chromium-browser \
  --user-data-dir="$PROFILE_DIR" \
  --lang=en-US \
  --accept-lang=en-US,en;q=0.9 \
  --disable-features=WebRtcHideLocalIpsWithMdns \
  --webrtc-ip-handling-policy=disable_non_proxied_udp \
  --no-first-run \
  --disable-background-timer-throttling \
  https://aistudio.google.com &

sleep 2

echo -e "${YELLOW}╔════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║          ВАЖНО: Действия в браузере        ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}1. chrome://settings/languages${NC}"
echo -e "   ${RED}→ Удалить русский язык ПОЛНОСТЬЮ${NC}"
echo -e "   ${GREEN}→ Оставить только English (United States)${NC}\n"

echo -e "${BLUE}2. chrome://settings/clearBrowserData${NC}"
echo -e "   ${RED}→ Time range: All time${NC}"
echo -e "   ${GREEN}→ Cookies, Cache, Site settings ✓${NC}\n"

echo -e "${BLUE}3. Проверка: https://ipleak.net${NC}"
echo -e "   ${GREEN}→ Language: en-US, en;q=0.9 (БЕЗ ru!)${NC}\n"

echo -e "${YELLOW}Для полной диагностики: ./scripts/quick-check.sh${NC}"