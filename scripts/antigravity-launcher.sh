#!/bin/bash
# Antigravity Launcher - запуск с проверкой VPN
# Использование: ./antigravity-launcher.sh

set -e

echo "=========================================="
echo "  Google Antigravity Launcher"
echo "=========================================="

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Заблокированные регионы
BLOCKED_REGIONS="RU CN IR KP SY CU"

# Проверка IP и региона
check_ip() {
    echo -e "\n${YELLOW}[1/3] Проверка IP адреса...${NC}"

    IP_INFO=$(curl -s "https://ipapi.co/json/" 2>/dev/null || echo "{}")
    IP=$(echo "$IP_INFO" | grep -o '"ip": "[^"]*"' | cut -d'"' -f4)
    COUNTRY=$(echo "$IP_INFO" | grep -o '"country_code": "[^"]*"' | cut -d'"' -f4)
    COUNTRY_NAME=$(echo "$IP_INFO" | grep -o '"country_name": "[^"]*"' | cut -d'"' -f4)

    if [ -z "$IP" ]; then
        echo -e "${RED}[ERROR] Не удалось получить IP. Проверьте интернет-соединение.${NC}"
        exit 1
    fi

    echo -e "  IP: ${GREEN}$IP${NC}"
    echo -e "  Страна: ${GREEN}$COUNTRY_NAME ($COUNTRY)${NC}"

    # Проверка блокировки
    if echo "$BLOCKED_REGIONS" | grep -q "$COUNTRY"; then
        echo -e "${RED}[ERROR] Регион $COUNTRY заблокирован для Antigravity!${NC}"
        echo -e "${YELLOW}Включите VPN с сервером в поддерживаемой стране (US, DE, EE, NL)${NC}"
        exit 1
    fi

    echo -e "${GREEN}[OK] Регион поддерживается${NC}"
}

# Проверка VPN
check_vpn() {
    echo -e "\n${YELLOW}[2/3] Проверка VPN...${NC}"

    # Проверка TUN интерфейса
    if ip link show tun0 &>/dev/null || ip link show utun0 &>/dev/null; then
        echo -e "${GREEN}[OK] TUN интерфейс обнаружен${NC}"
    else
        echo -e "${YELLOW}[WARN] TUN интерфейс не найден. VPN может работать в режиме прокси.${NC}"
    fi

    # Проверка NekoBox/Nekoray
    if pgrep -x "nekobox" > /dev/null || pgrep -x "nekoray" > /dev/null; then
        echo -e "${GREEN}[OK] NekoBox/Nekoray запущен${NC}"
    else
        echo -e "${YELLOW}[WARN] NekoBox/Nekoray не обнаружен${NC}"
    fi
}

# Запуск Antigravity
launch_antigravity() {
    echo -e "\n${YELLOW}[3/3] Запуск Antigravity...${NC}"

    # Поиск исполняемого файла
    ANTIGRAVITY_PATHS=(
        "/usr/bin/antigravity"
        "/usr/local/bin/antigravity"
        "$HOME/.local/bin/antigravity"
        "/opt/antigravity/antigravity"
        "/snap/bin/antigravity"
    )

    ANTIGRAVITY_BIN=""
    for path in "${ANTIGRAVITY_PATHS[@]}"; do
        if [ -x "$path" ]; then
            ANTIGRAVITY_BIN="$path"
            break
        fi
    done

    if [ -z "$ANTIGRAVITY_BIN" ]; then
        echo -e "${RED}[ERROR] Antigravity не найден!${NC}"
        echo -e "Скачайте с: ${GREEN}https://antigravity.google/download${NC}"
        exit 1
    fi

    echo -e "${GREEN}[OK] Найден: $ANTIGRAVITY_BIN${NC}"
    echo -e "\n${GREEN}Запуск Antigravity...${NC}\n"

    # Установка переменных окружения
    export LANG=en_US.UTF-8
    export LANGUAGE=en_US

    # Запуск
    "$ANTIGRAVITY_BIN" "$@"
}

# Основной flow
main() {
    check_ip
    check_vpn
    launch_antigravity "$@"
}

main "$@"
