#!/usr/bin/env python3
"""
Ozon Competitor Parser
Парсинг цен конкурентов через JSON-LD схему
Использует Playwright для обхода антибота
"""
import asyncio
import json
import re
from dataclasses import dataclass
from typing import Optional, List
from playwright.async_api import async_playwright, Page

@dataclass
class ProductData:
    sku: str
    name: str
    price: float
    currency: str
    brand: str
    rating: float
    review_count: int
    availability: str
    description: str
    image_url: str
    url: str

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "brand": self.brand,
            "rating": self.rating,
            "review_count": self.review_count,
            "availability": self.availability,
            "description": self.description[:200] + "..." if len(self.description) > 200 else self.description,
            "image_url": self.image_url,
            "url": self.url
        }

class OzonCompetitorParser:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--lang=en-US',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        self.context = await self.browser.new_context(
            locale='en-US',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def parse_product(self, url: str) -> Optional[ProductData]:
        """Парсинг одного товара по URL"""
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(2000)  # Ждём загрузки данных

            # Извлекаем JSON-LD
            jsonld = await page.evaluate('''() => {
                const script = document.querySelector('script[type="application/ld+json"]');
                return script ? JSON.parse(script.textContent) : null;
            }''')

            if not jsonld:
                print(f"JSON-LD не найден: {url}")
                return None

            # Парсим данные
            offers = jsonld.get('offers', {})
            rating = jsonld.get('aggregateRating', {})

            return ProductData(
                sku=str(jsonld.get('sku', '')),
                name=jsonld.get('name', ''),
                price=float(offers.get('price', 0)),
                currency=offers.get('priceCurrency', 'RUB'),
                brand=jsonld.get('brand', ''),
                rating=float(rating.get('ratingValue', 0)),
                review_count=int(rating.get('reviewCount', 0)),
                availability='InStock' if 'InStock' in offers.get('availability', '') else 'OutOfStock',
                description=jsonld.get('description', ''),
                image_url=jsonld.get('image', ''),
                url=offers.get('url', url)
            )
        except Exception as e:
            print(f"Ошибка парсинга {url}: {e}")
            return None
        finally:
            await page.close()

    async def parse_products(self, urls: List[str]) -> List[ProductData]:
        """Парсинг списка товаров"""
        results = []
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Парсинг: {url[:60]}...")
            product = await self.parse_product(url)
            if product:
                results.append(product)
                print(f"  ✓ {product.name[:50]}... = {product.price} {product.currency}")
            await asyncio.sleep(1)  # Задержка между запросами
        return results

    async def search_and_parse(self, query: str, limit: int = 10) -> List[ProductData]:
        """Поиск товаров и парсинг результатов"""
        page = await self.context.new_page()
        try:
            search_url = f"https://www.ozon.ru/search/?text={query}&from_global=true"
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)

            # Извлекаем ссылки на товары
            links = await page.evaluate('''(limit) => {
                const links = [];
                document.querySelectorAll('a[href*="/product/"]').forEach(a => {
                    const href = a.getAttribute('href');
                    if (href && href.includes('/product/') && !links.includes(href)) {
                        links.push('https://www.ozon.ru' + href.split('?')[0]);
                    }
                });
                return [...new Set(links)].slice(0, limit);
            }''', limit)

            print(f"Найдено {len(links)} товаров по запросу '{query}'")
            return await self.parse_products(links)
        finally:
            await page.close()


async def main():
    """Пример использования"""
    print("=== Ozon Competitor Parser ===\n")

    # Тестовые URL
    test_urls = [
        "https://www.ozon.ru/product/salfetki-ot-pyaten-na-odezhde-vlazhnye-pyatnovyvodyashchie-sredstvo-ochishchayushchie-obuv-mini-1650868905/",
    ]

    async with OzonCompetitorParser(headless=True) as parser:
        # Парсинг конкретных товаров
        print("1. Парсинг по URL:")
        products = await parser.parse_products(test_urls)

        for p in products:
            print(f"\n{'='*50}")
            print(json.dumps(p.to_dict(), indent=2, ensure_ascii=False))

        # Поиск и парсинг
        print("\n\n2. Поиск и парсинг:")
        search_results = await parser.search_and_parse("моторное масло fuchs", limit=5)

        print(f"\nНайдено {len(search_results)} товаров:")
        for p in search_results:
            print(f"  - {p.name[:60]}... = {p.price} {p.currency}")


if __name__ == "__main__":
    asyncio.run(main())
