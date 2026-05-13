"""
Configuration for Pump Narrative Scanner.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# App settings
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/coins.db")

# Research settings
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))

# Pump.fun API settings (public, read-only)
PUMP_API_URL = os.getenv("PUMP_API_URL", "https://frontend-api-v2.pump.fun/coins/latest")
PUMP_API_TIMEOUT = int(os.getenv("PUMP_API_TIMEOUT", "15"))
PUMP_FETCH_LIMIT = int(os.getenv("PUMP_FETCH_LIMIT", "20"))
