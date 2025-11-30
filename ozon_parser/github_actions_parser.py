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

    def __init__(self, use_camoufox: bool = True, delay: float = 10.0):
        self.use_camoufox = use_camoufox and CAMOUFOX_AVAILABLE
        self.delay = delay  # Увеличено с 3 до 10 секунд
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
                slow_mo=100,  # Замедление действий на 100мс (человекоподобно)
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

    async def human_behavior(self):
        """Имитация человеческого поведения на странице"""
        try:
            # Случайный скролл вниз
            scroll_amount = random.randint(300, 800)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # Скролл обратно вверх
            await self.page.evaluate(f"window.scrollBy(0, -{scroll_amount // 2})")
            await asyncio.sleep(random.uniform(0.3, 0.8))

            # Случайное движение мыши
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await self.page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass  # Игнорируем ошибки human behavior

    async def warmup(self):
        """Прогрев сессии - 5+ страниц для обхода rate-limit"""
        print("[WARMUP] Прогрев сессии Ozon (5 страниц)...", flush=True)

        warmup_urls = [
            "https://www.ozon.ru/",
            "https://www.ozon.ru/category/avtotovary-8500/",
            "https://www.ozon.ru/search/?text=масло+моторное",
            "https://www.ozon.ru/category/masla-motornye-8581/",
            "https://www.ozon.ru/search/?text=fuchs+titan",
        ]

        for i, url in enumerate(warmup_urls, 1):
            try:
                print(f"  [{i}/{len(warmup_urls)}] {url[:60]}...", flush=True)
                response = await self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
                status = response.status if response else "N/A"
                print(f"  [{i}/{len(warmup_urls)}] HTTP {status}", flush=True)

                # Человекоподобное поведение на каждой странице
                await self.human_behavior()

                # Увеличенная задержка 5-8 сек между warmup страницами
                delay = random.uniform(5.0, 8.0)
                print(f"  [{i}/{len(warmup_urls)}] Ожидание {delay:.1f}с...", flush=True)
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"  [{i}/{len(warmup_urls)}] ERROR: {str(e)[:50]}", flush=True)
                await asyncio.sleep(3)  # Даже при ошибке ждём

        print("[WARMUP] Сессия прогрета после 5 страниц, начинаем парсинг", flush=True)

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
            response = await self.page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # Check HTTP status
            if response and response.status >= 400:
                result["error"] = f"HTTP {response.status}"
                return result

            # Ждём загрузку контента + human behavior
            await asyncio.sleep(random.uniform(2.0, 4.0))
            await self.human_behavior()

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

    async def mini_warmup(self):
        """Короткий warmup после блокировки"""
        print("    [RE-WARMUP] Восстановление сессии...", flush=True)
        warmup_urls = [
            "https://www.ozon.ru/",
            "https://www.ozon.ru/search/?text=автомобильные+масла",
        ]
        for url in warmup_urls:
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await self.human_behavior()
                await asyncio.sleep(random.uniform(4.0, 6.0))
            except Exception:
                pass
        print("    [RE-WARMUP] Готово", flush=True)

    async def parse_search_page(self, query: str, target_skus: List[str] = None) -> List[Dict]:
        """
        Парсинг страницы ПОИСКА вместо отдельных карточек товаров.
        Одна страница = много товаров с ценами.

        Args:
            query: Поисковый запрос (напр. "fuchs titan 5w40")
            target_skus: Список SKU для фильтрации (опционально)

        Returns:
            Список найденных товаров с ценами
        """
        import re
        import urllib.parse

        encoded_query = urllib.parse.quote(query)
        url = f"https://www.ozon.ru/search/?text={encoded_query}&from_global=true"

        results = []
        print(f"\n[SEARCH] Парсинг поиска: '{query}'", flush=True)
        print(f"  URL: {url[:80]}...", flush=True)

        try:
            response = await self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
            status = response.status if response else "N/A"
            print(f"  HTTP: {status}", flush=True)

            if response and response.status >= 400:
                print(f"  [ERROR] HTTP {response.status}", flush=True)
                return results

            # Ждём загрузку + human behavior
            await asyncio.sleep(random.uniform(3.0, 5.0))
            await self.human_behavior()

            # Проверяем антибот
            title = await self.page.title()
            if "Antibot" in title or "captcha" in title.lower():
                print("  [ERROR] ANTIBOT_DETECTED on search page", flush=True)
                return results

            # === МЕТОД 1: Извлечение из JSON State ===
            print("  [DEBUG] Поиск JSON state...", flush=True)

            json_data = await self.page.evaluate("""
                () => {
                    // Ищем __NUXT_DATA__, __NEXT_DATA__, или другие JSON state
                    const scripts = document.querySelectorAll('script');
                    for (const script of scripts) {
                        const text = script.textContent || '';
                        // Ищем паттерны с данными товаров
                        if (text.includes('products') || text.includes('items') || text.includes('searchResultsV2')) {
                            // Пытаемся извлечь JSON
                            const matches = text.match(/\{[^{}]*"sku"[^{}]*\}/g);
                            if (matches && matches.length > 0) {
                                return { source: 'inline_json', count: matches.length, sample: matches[0] };
                            }
                        }
                    }

                    // Ищем window.__INITIAL_STATE__
                    if (window.__INITIAL_STATE__) {
                        return { source: '__INITIAL_STATE__', data: window.__INITIAL_STATE__ };
                    }

                    // Ищем NUXT
                    if (window.__NUXT__) {
                        return { source: '__NUXT__', keys: Object.keys(window.__NUXT__) };
                    }

                    return { source: 'not_found' };
                }
            """)

            print(f"  [DEBUG] JSON source: {json_data.get('source', 'unknown')}", flush=True)

            # === МЕТОД 2: Парсинг DOM карточек товаров ===
            print("  [DOM] Извлечение карточек товаров...", flush=True)

            products_data = await self.page.evaluate("""
                () => {
                    const products = [];

                    // Ozon использует data-widget="searchResultsV2" для результатов
                    const container = document.querySelector('[data-widget="searchResultsV2"]');
                    if (!container) {
                        // Альтернативный селектор
                        const items = document.querySelectorAll('[data-index]');
                        console.log('Found items with data-index:', items.length);
                    }

                    // Ищем карточки товаров по разным селекторам
                    const cards = document.querySelectorAll('div[class*="tile"], div[class*="product"], a[href*="/product/"]');

                    for (const card of cards) {
                        try {
                            // Извлекаем ссылку с SKU
                            const link = card.querySelector('a[href*="/product/"]') || card.closest('a[href*="/product/"]');
                            if (!link) continue;

                            const href = link.getAttribute('href') || '';
                            const skuMatch = href.match(/\/product\/([a-z0-9-]+)/i);
                            if (!skuMatch) continue;

                            const sku = skuMatch[1];

                            // Ищем цену
                            let price = 0;
                            const priceEl = card.querySelector('[class*="price"], [class*="Price"], span[class*="c3"]');
                            if (priceEl) {
                                const priceText = priceEl.textContent || '';
                                // Убираем пробелы и ₽, оставляем цифры
                                const priceMatch = priceText.replace(/\s/g, '').match(/(\d+)/);
                                if (priceMatch) {
                                    price = parseInt(priceMatch[1], 10);
                                }
                            }

                            // Ищем название
                            let name = '';
                            const nameEl = card.querySelector('[class*="title"], [class*="name"], span[class*="tsBody"]');
                            if (nameEl) {
                                name = nameEl.textContent?.trim() || '';
                            }

                            if (sku && price > 0) {
                                products.push({ sku, name: name.slice(0, 150), price });
                            }
                        } catch (e) {
                            // Игнорируем ошибки отдельных карточек
                        }
                    }

                    return products;
                }
            """)

            print(f"  [DOM] Найдено карточек: {len(products_data)}", flush=True)

            # === МЕТОД 3: Парсинг через JSON-LD (если есть) ===
            jsonld_products = await self.page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    const products = [];

                    for (const script of scripts) {
                        try {
                            const data = JSON.parse(script.textContent);
                            if (data['@type'] === 'ItemList' && data.itemListElement) {
                                for (const item of data.itemListElement) {
                                    if (item.item && item.item.offers) {
                                        products.push({
                                            sku: item.item.sku || '',
                                            name: item.item.name || '',
                                            price: parseFloat(item.item.offers.price) || 0
                                        });
                                    }
                                }
                            }
                        } catch (e) {}
                    }

                    return products;
                }
            """)

            print(f"  [JSON-LD] Найдено: {len(jsonld_products)}", flush=True)

            # Объединяем результаты из всех методов
            all_products = products_data + jsonld_products

            # Дедупликация по SKU
            seen_skus = set()
            for p in all_products:
                sku = str(p.get('sku', '')).split('-')[0]  # Убираем суффикс если есть
                if sku and sku not in seen_skus:
                    seen_skus.add(sku)
                    results.append({
                        "sku": sku,
                        "name": p.get('name', ''),
                        "price": p.get('price', 0),
                        "currency": "RUB",
                        "brand": "",
                        "rating": 0,
                        "reviews": 0,
                        "availability": "InStock" if p.get('price', 0) > 0 else "Unknown",
                        "error": "",
                        "parsed_at": datetime.utcnow().isoformat() + "Z",
                        "source": "search_page"
                    })

            # Фильтруем по target_skus если заданы
            if target_skus:
                target_set = set(str(s) for s in target_skus)
                filtered = [r for r in results if r['sku'] in target_set]
                print(f"  [FILTER] Совпадений с целевыми SKU: {len(filtered)}/{len(target_skus)}", flush=True)
                return filtered

            print(f"  [RESULT] Всего уникальных товаров: {len(results)}", flush=True)

            # Выводим первые 5 для проверки
            for i, p in enumerate(results[:5]):
                print(f"    {i+1}. SKU {p['sku']}: {p['price']} RUB - {p['name'][:50]}...", flush=True)

        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}", flush=True)

        return results

    async def parse_search_batch(self, queries: List[str], target_skus: List[str] = None) -> List[Dict]:
        """
        Парсинг нескольких поисковых запросов.

        Args:
            queries: Список поисковых запросов
            target_skus: Целевые SKU для сопоставления
        """
        all_results = []

        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Обрабатываем запрос: '{query}'", flush=True)

            results = await self.parse_search_page(query, target_skus)
            all_results.extend(results)

            # Задержка между запросами
            if i < len(queries):
                delay = random.uniform(10.0, 15.0)
                print(f"  Ожидание {delay:.1f}с перед следующим запросом...", flush=True)
                await asyncio.sleep(delay)

        # Дедупликация финальных результатов
        seen = set()
        unique_results = []
        for r in all_results:
            if r['sku'] not in seen:
                seen.add(r['sku'])
                unique_results.append(r)

        print(f"\n[TOTAL] Найдено уникальных товаров: {len(unique_results)}", flush=True)
        return unique_results

    async def parse_batch(self, skus: List[str]) -> List[Dict]:
        """Парсинг списка SKU с re-warmup при блокировке"""
        results = []
        total = len(skus)
        antibot_count = 0
        consecutive_antibot = 0

        for i, sku in enumerate(skus, 1):
            print(f"[{i}/{total}] SKU {sku}...", end=" ", flush=True)

            result = await self.parse_product(sku)
            results.append(result)

            if result["error"]:
                print(f"ERROR: {result['error']}")
                if result["error"] == "ANTIBOT_DETECTED":
                    antibot_count += 1
                    consecutive_antibot += 1

                    # После 2 подряд блокировок - re-warmup
                    if consecutive_antibot >= 2:
                        await self.mini_warmup()
                        consecutive_antibot = 0

                    # Абортируем только после 5 блокировок подряд
                    if antibot_count >= 5:
                        print("\n[ABORT] Too many antibot detections, stopping")
                        break
            else:
                print(f"{result['price']} RUB | {result['rating']}* | {result['reviews']} reviews")
                consecutive_antibot = 0  # Сброс счётчика при успехе

            # Увеличенная задержка 25-35 сек
            if i < total:
                delay = 25.0 + random.uniform(0, 10.0)
                print(f"    Ожидание {delay:.1f}с перед следующим товаром...", flush=True)
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
    parser.add_argument("--delay", type=float, default=10.0, help="Delay between requests (10-15s recommended)")
    parser.add_argument("--no-camoufox", action="store_true", help="Use standard Playwright")
    parser.add_argument("--search", action="store_true", help="Use SEARCH page parsing (v4 mode)")
    parser.add_argument("--queries", nargs="+", default=["fuchs titan"], help="Search queries for --search mode")

    args = parser.parse_args()

    # Определяем режим
    mode = "SEARCH" if args.search else "PRODUCT"

    print("=" * 60)
    print("  OZON PARSER - GitHub Actions Cloud Version v4")
    print(f"  Mode: {mode} page parsing")
    print("=" * 60)
    print(f"  Browser: {'Camoufox' if CAMOUFOX_AVAILABLE and not args.no_camoufox else 'Playwright + SlowMo'}")
    if args.search:
        print(f"  Queries: {args.queries}")
    else:
        print(f"  Delay: 25-35s between products")
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
        # Fallback: real SKUs from your Google Sheets (Fuchs oils)
        skus = [
            "2047259625",  # Fuchs 5W-40 1L - 819₽
            "2047258756",  # Fuchs 5W-30 1L - 697₽
            "2047250383",  # Fuchs 5W-40 4L - 1915₽
            "2047248764",  # Fuchs 5W-40 4L - 2653₽
            "2047245776",  # Fuchs 0W-20 4L - 2388₽
        ]
        print(f"[INFO] Using built-in test SKUs: {len(skus)}")

    # Apply limit
    if args.limit > 0:
        skus = skus[:args.limit]
        print(f"[INFO] Limited to {args.limit} SKUs")

    # Parse
    ozon = CloudOzonParser(
        use_camoufox=CAMOUFOX_AVAILABLE and not args.no_camoufox,
        delay=args.delay
    )

    try:
        await ozon.start()
        await ozon.warmup()  # Прогрев сессии для обхода rate-limit

        # === РЕЖИМ ПАРСИНГА ===
        if args.search:
            # v4: Парсинг страниц ПОИСКА (одна страница = много товаров)
            print(f"\n[START] Parsing SEARCH pages: {args.queries}")
            results = await ozon.parse_search_batch(args.queries, target_skus=skus if skus else None)
        else:
            # v3: Парсинг отдельных карточек товаров (старый метод)
            print(f"\n[START] Parsing {len(skus)} product pages...")
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
        successful = [r for r in results if not r.get("error")]
        antibot = [r for r in results if r.get("error") == "ANTIBOT_DETECTED"]

        print(f"\n{'='*50}")
        print(f"RESULTS: {len(successful)} products found")
        if antibot:
            print(f"ANTIBOT: {len(antibot)} blocked")

        if successful:
            prices = [r["price"] for r in successful if r["price"] > 0]
            if prices:
                print(f"Prices: {min(prices):.0f} - {max(prices):.0f} RUB")
                print(f"Average: {sum(prices)/len(prices):.0f} RUB")

        # Exit code
        if not results:
            print("\n[ERROR] No results obtained")
            sys.exit(1)

    finally:
        await ozon.close()


if __name__ == "__main__":
    asyncio.run(main())
