"""Parse endpoints for Ozon competitor prices"""

import uuid
import asyncio
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from loguru import logger

from api.services.sheets_client import GoogleSheetsClient

router = APIRouter()

# In-memory task storage (for MVP, use Redis in production)
tasks = {}


class ParseRequest(BaseModel):
    """Request to start parsing"""
    spreadsheet_id: str
    sheet_name: str = "Парсинг товаров"
    column_sku: str = "A"
    start_row: int = 2


class ParseResponse(BaseModel):
    """Response with task info"""
    task_id: str
    status: str
    message: str


class TaskStatus(BaseModel):
    """Task status response"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: str
    total: int
    processed: int
    errors: int
    started_at: Optional[str]
    completed_at: Optional[str]


@router.post("/parse", response_model=ParseResponse)
async def start_parsing(
    request: ParseRequest,
    background_tasks: BackgroundTasks,
    req: Request
):
    """
    Start parsing Ozon products from Google Sheets.

    Reads SKUs from column A, parses Ozon, writes results to columns B-H.
    """
    task_id = str(uuid.uuid4())[:8]

    tasks[task_id] = {
        "status": "pending",
        "progress": "0/0",
        "total": 0,
        "processed": 0,
        "errors": 0,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None
    }

    # Get parser service from app state
    parser = req.app.state.parser

    # Start background task
    background_tasks.add_task(
        run_parsing_task,
        task_id,
        request.spreadsheet_id,
        request.sheet_name,
        request.column_sku,
        request.start_row,
        parser
    )

    logger.info(f"Started parsing task {task_id} for sheet {request.spreadsheet_id}")

    return ParseResponse(
        task_id=task_id,
        status="started",
        message=f"Parsing started. Check status at /api/parse/status/{task_id}"
    )


@router.get("/parse/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get parsing task status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return TaskStatus(
        task_id=task_id,
        **task
    )


@router.post("/parse/test")
async def test_parse_single(sku: str, req: Request):
    """Test parsing a single SKU (for debugging)"""
    parser = req.app.state.parser
    result = await parser.parse_product(sku)
    return result


async def run_parsing_task(
    task_id: str,
    spreadsheet_id: str,
    sheet_name: str,
    column_sku: str,
    start_row: int,
    parser
):
    """Background task for parsing"""
    try:
        tasks[task_id]["status"] = "running"

        # Initialize Google Sheets client
        sheets = GoogleSheetsClient()

        # Read SKUs from sheet
        logger.info(f"Reading SKUs from {spreadsheet_id}/{sheet_name}")
        skus = sheets.read_skus(spreadsheet_id, sheet_name, column_sku, start_row)

        if not skus:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["progress"] = "No SKUs found"
            return

        total = len(skus)
        tasks[task_id]["total"] = total
        logger.info(f"Found {total} SKUs to parse")

        results = []
        errors = 0

        for i, sku in enumerate(skus, 1):
            try:
                # Parse product
                result = await parser.parse_product(sku)
                results.append(result)

                if result.get("error"):
                    errors += 1
                    logger.warning(f"[{i}/{total}] SKU {sku}: {result['error']}")
                else:
                    logger.info(f"[{i}/{total}] SKU {sku}: {result['price']} RUB")

                # Update progress
                tasks[task_id]["processed"] = i
                tasks[task_id]["errors"] = errors
                tasks[task_id]["progress"] = f"{i}/{total}"

                # Write result immediately to sheet
                row_num = start_row + i - 1
                sheets.write_result(spreadsheet_id, sheet_name, row_num, result)

                # Delay between requests (2-4 sec)
                if i < total:
                    await asyncio.sleep(2.5)

            except Exception as e:
                logger.error(f"Error parsing SKU {sku}: {e}")
                errors += 1
                tasks[task_id]["errors"] = errors

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"Task {task_id} completed: {total - errors}/{total} successful")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["progress"] = str(e)
