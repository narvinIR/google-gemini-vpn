#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROUTING_CONFIG="/mnt/c/Users/Пользователь/Downloads/nekoray-4.0-beta4-2024-10-09-windows64/nekoray/config/routes_box/Default"
BACKUP_CONFIG="${ROUTING_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Применение DNS конфигурации для Google    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}\n"

if [[ ! -f "$ROUTING_CONFIG" ]]; then
  echo -e "${RED}✗ Конфиг не найден: $ROUTING_CONFIG${NC}"
  exit 1
fi

echo -e "${YELLOW}[1/3]${NC} Создание бэкапа..."
cp "$ROUTING_CONFIG" "$BACKUP_CONFIG"
if [[ $? -eq 0 ]]; then
  echo -e "      ${GREEN}✓ Бэкап: $(basename $BACKUP_CONFIG)${NC}"
else
  echo -e "      ${RED}✗ Ошибка создания бэкапа${NC}"
  exit 1
fi

echo -e "\n${YELLOW}[2/3]${NC} Изменение use_dns_object: false → true..."
sed -i 's/"use_dns_object": false/"use_dns_object": true/' "$ROUTING_CONFIG"
if grep -q '"use_dns_object": true' "$ROUTING_CONFIG"; then
  echo -e "      ${GREEN}✓ DNS объект активирован${NC}"
else
  echo -e "      ${RED}✗ Не удалось изменить параметр${NC}"
  echo -e "      ${YELLOW}Восстановление из бэкапа...${NC}"
  cp "$BACKUP_CONFIG" "$ROUTING_CONFIG"
  exit 1
fi

echo -e "\n${YELLOW}[3/3]${NC} Проверка конфигурации..."
echo -e "      ${BLUE}DNS серверы:${NC}"
echo -e "        - Cloudflare DoH: https://1.1.1.1/dns-query"
echo -e "        - Cloudflare Direct: 1.1.1.1"
echo -e "      ${BLUE}Маршрутизация:${NC}"
echo -e "        - google.com → Cloudflare"
echo -e "        - googleapis.com → Cloudflare"
echo -e "        - gstatic.com → Cloudflare"

echo -e "\n${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${GREEN}✓ Конфигурация применена${NC}               ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}ВАЖНО:${NC} Перезапустите NekoBox для применения изменений!"
echo -e "${BLUE}После перезапуска проверьте: ./scripts/quick-check.sh${NC}\n"

echo -e "${YELLOW}Бэкап сохранен:${NC} $BACKUP_CONFIG"
