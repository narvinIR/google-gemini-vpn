# Ozon Parser API - Dockerfile
# Uses official Playwright image

FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/

# Expose port
EXPOSE 8000

# Start FastAPI (as root to avoid permission issues with browser)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
