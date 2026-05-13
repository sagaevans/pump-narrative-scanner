"""
Pump Client module - fetches newly created public meme token data.

This module collects public token metadata only.
It does NOT execute trades, connect wallets, or handle private keys.

Data source: pump.fun public API (read-only, no authentication required)
Fallback: Returns dummy sample data if live data is unavailable.
"""

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Optional


# Public API endpoint for recently created tokens on pump.fun
PUMP_FUN_API_URL = "https://frontend-api-v2.pump.fun/coins/latest"
PUMP_FUN_COIN_URL = "https://frontend-api-v2.pump.fun/coins"

# Request timeout in seconds
REQUEST_TIMEOUT = 15

# Fallback sample data used when live API is unavailable
FALLBACK_TOKENS = [
    {
        "name": "HantaCoin",
        "symbol": "HANTA",
        "mint_address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "description": "Hantavirus awareness token. Urgent public health alert on Solana.",
        "image_url": "https://example.com/hanta.png",
        "website": "",
        "twitter": "",
        "telegram": "",
        "pump_url": "https://pump.fun/coin/EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "created_at": "2025-01-15T10:30:00Z",
    },
    {
        "name": "AI Agent Token",
        "symbol": "AIGT",
        "mint_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "description": "Decentralized AI agent framework on Solana. Building the future of autonomous compute.",
        "image_url": "https://example.com/aigt.png",
        "website": "https://aiagenttoken.io",
        "twitter": "https://twitter.com/aigt_sol",
        "telegram": "",
        "pump_url": "https://pump.fun/coin/7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "created_at": "2025-01-16T08:00:00Z",
    },
    {
        "name": "TrumpMAGA2025",
        "symbol": "MAGA25",
        "mint_address": "9nEqaUcb16sQ3Tn1psbkWqyhPdLmfHWjKGymREjsAgTE",
        "description": "Political meme token. Make America Great Again 2025 on chain.",
        "image_url": "https://example.com/maga25.png",
        "website": "",
        "twitter": "https://twitter.com/maga25sol",
        "telegram": "",
        "pump_url": "https://pump.fun/coin/9nEqaUcb16sQ3Tn1psbkWqyhPdLmfHWjKGymREjsAgTE",
        "created_at": "2025-01-16T12:00:00Z",
    },
    {
        "name": "CatSolana",
        "symbol": "CATSOL",
        "mint_address": "3Kz9bQiEjY7pGmMJFbNHFxGL3n5HERxQ4nRGkfm5VoXy",
        "description": "Cats rule Solana. Community-driven cat meme. Meow to the moon.",
        "image_url": "https://example.com/catsol.png",
        "website": "https://catsol.meme",
        "twitter": "https://twitter.com/catsolana",
        "telegram": "https://t.me/catsolana",
        "pump_url": "https://pump.fun/coin/3Kz9bQiEjY7pGmMJFbNHFxGL3n5HERxQ4nRGkfm5VoXy",
        "created_at": "2025-01-17T06:00:00Z",
    },
    {
        "name": "ElonRocket",
        "symbol": "ELON",
        "mint_address": "5pBz8Gxd4kEuj3Uvtwi9MxF72RcFhKUmj3cYzW9K4tRe",
        "description": "To the moon with Elon. Rocket-themed celebrity meme token.",
        "image_url": "https://example.com/elonrocket.png",
        "website": "",
        "twitter": "https://twitter.com/elonrocket_sol",
        "telegram": "",
        "pump_url": "https://pump.fun/coin/5pBz8Gxd4kEuj3Uvtwi9MxF72RcFhKUmj3cYzW9K4tRe",
        "created_at": "2025-01-17T14:30:00Z",
    },
    {
        "name": "WarStrike",
        "symbol": "WSTR",
        "mint_address": "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2",
        "description": "Military conflict token. Missile strike breaking news.",
        "image_url": "https://example.com/warstrike.png",
        "website": "",
        "twitter": "",
        "telegram": "",
        "pump_url": "https://pump.fun/coin/A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2",
        "created_at": "2025-01-18T09:00:00Z",
    },
    {
        "name": "CrashBankRun",
        "symbol": "CRASH",
        "mint_address": "B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8s9T0u1V2w3",
        "description": "Bank run panic. Market crash imminent. Last chance to get in.",
        "image_url": "",
        "website": "",
        "twitter": "",
        "telegram": "",
        "pump_url": "https://pump.fun/coin/B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8s9T0u1V2w3",
        "created_at": "2025-01-18T11:00:00Z",
    },
]


