"""
Google Sheets Client
Read SKUs and write parsing results
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    logger.warning("gspread not available")


class GoogleSheetsClient:
    """Client for Google Sheets API"""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Column mapping for results
    COLUMNS = {
        "name": "B",
        "price": "C",
        "brand": "D",
        "rating": "E",
        "reviews": "F",
        "availability": "G",
        "parsed_at": "H",
        "error": "I"
    }

    def __init__(self):
        self.client: Optional[gspread.Client] = None
        self._init_client()

    def _init_client(self):
        """Initialize gspread client from environment"""
        if not GSPREAD_AVAILABLE:
            logger.error("gspread is not installed")
            return

        # Get credentials from environment variable
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

        if not creds_json:
            # Try to load from file
            creds_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials/service-account.json")
            if os.path.exists(creds_file):
                with open(creds_file, "r") as f:
                    creds_json = f.read()
            else:
                logger.warning("Google credentials not found. Set GOOGLE_CREDENTIALS_JSON env var")
                return

        try:
            creds_dict = json.loads(creds_json)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)
            self.client = gspread.authorize(credentials)
            logger.info("Google Sheets client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")

    def read_skus(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        column: str = "A",
        start_row: int = 2
    ) -> List[str]:
        """Read SKUs from column"""
        if not self.client:
            logger.error("Google Sheets client not initialized")
            return []

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)

            # Get all values from column
            col_index = ord(column.upper()) - ord('A') + 1
            values = worksheet.col_values(col_index)

            # Skip header and empty values
            skus = [v.strip() for v in values[start_row - 1:] if v and v.strip()]

            logger.info(f"Read {len(skus)} SKUs from {sheet_name}")
            return skus

        except Exception as e:
            logger.error(f"Error reading SKUs: {e}")
            return []

    def write_result(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        row: int,
        result: Dict
    ):
        """Write parsing result to row"""
        if not self.client:
            logger.error("Google Sheets client not initialized")
            return

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)

            # Prepare values for each column
            updates = []
            for field, col in self.COLUMNS.items():
                value = result.get(field, "")
                if isinstance(value, (int, float)) and value == 0 and field not in ["price", "rating", "reviews"]:
                    value = ""
                cell = f"{col}{row}"
                updates.append({
                    "range": cell,
                    "values": [[value]]
                })

            # Batch update
            worksheet.batch_update(updates)

        except Exception as e:
            logger.error(f"Error writing result to row {row}: {e}")

    def write_headers(self, spreadsheet_id: str, sheet_name: str):
        """Write column headers"""
        if not self.client:
            return

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)

            headers = [
                ("A1", "SKU"),
                ("B1", "Название"),
                ("C1", "Цена"),
                ("D1", "Бренд"),
                ("E1", "Рейтинг"),
                ("F1", "Отзывы"),
                ("G1", "Наличие"),
                ("H1", "Дата парсинга"),
                ("I1", "Ошибка")
            ]

            updates = [{"range": cell, "values": [[value]]} for cell, value in headers]
            worksheet.batch_update(updates)

            logger.info(f"Headers written to {sheet_name}")

        except Exception as e:
            logger.error(f"Error writing headers: {e}")
