#!/usr/bin/env python3
"""
Ozon Parser API Server
Запускается на локальном ПК, доступен через Cloudflare Tunnel

Использование:
  uvicorn api_server:app --host 0.0.0.0 --port 8080 --reload

Endpoints:
  GET  /health           - проверка работоспособности
  GET  /parse/{sku}      - парсинг одного SKU
  POST /parse/batch      - парсинг списка SKU
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auto_parser import OzonParser


# Глобальный инстанс парсера (singleton)
parser_instance: Optional[OzonParser] = None
parser_lock = asyncio.Lock()


class ParseResult(BaseModel):
    sku: str
    name: Optional[str] = None
    price: Optional[float] = None
    currency: str = "RUB"
    brand: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    availability: Optional[str] = None
    error: Optional[str] = None
    parsed_at: str


class BatchRequest(BaseModel):
    skus: list[str]


class BatchResponse(BaseModel):
    results: list[ParseResult]
    total: int
    successful: int
    failed: int


class HealthResponse(BaseModel):
    status: str
    browser_active: bool
    timestamp: str


async def get_parser() -> OzonParser:
    """Получить или создать инстанс парсера"""
    global parser_instance

    async with parser_lock:
        if parser_instance is None:
            parser_instance = OzonParser(headless=True, delay=2.0)
            await parser_instance.start()
            print("[API] Браузер инициализирован")
        return parser_instance


async def shutdown_parser():
    """Закрыть парсер при остановке сервера"""
    global parser_instance
    if parser_instance:
        await parser_instance.close()
        parser_instance = None
        print("[API] Браузер закрыт")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: запуск и остановка парсера"""
    yield
    await shutdown_parser()


# FastAPI приложение
app = FastAPI(
    title="Ozon Parser API",
    description="API для парсинга цен конкурентов с Ozon. Работает на локальном ПК через Cloudflare Tunnel.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS для доступа из Unify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка работоспособности API"""
    return HealthResponse(
        status="ok",
        browser_active=parser_instance is not None,
        timestamp=datetime.now().isoformat()
    )


@app.get("/parse/{sku}", response_model=ParseResult)
async def parse_single(sku: str):
    """Парсинг одного товара по SKU"""
    try:
        parser = await get_parser()
        result = await parser.parse_product(sku)

        return ParseResult(
            sku=result["sku"],
            name=result.get("name"),
            price=result.get("price"),
            currency=result.get("currency", "RUB"),
            brand=result.get("brand"),
            rating=result.get("rating"),
            reviews=result.get("reviews"),
            availability=result.get("availability"),
            error=result.get("error") if result.get("error") else None,
            parsed_at=result.get("parsed_at", datetime.now().isoformat())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse/batch", response_model=BatchResponse)
async def parse_batch(request: BatchRequest):
    """Парсинг списка SKU"""
    if not request.skus:
        raise HTTPException(status_code=400, detail="Список SKU пуст")

    if len(request.skus) > 50:
        raise HTTPException(status_code=400, detail="Максимум 50 SKU за запрос")

    try:
        parser = await get_parser()
        results = await parser.parse_batch(request.skus)

        parsed_results = []
        successful = 0
        failed = 0

        for r in results:
            parsed = ParseResult(
                sku=r["sku"],
                name=r.get("name"),
                price=r.get("price"),
                currency=r.get("currency", "RUB"),
                brand=r.get("brand"),
                rating=r.get("rating"),
                reviews=r.get("reviews"),
                availability=r.get("availability"),
                error=r.get("error") if r.get("error") else None,
                parsed_at=r.get("parsed_at", datetime.now().isoformat())
            )
            parsed_results.append(parsed)

            if r.get("error"):
                failed += 1
            else:
                successful += 1

        return BatchResponse(
            results=parsed_results,
            total=len(results),
            successful=successful,
            failed=failed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restart")
async def restart_browser():
    """Перезапуск браузера (если завис)"""
    global parser_instance

    async with parser_lock:
        if parser_instance:
            await parser_instance.close()
            parser_instance = None

        parser_instance = OzonParser(headless=True, delay=2.0)
        await parser_instance.start()

    return {"status": "restarted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
