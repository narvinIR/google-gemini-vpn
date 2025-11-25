#!/bin/bash

PROFILE_38="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/profiles/38.json"
PROFILE_39="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/profiles/39.json"
NEKOBOX_CONFIG="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/groups/nekobox.json"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Статус NekoBox VPN ===${NC}\n"

if [[ ! -f "$NEKOBOX_CONFIG" ]]; then
  echo -e "${RED}Ошибка: Конфиг NekoBox не найден${NC}"
  exit 1
fi

ACTIVE_ID=$(grep -oP '"remember_id":\s*\K\d+' "$NEKOBOX_CONFIG")

if [[ "$ACTIVE_ID" == "38" ]]; then
  ACTIVE_PROFILE="$PROFILE_38"
  echo -e "${GREEN}✓ Активный сервер: Tallinn (Профиль 38)${NC}"
elif [[ "$ACTIVE_ID" == "39" ]]; then
  ACTIVE_PROFILE="$PROFILE_39"
  echo -e "${YELLOW}⚠ Активный сервер: Профиль 39${NC}"
else
  echo -e "${RED}✗ Не удалось определить активный сервер${NC}"
  exit 1
fi

SERVER_IP=$(grep -oP '"addr":\s*"\K[^"]+' "$ACTIVE_PROFILE")
SERVER_PORT=$(grep -oP '"port":\s*\K\d+' "$ACTIVE_PROFILE")
SERVER_NAME=$(grep -oP '"name":\s*"\K[^"]+' "$ACTIVE_PROFILE")

echo -e "  IP: ${BLUE}$SERVER_IP${NC}"
echo -e "  Port: ${BLUE}$SERVER_PORT${NC}"
echo -e "  Name: ${BLUE}$SERVER_NAME${NC}\n"

DL=$(grep -oP '"dl":\s*\K\d+' "$ACTIVE_PROFILE")
UL=$(grep -oP '"ul":\s*\K\d+' "$ACTIVE_PROFILE")

DL_GB=$(echo "scale=2; $DL / 1073741824" | bc)
UL_GB=$(echo "scale=2; $UL / 1073741824" | bc)

echo -e "${BLUE}=== Трафик ===${NC}"
echo -e "  Download: ${GREEN}${DL_GB} GB${NC}"
echo -e "  Upload: ${GREEN}${UL_GB} GB${NC}\n"

FAKEDNS=$(grep -oP '"fakedns":\s*\K\w+' "$NEKOBOX_CONFIG")
VPN_MODE=$(grep -oP '"spmode2":\s*\[\s*"\K[^"]+' "$NEKOBOX_CONFIG")

echo -e "${BLUE}=== Настройки ===${NC}"
if [[ "$FAKEDNS" == "true" ]]; then
  echo -e "  FakeDNS: ${GREEN}✓ Включен${NC}"
else
  echo -e "  FakeDNS: ${RED}✗ Выключен${NC}"
fi
echo -e "  Режим: ${BLUE}$VPN_MODE${NC}\n"

echo -e "${YELLOW}Для мониторинга логов: ./scripts/monitor-logs.sh${NC}"
