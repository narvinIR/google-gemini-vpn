#!/usr/bin/env python3
"""
Ozon Parser CLI
Использование: python -m ozon_parser.main [команда] [опции]
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from seller_api import OzonSellerAPI, test_connection, ACCOUNTS

def cmd_test(args):
    """Тест подключения ко всем аккаунтам"""
    print("=== Тест подключения к Ozon Seller API ===\n")
    for acc in ACCOUNTS.keys():
        test_connection(acc)

def cmd_products(args):
    """Список товаров"""
    api = OzonSellerAPI(args.account)
    result = api.get_product_list(limit=args.limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_prices(args):
    """Цены товаров"""
    api = OzonSellerAPI(args.account)
    result = api.get_prices(limit=args.limit)

    if "result" in result and "items" in result["result"]:
        items = result["result"]["items"]
        print(f"\n=== Цены ({len(items)} товаров) ===\n")
        for item in items[:20]:  # Показываем первые 20
            pid = item.get("product_id", "?")
            offer = item.get("offer_id", "?")
            price = item.get("price", {}).get("price", "?")
            old = item.get("price", {}).get("old_price", "-")
            ozon_card = item.get("price", {}).get("ozon_card_price", "-")
            print(f"[{pid}] {offer}: {price}₽ (было: {old}, Ozon карта: {ozon_card})")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_stocks(args):
    """Остатки товаров"""
    api = OzonSellerAPI(args.account)
    result = api.get_stocks(limit=args.limit)

    if "result" in result and "items" in result["result"]:
        items = result["result"]["items"]
        print(f"\n=== Остатки ({len(items)} товаров) ===\n")
        for item in items[:20]:
            pid = item.get("product_id", "?")
            offer = item.get("offer_id", "?")
            stocks = item.get("stocks", [])
            total = sum(s.get("present", 0) for s in stocks)
            print(f"[{pid}] {offer}: {total} шт")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_info(args):
    """Информация о товаре по product_id"""
    api = OzonSellerAPI(args.account)
    product_ids = [int(x) for x in args.ids.split(",")]
    result = api.get_product_info(product_ids=product_ids)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description="Ozon Seller API CLI")
    parser.add_argument("-a", "--account", default="main", choices=["main", "prices"],
                        help="Аккаунт: main (VERTEX) или prices (Foxgear)")

    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # test
    sub_test = subparsers.add_parser("test", help="Тест подключения")
    sub_test.set_defaults(func=cmd_test)

    # products
    sub_products = subparsers.add_parser("products", help="Список товаров")
    sub_products.add_argument("-l", "--limit", type=int, default=100)
    sub_products.set_defaults(func=cmd_products)

    # prices
    sub_prices = subparsers.add_parser("prices", help="Цены товаров")
    sub_prices.add_argument("-l", "--limit", type=int, default=100)
    sub_prices.set_defaults(func=cmd_prices)

    # stocks
    sub_stocks = subparsers.add_parser("stocks", help="Остатки товаров")
    sub_stocks.add_argument("-l", "--limit", type=int, default=100)
    sub_stocks.set_defaults(func=cmd_stocks)

    # info
    sub_info = subparsers.add_parser("info", help="Инфо о товаре по ID")
    sub_info.add_argument("ids", help="product_id через запятую: 123,456,789")
    sub_info.set_defaults(func=cmd_info)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)

if __name__ == "__main__":
    main()
