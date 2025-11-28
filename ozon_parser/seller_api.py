"""
Ozon Seller API Client
Документация: https://docs.ozon.ru/api/seller/
"""
import os
import json
import requests
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api-seller.ozon.ru"

@dataclass
class OzonCredentials:
    client_id: str
    api_key: str
    name: str = "default"

# Предустановленные аккаунты
ACCOUNTS = {
    "main": OzonCredentials(
        client_id=os.getenv("OZON_MAIN_CLIENT_ID", ""),
        api_key=os.getenv("OZON_MAIN_API_KEY", ""),
        name="VERTEX"
    ),
    "prices": OzonCredentials(
        client_id=os.getenv("OZON_PRICES_CLIENT_ID", ""),
        api_key=os.getenv("OZON_PRICES_API_KEY", ""),
        name="Foxgear"
    )
}

class OzonSellerAPI:
    def __init__(self, account: str = "main"):
        creds = ACCOUNTS.get(account)
        if not creds or not creds.client_id:
            raise ValueError(f"Account '{account}' not found or credentials missing")
        self.creds = creds
        self.session = requests.Session()
        self.session.headers.update({
            "Client-Id": creds.client_id,
            "Api-Key": creds.api_key,
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        url = f"{BASE_URL}{endpoint}"
        try:
            resp = self.session.request(method, url, json=data)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e), "status_code": resp.status_code, "body": resp.text}
        except Exception as e:
            return {"error": str(e)}

    # === Товары ===

    def get_product_list(self, limit: int = 100, last_id: str = "") -> dict:
        """Список товаров"""
        return self._request("POST", "/v3/product/list", {
            "filter": {"visibility": "ALL"},
            "limit": limit,
            "last_id": last_id
        })

    def get_product_info(self, product_ids: list = None, offer_ids: list = None, skus: list = None) -> dict:
        """Информация о товарах"""
        return self._request("POST", "/v2/product/info", {
            "product_id": product_ids or [],
            "offer_id": offer_ids or [],
            "sku": skus or []
        })

    # === Цены ===

    def get_prices(self, limit: int = 1000, last_id: str = "") -> dict:
        """Получить цены товаров"""
        return self._request("POST", "/v5/product/info/prices", {
            "filter": {"visibility": "ALL"},
            "limit": limit,
            "last_id": last_id
        })

    def update_prices(self, prices: list) -> dict:
        """Обновить цены. prices = [{"product_id": 123, "price": "1000"}]"""
        return self._request("POST", "/v1/product/import/prices", {
            "prices": prices
        })

    # === Остатки ===

    def get_stocks(self, limit: int = 1000, last_id: str = "") -> dict:
        """Получить остатки товаров (FBO + FBS)"""
        return self._request("POST", "/v4/product/info/stocks", {
            "filter": {"visibility": "ALL"},
            "limit": limit,
            "last_id": last_id
        })

    def update_stocks(self, stocks: list) -> dict:
        """Обновить остатки. stocks = [{"product_id": 123, "stock": 10, "warehouse_id": 123}]"""
        return self._request("POST", "/v2/products/stocks", {
            "stocks": stocks
        })

    # === Финансы ===

    def get_transactions(self, date_from: str, date_to: str, page: int = 1) -> dict:
        """Транзакции за период. Формат дат: YYYY-MM-DD"""
        return self._request("POST", "/v3/finance/transaction/list", {
            "filter": {
                "date": {"from": f"{date_from}T00:00:00Z", "to": f"{date_to}T23:59:59Z"}
            },
            "page": page,
            "page_size": 1000
        })

    # === Аналитика ===

    def get_search_queries(self, date_from: str, date_to: str, limit: int = 100) -> dict:
        """Поисковые запросы (новый метод Oct 2025)"""
        return self._request("POST", "/v1/search-queries/text", {
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit
        })


def test_connection(account: str = "main") -> bool:
    """Тест подключения"""
    try:
        api = OzonSellerAPI(account)
        result = api.get_product_list(limit=1)
        if "error" in result:
            print(f"[{account}] Ошибка: {result}")
            return False
        print(f"[{account}] OK - найдено товаров: {result.get('result', {}).get('total', 'N/A')}")
        return True
    except Exception as e:
        print(f"[{account}] Исключение: {e}")
        return False


if __name__ == "__main__":
    print("=== Тест Ozon Seller API ===\n")

    for acc in ["main", "prices"]:
        test_connection(acc)

    print("\n=== Пример: получение цен ===")
    api = OzonSellerAPI("main")
    prices = api.get_prices(limit=5)
    print(json.dumps(prices, indent=2, ensure_ascii=False)[:1000])
