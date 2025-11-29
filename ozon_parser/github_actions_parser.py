#!/usr/bin/env python3
"""
Ozon Parser for GitHub Actions (CLOUD VERSION)

Отличия от локальной версии:
- Использует Camoufox (anti-detect browser) вместо обычного Playwright
- Сохраняет в Supabase вместо/вместе с Google Sheets
- Работает в headless режиме без GUI
- Конфиг через переменные окружения (GitHub Secrets)
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

# Проверка Camoufox
try:
    from camoufox.async_api import AsyncCamoufox
    CAMOUFOX_AVAILABLE = True
except ImportError:
    CAMOUFOX_AVAILABLE = False
    print("[WARN] Camoufox not available, using standard Playwright")

# Fallback на обычный Playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: pip install playwright && playwright install chromium")
    sys.exit(1)

# Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("[WARN] Supabase not available")

# Google Sheets
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False


class CloudOzonParser:
    """Парсер Ozon для облачного выполнения"""

    def __init__(self, use_camoufox: bool = True, delay: float = 3.0):
        self.use_camoufox = use_camoufox and CAMOUFOX_AVAILABLE
        self.delay = delay
        self.browser = None
        self.page = None
        self._playwright = None

    async def start(self):
        """Запуск браузера"""
        if self.use_camoufox:
            print("[START] Camoufox (anti-detect mode)")
            self.browser = await AsyncCamoufox(headless=True).__aenter__()
            self.page = await self.browser.new_page()
        else:
            print("[START] Standard Playwright (headless)")
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--lang=ru-RU",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            )
            context = await self.browser.new_context(
                locale="ru-RU",
                timezone_id="Europe/Moscow",
                viewport={"width": 1920, "height": 1080},
            )
            self.page = await context.new_page()

            # Anti-detection scripts
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)

        print("[OK] Browser started")

    async def close(self):
        """Закрытие браузера"""
        if self.browser:
            if self.use_camoufox:
                await self.browser.__aexit__(None, None, None)
            else:
                await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
        print("[OK] Browser closed")

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
            "parsed_at": datetime.utcnow().isoformat() + "Z"
        }

        try:
            response = await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Check HTTP status
            if response and response.status >= 400:
                result["error"] = f"HTTP {response.status}"
                return result

            await asyncio.sleep(2)

            # Check antibot
            title = await self.page.title()
            content = await self.page.content()

            if "Antibot" in title or "captcha" in content.lower() or "robot" in content.lower():
                result["error"] = "ANTIBOT_DETECTED"
                print(f"  [!] Antibot/Captcha on SKU {sku}")
                return result

            # Extract JSON-LD
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
                result["availability"] = "InStock" if "InStock" in availability else "OutOfStock"

                rating = jsonld_data.get("aggregateRating", {})
                result["rating"] = float(rating.get("ratingValue", 0))
                result["reviews"] = int(rating.get("reviewCount", 0))
            else:
                # Check if product not found
                if "товар не найден" in content.lower() or "page not found" in content.lower():
                    result["error"] = "PRODUCT_NOT_FOUND"
                else:
                    result["error"] = "JSON_LD_NOT_FOUND"

        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    async def parse_batch(self, skus: List[str]) -> List[Dict]:
        """Парсинг списка SKU"""
        results = []
        total = len(skus)
        antibot_count = 0

        for i, sku in enumerate(skus, 1):
            print(f"[{i}/{total}] SKU {sku}...", end=" ", flush=True)

            result = await self.parse_product(sku)
            results.append(result)

            if result["error"]:
                print(f"ERROR: {result['error']}")
                if result["error"] == "ANTIBOT_DETECTED":
                    antibot_count += 1
                    if antibot_count >= 3:
                        print("\n[ABORT] Too many antibot detections, stopping")
                        break
            else:
                print(f"{result['price']} RUB | {result['rating']}* | {result['reviews']} reviews")

            # Random delay
            if i < total:
                delay = self.delay + random.uniform(0.5, 2.0)
                await asyncio.sleep(delay)

        return results


def init_supabase() -> Optional[Client]:
    """Инициализация Supabase клиента"""
    if not SUPABASE_AVAILABLE:
        return None

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("[WARN] SUPABASE_URL or SUPABASE_KEY not set")
        return None

    return create_client(url, key)


def save_to_supabase(client: Client, results: List[Dict]) -> bool:
    """Сохранение результатов в Supabase"""
    try:
        # Prepare data for upsert
        rows = []
        for r in results:
            if not r["error"]:  # Only save successful parses
                rows.append({
                    "sku": r["sku"],
                    "name": r["name"][:500] if r["name"] else None,
                    "price": r["price"],
                    "currency": r["currency"],
                    "brand": r["brand"],
                    "rating": r["rating"],
                    "reviews": r["reviews"],
                    "availability": r["availability"],
                    "parsed_at": r["parsed_at"]
                })

        if rows:
            # Upsert to competitor_prices table
            client.table("competitor_prices").upsert(
                rows,
                on_conflict="sku"
            ).execute()
            print(f"[OK] Saved {len(rows)} rows to Supabase")
            return True

    except Exception as e:
        print(f"[ERROR] Supabase save failed: {e}")

    return False


def init_gsheets():
    """Инициализация Google Sheets из env credentials"""
    if not GSHEETS_AVAILABLE:
        return None

    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        print("[WARN] GOOGLE_CREDENTIALS not set")
        return None

    try:
        creds_dict = json.loads(creds_json)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"[ERROR] Google Sheets init failed: {e}")
        return None


def read_skus_from_sheets(gc, sheet_id: str) -> List[str]:
    """Читает SKU из Google Sheets"""
    try:
        spreadsheet = gc.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet("Парсинг товаров")
        values = worksheet.col_values(1)[1:]  # Column A, skip header
        return [v.strip() for v in values if v.strip()]
    except Exception as e:
        print(f"[ERROR] Reading sheets: {e}")
        return []


def write_results_to_sheets(gc, sheet_id: str, results: List[Dict]):
    """Записывает результаты в Google Sheets"""
    try:
        spreadsheet = gc.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet("Парсинг товаров")

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

        if rows:
            worksheet.update(values=rows, range_name=f"B2:I{1 + len(rows)}")
            print(f"[OK] Updated {len(rows)} rows in Google Sheets")

    except Exception as e:
        print(f"[ERROR] Writing to sheets: {e}")


def write_csv(filepath: str, results: List[Dict]):
    """Записывает результаты в CSV"""
    fieldnames = ["sku", "name", "price", "currency", "brand", "rating", "reviews", "availability", "parsed_at", "error"]

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"[OK] Saved to {filepath}")


async def main():
    parser = argparse.ArgumentParser(description="Ozon Parser for GitHub Actions")
    parser.add_argument("--limit", type=int, default=0, help="Limit SKUs (0 = all)")
    parser.add_argument("--test", action="store_true", help="Test mode (no save)")
    parser.add_argument("--skus", nargs="+", help="Manual SKU list")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between requests")
    parser.add_argument("--no-camoufox", action="store_true", help="Use standard Playwright")

    args = parser.parse_args()

    print("=" * 60)
    print("  OZON PARSER - GitHub Actions Cloud Version")
    print("=" * 60)
    print(f"  Mode: {'Camoufox' if CAMOUFOX_AVAILABLE and not args.no_camoufox else 'Playwright'}")
    print(f"  Delay: {args.delay}s + random")
    print(f"  Test mode: {args.test}")
    print("=" * 60)
    print()

    # Get SKUs
    skus = []
    gc = None
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")

    if args.skus:
        skus = args.skus
        print(f"[INFO] SKUs from args: {len(skus)}")
    elif sheet_id:
        gc = init_gsheets()
        if gc:
            skus = read_skus_from_sheets(gc, sheet_id)
            print(f"[INFO] SKUs from Google Sheets: {len(skus)}")

    if not skus:
        # Fallback: test SKUs
        skus = ["1234567890", "9876543210"]
        print(f"[WARN] Using test SKUs: {skus}")

    # Apply limit
    if args.limit > 0:
        skus = skus[:args.limit]
        print(f"[INFO] Limited to {args.limit} SKUs")

    print(f"\n[START] Parsing {len(skus)} products...")

    # Parse
    ozon = CloudOzonParser(
        use_camoufox=CAMOUFOX_AVAILABLE and not args.no_camoufox,
        delay=args.delay
    )

    try:
        await ozon.start()
        results = await ozon.parse_batch(skus)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"results_{timestamp}.csv"
        write_csv(csv_path, results)

        if not args.test:
            # Save to Supabase
            supabase = init_supabase()
            if supabase:
                save_to_supabase(supabase, results)

            # Update Google Sheets
            if gc and sheet_id:
                write_results_to_sheets(gc, sheet_id, results)

        # Stats
        successful = [r for r in results if not r["error"]]
        antibot = [r for r in results if r["error"] == "ANTIBOT_DETECTED"]

        print(f"\n{'='*50}")
        print(f"RESULTS: {len(successful)}/{len(results)} successful")
        print(f"ANTIBOT: {len(antibot)} blocked")

        if successful:
            prices = [r["price"] for r in successful if r["price"] > 0]
            if prices:
                print(f"Prices: {min(prices):.0f} - {max(prices):.0f} RUB")

        # Exit code based on success rate
        success_rate = len(successful) / len(results) if results else 0
        if success_rate < 0.5:
            print(f"\n[WARN] Low success rate: {success_rate:.0%}")
            if len(antibot) >= 3:
                print("[ERROR] GitHub Actions IP likely blocked by Ozon")
                sys.exit(2)

    finally:
        await ozon.close()


if __name__ == "__main__":
    asyncio.run(main())
