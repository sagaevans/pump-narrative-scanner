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

# Data source settings
# DexScreener public API (primary source, no auth required)
DEXSCREENER_BOOSTS_URL = os.getenv("DEXSCREENER_BOOSTS_URL", "https://api.dexscreener.com/token-boosts/latest/v1")
DEXSCREENER_PROFILES_URL = os.getenv("DEXSCREENER_PROFILES_URL", "https://api.dexscreener.com/token-profiles/latest/v1")
DEXSCREENER_TOKENS_URL = os.getenv("DEXSCREENER_TOKENS_URL", "https://api.dexscreener.com/tokens/v1/solana")

# pump.fun API v3 (secondary source, may be Cloudflare-blocked in some environments)
PUMP_API_URL = os.getenv("PUMP_API_URL", "https://frontend-api-v3.pump.fun/coins/latest")

# Fetch settings
PUMP_API_TIMEOUT = int(os.getenv("PUMP_API_TIMEOUT", "20"))
PUMP_FETCH_LIMIT = int(os.getenv("PUMP_FETCH_LIMIT", "20"))
