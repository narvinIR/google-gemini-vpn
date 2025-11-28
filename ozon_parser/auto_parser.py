#!/usr/bin/env python3
"""
Автономный парсер конкурентов Ozon (ЛОКАЛЬНАЯ ВЕРСИЯ)
Читает SKU из Google Sheets → Парсит цены → Записывает обратно

Использование:
  python auto_parser.py                           # Использует конфиг по умолчанию
  python auto_parser.py --sheet "ID_таблицы"
  python auto_parser.py --csv input.csv --output results.csv

ВАЖНО: Запускать на ДОМАШНЕМ ПК, не на VPS (Ozon блокирует датацентры)
"""

import asyncio
import argparse
import csv
import json
import random
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

try:
    from playwright.async_api import async_playwright, Browser, Page
    try:
        from playwright_stealth import Stealth
        STEALTH_AVAILABLE = True
    except ImportError:
        STEALTH_AVAILABLE = False
except ImportError:
    print("Установи playwright: pip install playwright && playwright install chromium")
    sys.exit(1)

# Google Sheets через gspread
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    print("[WARN] gspread не установлен, Google Sheets недоступен")

# Конфигурация по умолчанию
DEFAULT_SHEET_ID = "1la2mK1DpL6KvnQ5t4oRDvUietTMhgS2ZWfNnS1H4EgQ"
DEFAULT_CREDS_PATH = Path(__file__).parent.parent / "credentials" / "service-account.json"


class OzonParser:
    """Парсер цен конкурентов с Ozon через JSON-LD Schema"""

    def __init__(self, headless: bool = False, delay: float = 2.5):
        self.headless = headless  # False = видишь браузер, True = фоновый режим
        self.delay = delay  # Задержка между запросами (сек)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def start(self):
        """Запуск браузера"""
        self._playwright = await async_playwright().start()

        # Используем существующий профиль Chrome (с пройденным антиботом)
        user_data_dir = Path.home() / "OzonParserProfile"

        self.browser = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=self.headless,
            locale="ru-RU",  # Русская локаль для Ozon
            timezone_id="Europe/Moscow",
            viewport={"width": 1920, "height": 1080},
            args=[
                "--lang=ru-RU",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ]
        )
        self.page = await self.browser.new_page()

        # Применяем stealth если доступен
        if STEALTH_AVAILABLE:
            stealth = Stealth()
            await stealth.apply_stealth_async(self.page)
            print("[OK] Stealth mode активирован")

        # Маскировка автоматизации
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']});
        """)

        print(f"[OK] Браузер запущен (headless={self.headless})")

    async def close(self):
        """Закрытие браузера"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, '_playwright') and self._playwright:
            await self._playwright.stop()

    async def parse_product(self, sku: str) -> Dict:
        """Парсинг одного товара по SKU"""
        url = f"https://www.ozon.ru/product/{sku}/"
        result = {
            "sku": sku,
            "name": "",
            "price": 0,
            "currency": "RUB",
            "brand": "",
            "rating": 0,
            "reviews": 0,
            "availability": "",
            "error": "",
            "parsed_at": datetime.now().isoformat()
        }

        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)  # Ждём загрузку

            # Проверяем антибот
            title = await self.page.title()
            if "Antibot" in title or "Challenge" in title:
                print(f"  [!] Antibot detected, waiting 5s...")
                await asyncio.sleep(5)

            # Извлекаем JSON-LD
            jsonld_data = await self.page.evaluate("""
                () => {
                    const script = document.querySelector('script[type="application/ld+json"]');
                    if (!script) return null;
                    try {
                        return JSON.parse(script.textContent);
                    } catch(e) {
                        return null;
                    }
                }
            """)

            if jsonld_data:
                result["name"] = jsonld_data.get("name", "")
                result["brand"] = jsonld_data.get("brand", {})
                if isinstance(result["brand"], dict):
                    result["brand"] = result["brand"].get("name", "")

                offers = jsonld_data.get("offers", {})
                result["price"] = float(offers.get("price", 0))
                result["currency"] = offers.get("priceCurrency", "RUB")

                availability = offers.get("availability", "")
                result["availability"] = "В наличии" if "InStock" in availability else "Нет в наличии"

                rating = jsonld_data.get("aggregateRating", {})
                result["rating"] = float(rating.get("ratingValue", 0))
                result["reviews"] = int(rating.get("reviewCount", 0))
            else:
                result["error"] = "JSON-LD not found"

        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    async def parse_batch(self, skus: List[str], progress_callback=None) -> List[Dict]:
        """Парсинг списка SKU"""
        results = []
        total = len(skus)

        for i, sku in enumerate(skus, 1):
            print(f"[{i}/{total}] Парсинг SKU {sku}...", end=" ")

            result = await self.parse_product(sku)
            results.append(result)

            if result["error"]:
                print(f"ОШИБКА: {result['error']}")
            else:
                print(f"{result['price']} {result['currency']} | {result['rating']}★ | {result['reviews']} отзывов")

            if progress_callback:
                progress_callback(i, total, result)

            # Случайная задержка (2-4 сек) чтобы не забанили
            if i < total:
                delay = self.delay + random.uniform(0, 1.5)
                await asyncio.sleep(delay)

        return results


def read_csv(filepath: str) -> List[str]:
    """Читает SKU из CSV (первая колонка)"""
    skus = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # Пропускаем заголовок
        for row in reader:
            if row and row[0].strip():
                skus.append(row[0].strip())
    return skus