def _normalize_token(raw: dict) -> Optional[dict]:
    """
    Normalize raw API token data into our standard format.

    Args:
        raw: Raw token data from pump.fun API

    Returns:
        Normalized token dictionary or None if invalid
    """
    mint = raw.get("mint") or raw.get("mint_address")
    if not mint:
        return None

    # Parse created timestamp
    created_at = raw.get("created_timestamp")
    if created_at and isinstance(created_at, (int, float)):
        created_at = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    elif not created_at:
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "name": raw.get("name") or raw.get("token_name") or "",
        "symbol": raw.get("symbol") or raw.get("ticker") or "",
        "mint_address": mint,
        "description": raw.get("description") or "",
        "image_url": raw.get("image_uri") or raw.get("image_url") or "",
        "website": raw.get("website") or "",
        "twitter": raw.get("twitter") or "",
        "telegram": raw.get("telegram") or "",
        "pump_url": f"https://pump.fun/coin/{mint}",
        "created_at": created_at,
    }


async def fetch_latest_tokens(limit: int = 20) -> list:
    """
    Fetch the latest tokens from the pump.fun public API.

    Args:
        limit: Number of tokens to fetch (default 20)

    Returns:
        List of normalized token dictionaries.
        Falls back to dummy data if the API is unreachable.
    """
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            params = {"limit": limit, "offset": 0, "includeNsfw": "false"}
            headers = {
                "User-Agent": "PumpNarrativeScanner/0.1 (research tool)",
                "Accept": "application/json",
            }

            async with session.get(PUMP_FUN_API_URL, params=params, headers=headers) as response:
                if response.status != 200:
                    print(f"[pump_client] API returned status {response.status}, using fallback data.")
                    return get_fallback_tokens()

                data = await response.json()

                # API may return a list directly or nested under a key
                tokens_raw = data if isinstance(data, list) else data.get("tokens", data.get("data", []))

                if not tokens_raw:
                    print("[pump_client] API returned empty data, using fallback.")
                    return get_fallback_tokens()

                normalized = []
                for raw in tokens_raw:
                    token = _normalize_token(raw)
                    if token:
                        normalized.append(token)

                if not normalized:
                    print("[pump_client] No valid tokens from API, using fallback.")
                    return get_fallback_tokens()

                print(f"[pump_client] Fetched {len(normalized)} tokens from live API.")
                return normalized

    except asyncio.TimeoutError:
        print("[pump_client] API request timed out, using fallback data.")
        return get_fallback_tokens()
    except aiohttp.ClientError as e:
        print(f"[pump_client] Connection error: {e}, using fallback data.")
        return get_fallback_tokens()
    except Exception as e:
        print(f"[pump_client] Unexpected error: {e}, using fallback data.")
        return get_fallback_tokens()


def fetch_latest_tokens_sync(limit: int = 20) -> list:
    """
    Synchronous wrapper for fetch_latest_tokens.
    Useful when calling from non-async context (e.g., main.py startup).

    Args:
        limit: Number of tokens to fetch

    Returns:
        List of normalized token dictionaries
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If event loop is already running, use fallback
            # (this happens inside FastAPI/uvicorn)
            return get_fallback_tokens()
        return loop.run_until_complete(fetch_latest_tokens(limit))
    except RuntimeError:
        # No event loop exists, create one
        return asyncio.run(fetch_latest_tokens(limit))


def get_fallback_tokens() -> list:
    """
    Return fallback dummy token data.
    Used when the live API is unavailable so the dashboard still works locally.

    Returns:
        List of sample token dictionaries
    """
    print("[pump_client] Using fallback sample data.")
    return FALLBACK_TOKENS.copy()
