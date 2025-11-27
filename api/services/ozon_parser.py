"""
Ozon Parser Service
Extracts product data from Ozon using JSON-LD Schema
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime
from loguru import logger

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    from playwright_stealth import stealth_async
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available")


class OzonParserService:
    """Service for parsing Ozon product pages"""

    def __init__(self, headless: bool = True, delay: float = 2.5):
        self.headless = headless
        self.delay = delay
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None

    async def start(self):
        """Initialize browser"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright is not installed")
            return

        self._playwright = await async_playwright().start()

        # Launch browser with stealth settings
        self.browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--lang=en-US",
            ]
        )

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="Europe/Moscow",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.page = await self.context.new_page()

        # Apply stealth patches
        await stealth_async(self.page)

        logger.info(f"Browser started (headless={self.headless})")

    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser closed")

    async def parse_product(self, sku: str) -> Dict:
        """
        Parse single product by SKU.
        Uses JSON-LD Schema for reliable data extraction.
        """
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
            "parsed_at": datetime.utcnow().isoformat()
        }

        if not self.page:
            result["error"] = "Browser not initialized"
            return result

        try:
            # Navigate to product page
            response = await self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            if response and response.status >= 400:
                result["error"] = f"HTTP {response.status}"
                return result

            # Wait for page to load
            await asyncio.sleep(2)

            # Check for antibot
            title = await self.page.title()
            if "Antibot" in title or "Challenge" in title:
                logger.warning(f"Antibot detected for SKU {sku}, waiting...")
                await asyncio.sleep(5)

                # Check again
                title = await self.page.title()
                if "Antibot" in title:
                    result["error"] = "Blocked by antibot"
                    return result

            # Extract JSON-LD data
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

            if not jsonld_data:
                result["error"] = "JSON-LD not found"
                return result

            # Parse JSON-LD data
            result["name"] = jsonld_data.get("name", "")

            # Brand can be string or object
            brand = jsonld_data.get("brand", "")
            if isinstance(brand, dict):
                result["brand"] = brand.get("name", "")
            else:
                result["brand"] = str(brand)

            # Offers (price, availability)
            offers = jsonld_data.get("offers", {})
            result["price"] = float(offers.get("price", 0))
            result["currency"] = offers.get("priceCurrency", "RUB")

            availability = offers.get("availability", "")
            result["availability"] = "В наличии" if "InStock" in availability else "Нет в наличии"

            # Rating
            rating = jsonld_data.get("aggregateRating", {})
            result["rating"] = float(rating.get("ratingValue", 0))
            result["reviews"] = int(rating.get("reviewCount", 0))

        except Exception as e:
            result["error"] = str(e)[:100]
            logger.error(f"Error parsing SKU {sku}: {e}")

        return result