def write_csv(filepath: str, results: List[Dict]):
    """Записывает результаты в CSV"""
    fieldnames = ["sku", "name", "price", "currency", "brand", "rating", "reviews", "availability", "parsed_at", "error"]

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[OK] Результаты сохранены: {filepath}")


class GoogleSheetsClient:
    """Клиент для Google Sheets через gspread"""

    def __init__(self, credentials_file: str = None):
        if not GSHEETS_AVAILABLE:
            raise ImportError("Установи: pip install gspread google-auth")

        creds_path = credentials_file or str(DEFAULT_CREDS_PATH)

        if not Path(creds_path).exists():
            raise FileNotFoundError(f"Credentials не найдены: {creds_path}")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        self.gc = gspread.authorize(creds)
        print(f"[OK] Google Sheets подключен")

    def read_skus(self, spreadsheet_id: str, sheet_name: str = "Парсинг товаров") -> List[str]:
        """Читает SKU из колонки A листа 'Парсинг товаров'"""
        spreadsheet = self.gc.open_by_key(spreadsheet_id)

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.sheet1
            print(f"[WARN] Лист '{sheet_name}' не найден, используем первый лист")

        # Читаем колонку A начиная со 2 строки (пропускаем заголовок)
        values = worksheet.col_values(1)[1:]  # col A, skip header
        skus = [v.strip() for v in values if v.strip()]
        return skus

    def write_results(self, spreadsheet_id: str, results: List[Dict], sheet_name: str = "Парсинг товаров"):
        """Записывает результаты в колонки B-I"""
        spreadsheet = self.gc.open_by_key(spreadsheet_id)

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.sheet1

        # Подготовка данных: B=Name, C=Price, D=Brand, E=Rating, F=Reviews, G=Availability, H=Date, I=Error
        rows = []
        for r in results:
            rows.append([
                r["name"][:200] if r["name"] else "",
                r["price"],
                r["brand"],
                r["rating"],
                r["reviews"],
                r["availability"],
                r["parsed_at"],
                r["error"]
            ])

        # Batch update начиная с B2
        if rows:
            start_row = 2
            end_row = start_row + len(rows) - 1
            range_name = f"B{start_row}:I{end_row}"
            worksheet.update(values=rows, range_name=range_name, value_input_option="RAW")
            print(f"[OK] Записано {len(rows)} строк в Google Sheets ({sheet_name})")


async def main():
    parser = argparse.ArgumentParser(description="Парсер конкурентов Ozon (ЛОКАЛЬНАЯ ВЕРСИЯ)")
    parser.add_argument("--csv", help="CSV файл со SKU (колонка A)")
    parser.add_argument("--output", "-o", default="results.csv", help="Выходной CSV файл")
    parser.add_argument("--sheet", default=DEFAULT_SHEET_ID, help="ID Google Sheets таблицы")
    parser.add_argument("--creds", default=str(DEFAULT_CREDS_PATH), help="Файл credentials для Google API")
    parser.add_argument("--headless", action="store_true", help="Фоновый режим (без окна браузера)")
    parser.add_argument("--delay", type=float, default=2.5, help="Задержка между запросами (сек)")
    parser.add_argument("--skus", nargs="+", help="SKU через пробел: --skus 123 456 789")
    parser.add_argument("--limit", type=int, default=0, help="Ограничить количество SKU (0 = все)")

    args = parser.parse_args()

    print("=" * 60)
    print("  OZON PARSER - Локальная версия для домашнего ПК")
    print("=" * 60)
    print()

    # Определяем источник SKU
    skus = []
    sheets_client = None
    spreadsheet_id = None

    if args.skus:
        skus = args.skus
        print(f"[INFO] SKU из командной строки: {len(skus)} шт")

    elif args.csv:
        skus = read_csv(args.csv)
        print(f"[INFO] SKU из {args.csv}: {len(skus)} шт")

    else:
        # По умолчанию берём из Google Sheets
        if "docs.google.com" in args.sheet:
            spreadsheet_id = args.sheet.split("/d/")[1].split("/")[0]
        else:
            spreadsheet_id = args.sheet

        sheets_client = GoogleSheetsClient(args.creds)
        skus = sheets_client.read_skus(spreadsheet_id)
        print(f"[INFO] SKU из Google Sheets: {len(skus)} шт")

    if not skus:
        print("[ERROR] Список SKU пуст!")
        sys.exit(1)

    # Применяем лимит
    if args.limit > 0:
        skus = skus[:args.limit]
        print(f"[INFO] Ограничено до {args.limit} SKU")

    print(f"\n[START] Начинаем парсинг {len(skus)} товаров...")
    print(f"[INFO] Задержка между запросами: {args.delay}-{args.delay + 1.5} сек")
    print()

    # Парсим
    ozon = OzonParser(headless=args.headless, delay=args.delay)

    try:
        await ozon.start()
        results = await ozon.parse_batch(skus)

        # Сохраняем результаты
        if sheets_client and spreadsheet_id:
            sheets_client.write_results(spreadsheet_id, results)

        write_csv(args.output, results)

        # Статистика
        successful = [r for r in results if not r["error"]]
        print(f"\n{'='*50}")
        print(f"ИТОГО: {len(successful)}/{len(results)} успешно")

        if successful:
            prices = [r["price"] for r in successful if r["price"] > 0]
            if prices:
                print(f"Цены: {min(prices):.0f} - {max(prices):.0f} ₽")
                print(f"Средняя: {sum(prices)/len(prices):.0f} ₽")

    finally:
        await ozon.close()


if __name__ == "__main__":
    asyncio.run(main())
