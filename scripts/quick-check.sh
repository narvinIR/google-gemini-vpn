#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

NEKOBOX_CONFIG="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/groups/nekobox.json"
PROFILE_38="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/profiles/38.json"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Проверка готовности для Google Gemini    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}\n"

ALL_OK=true

echo -e "${YELLOW}[1/5]${NC} Проверка NekoBox..."
if [[ -f "$NEKOBOX_CONFIG" ]]; then
  ACTIVE_ID=$(grep -oP '"remember_id":\s*\K\d+' "$NEKOBOX_CONFIG")
  if [[ "$ACTIVE_ID" == "38" ]]; then
    echo -e "      ${GREEN}✓ NekoBox активен (Tallinn)${NC}"
  else
    echo -e "      ${YELLOW}⚠ Активен профиль $ACTIVE_ID (не Tallinn)${NC}"
    ALL_OK=false
  fi
else
  echo -e "      ${RED}✗ NekoBox не найден${NC}"
  ALL_OK=false
fi

echo -e "\n${YELLOW}[2/5]${NC} Проверка DNS..."
ROUTING_CONFIG="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/routes_box/Default"
if [[ -f "$ROUTING_CONFIG" ]]; then
  USE_DNS_OBJECT=$(grep -oP '"use_dns_object":\s*\K\w+' "$ROUTING_CONFIG")
  if [[ "$USE_DNS_OBJECT" == "true" ]]; then
    echo -e "      ${GREEN}✓ DNS объект активирован${NC}"
  else
    echo -e "      ${RED}✗ DNS объект НЕ активирован (use_dns_object: false)${NC}"
    echo -e "      ${YELLOW}  Решение: ./scripts/apply-dns-config.sh${NC}"
    ALL_OK=false
  fi
else
  echo -e "      ${RED}✗ Конфиг маршрутизации не найден${NC}"
  ALL_OK=false
fi

echo -e "\n${YELLOW}[3/5]${NC} Проверка FakeDNS..."
FAKEDNS=$(grep -oP '"fakedns":\s*\K\w+' "$NEKOBOX_CONFIG" 2>/dev/null)
if [[ "$FAKEDNS" == "true" ]]; then
  echo -e "      ${GREEN}✓ FakeDNS включен${NC}"
else
  echo -e "      ${RED}✗ FakeDNS выключен${NC}"
  ALL_OK=false
fi

echo -e "\n${YELLOW}[4/5]${NC} Проверка локали браузера..."
echo -e "      ${YELLOW}⚠ Требуется ручная проверка:${NC}"
echo -e "      ${BLUE}1. Запустить: ./gemini-browser.sh (или .bat)${NC}"
echo -e "      ${BLUE}2. Открыть: chrome://settings/languages${NC}"
echo -e "      ${BLUE}3. Удалить русский язык полностью${NC}"
echo -e "      ${BLUE}4. Проверить: https://ipleak.net → Language: en-US${NC}"

echo -e "\n${YELLOW}[5/5]${NC} Проверка Google аккаунта..."
echo -e "      ${YELLOW}⚠ Требуется новый аккаунт:${NC}"
echo -e "      ${BLUE}1. VPN ON + изолированный Chrome${NC}"
echo -e "      ${BLUE}2. https://accounts.google.com/signup${NC}"
echo -e "      ${BLUE}3. Country: Estonia, Email: proton.me${NC}"

echo -e "\n${BLUE}╔════════════════════════════════════════════╗${NC}"
if [[ "$ALL_OK" == true ]]; then
  echo -e "${BLUE}║${NC}  ${GREEN}✓ Система готова к запуску Gemini${NC}       ${BLUE}║${NC}"
  echo -e "${BLUE}║${NC}  ${YELLOW}Запустить: ./gemini-browser.sh${NC}          ${BLUE}║${NC}"
else
  echo -e "${BLUE}║${NC}  ${RED}✗ Требуется настройка${NC}                   ${BLUE}║${NC}"
  echo -e "${BLUE}║${NC}  ${YELLOW}См. инструкции выше${NC}                    ${BLUE}║${NC}"
fi
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}Дополнительные команды:${NC}"
echo -e "  ${BLUE}./scripts/vpn-status.sh${NC}      - Статус VPN"
echo -e "  ${BLUE}./scripts/monitor-logs.sh${NC}    - Логи в реальном времени"
echo -e "  ${BLUE}./check-leaks.bat${NC}            - Проверка утечек (Windows)"
