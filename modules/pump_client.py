"""
Pump Client module - fetches newly created public meme token data.

This module collects public token metadata only.
It does NOT execute trades, connect wallets, or handle private keys.

Data sources (tried in order):
1. DexScreener public API (token-boosts/latest + batch token lookup)
2. DexScreener token-profiles/latest
3. pump.fun frontend-api-v3 (may be blocked by Cloudflare in some environments)
4. Fallback: Built-in sample data

The app always works locally even if all live sources fail.
"""

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Optional


# Data source tracking
DATA_SOURCE = "unknown"

# DexScreener public API endpoints (no auth required, reliable)
DEXSCREENER_BOOSTS_URL = "https://api.dexscreener.com/token-boosts/latest/v1"
DEXSCREENER_PROFILES_URL = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_TOKENS_URL = "https://api.dexscreener.com/tokens/v1/solana"

# pump.fun frontend API v3 (current version, may require browser-like access)
PUMP_FUN_API_V3_URL = "https://frontend-api-v3.pump.fun/coins/latest"

# Request timeout in seconds
REQUEST_TIMEOUT = 20

# Fallback sample data used when all live APIs are unavailable
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
        "created_at": "2025-01-15 10:30:00",
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
        "created_at": "2025-01-16 08:00:00",
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
        "created_at": "2025-01-16 12:00:00",
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
        "created_at": "2025-01-17 06:00:00",
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
        "created_at": "2025-01-17 14:30:00",
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
        "created_at": "2025-01-18 09:00:00",
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
        "created_at": "2025-01-18 11:00:00",
    },
]


def _log(msg: str):
    """Print a timestamped log message."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [pump_client] {msg}")


def _normalize_dexscreener_token(boost_data: dict, pair_data: Optional[dict] = None) -> Optional[dict]:
    """
    Normalize token data from DexScreener API into our standard format.

    Args:
        boost_data: Token boost/profile data from DexScreener
        pair_data: Optional pair data from batch token lookup

    Returns:
        Normalized token dictionary or None if invalid
    """
    address = boost_data.get("tokenAddress")
    if not address:
        return None

    # Extract from pair data (batch lookup)
    name = ""
    symbol = ""
    created_at = ""
    image_url = ""
    website = ""
    twitter = ""
    telegram = ""

    if pair_data:
        base = pair_data.get("baseToken", {})
        name = base.get("name", "")
        symbol = base.get("symbol", "")

        # Parse created timestamp (ms since epoch)
        created_ms = pair_data.get("pairCreatedAt")
        if created_ms and isinstance(created_ms, (int, float)):
            created_at = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Extract social/website from info
        info = pair_data.get("info", {})
        image_url = info.get("imageUrl", "")
        websites = info.get("websites", [])
        socials = info.get("socials", [])

        if websites:
            website = websites[0].get("url", "")
        for social in socials:
            if social.get("type") == "twitter" and not twitter:
                twitter = social.get("url", "")
            elif social.get("type") == "telegram" and not telegram:
                telegram = social.get("url", "")

    # Also check links from boost data
    links = boost_data.get("links", [])
    for link in links:
        link_type = link.get("type", "")
        link_url = link.get("url", "")
        if link_type == "twitter" and not twitter:
            twitter = link_url
        elif link_type == "telegram" and not telegram:
            telegram = link_url
        elif link_type == "website" and not website:
            website = link_url

    # Use icon from boost data if no image from pair lookup
    if not image_url:
        icon = boost_data.get("icon", "")
        if icon and icon.startswith("http"):
            image_url = icon

    # Description from boost data
    description = boost_data.get("description", "")

    if not created_at:
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Determine pump URL
    pump_url = f"https://pump.fun/coin/{address}" if address.endswith("pump") else f"https://dexscreener.com/solana/{address}"

    return {
        "name": name or address[:12],
        "symbol": symbol or "???",
        "mint_address": address,
        "description": description,
        "image_url": image_url,
        "website": website,
        "twitter": twitter,
        "telegram": telegram,
        "pump_url": pump_url,
        "created_at": created_at,
    }


def _normalize_pumpfun_token(raw: dict) -> Optional[dict]:
    """
    Normalize raw token data from pump.fun API into our standard format.

    Args:
        raw: Raw token data from pump.fun API

    Returns:
        Normalized token dictionary or None if invalid
    """
    mint = raw.get("mint") or raw.get("mint_address")
    if not mint:
        return None

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


async def _fetch_from_dexscreener(session: aiohttp.ClientSession, limit: int = 20) -> Optional[list]:
    """
    Fetch tokens from DexScreener public API.
    Uses token-boosts/latest + batch token lookup for full metadata.

    Returns:
        List of normalized tokens, or None if failed
    """
    _log(f"Trying DexScreener API: {DEXSCREENER_BOOSTS_URL}")

    try:
        # Step 1: Get latest boosted tokens (includes descriptions)
        async with session.get(DEXSCREENER_BOOSTS_URL) as resp:
            _log(f"  DexScreener boosts response: HTTP {resp.status}")
            if resp.status != 200:
                return None

            data = await resp.json()
            if not isinstance(data, list) or not data:
                _log("  DexScreener boosts returned empty data")
                return None

            # Filter to Solana tokens only
            solana_tokens = [t for t in data if t.get("chainId") == "solana"]
            _log(f"  Found {len(solana_tokens)} Solana tokens from boosts")

            if not solana_tokens:
                return None

            # Limit
            solana_tokens = solana_tokens[:limit]

        # Step 2: Batch lookup for name/symbol/info
        addresses = [t["tokenAddress"] for t in solana_tokens]
        batch_url = f"{DEXSCREENER_TOKENS_URL}/{','.join(addresses)}"
        _log(f"  Batch lookup: {len(addresses)} addresses via DexScreener tokens API")

        pair_lookup = {}
        try:
            async with session.get(batch_url) as resp2:
                if resp2.status == 200:
                    pairs = await resp2.json()
                    if isinstance(pairs, list):
                        for p in pairs:
                            base = p.get("baseToken", {})
                            addr = base.get("address", "")
                            if addr and addr not in pair_lookup:
                                pair_lookup[addr] = p
                        _log(f"  Batch lookup returned {len(pair_lookup)} unique token pairs")
                else:
                    _log(f"  Batch lookup returned HTTP {resp2.status}, continuing without pair data")
        except Exception as e:
            _log(f"  Batch lookup failed: {e}, continuing without pair data")

        # Step 3: Normalize and merge
        normalized = []
        for boost in solana_tokens:
            addr = boost["tokenAddress"]
            pair = pair_lookup.get(addr)
            token = _normalize_dexscreener_token(boost, pair)
            if token:
                normalized.append(token)

        if normalized:
            _log(f"  Successfully normalized {len(normalized)} tokens from DexScreener")
            return normalized

        return None

    except Exception as e:
        _log(f"  DexScreener error: {type(e).__name__}: {e}")
        return None


async def _fetch_from_dexscreener_profiles(session: aiohttp.ClientSession, limit: int = 20) -> Optional[list]:
    """
    Alternate DexScreener source: token-profiles/latest.
    Has less description data but still provides token addresses and links.

    Returns:
        List of normalized tokens, or None if failed
    """
    _log(f"Trying DexScreener profiles: {DEXSCREENER_PROFILES_URL}")

    try:
        async with session.get(DEXSCREENER_PROFILES_URL) as resp:
            _log(f"  DexScreener profiles response: HTTP {resp.status}")
            if resp.status != 200:
                return None

            data = await resp.json()
            if not isinstance(data, list) or not data:
                return None

            solana_tokens = [t for t in data if t.get("chainId") == "solana"]
            _log(f"  Found {len(solana_tokens)} Solana tokens from profiles")

            if not solana_tokens:
                return None

            solana_tokens = solana_tokens[:limit]

            # Batch lookup
            addresses = [t["tokenAddress"] for t in solana_tokens]
            batch_url = f"{DEXSCREENER_TOKENS_URL}/{','.join(addresses)}"
            pair_lookup = {}

            try:
                async with session.get(batch_url) as resp2:
                    if resp2.status == 200:
                        pairs = await resp2.json()
                        if isinstance(pairs, list):
                            for p in pairs:
                                base = p.get("baseToken", {})
                                addr = base.get("address", "")
                                if addr and addr not in pair_lookup:
                                    pair_lookup[addr] = p
                            _log(f"  Batch lookup returned {len(pair_lookup)} pairs")
            except Exception as e:
                _log(f"  Batch lookup failed: {e}")

            # Normalize - use profile data like boost data (similar structure)
            normalized = []
            for profile in solana_tokens:
                addr = profile["tokenAddress"]
                pair = pair_lookup.get(addr)
                # Profile data uses same structure as boost for normalization
                token = _normalize_dexscreener_token(profile, pair)
                if token:
                    normalized.append(token)

            if normalized:
                _log(f"  Successfully normalized {len(normalized)} tokens from profiles")
                return normalized

            return None

    except Exception as e:
        _log(f"  DexScreener profiles error: {type(e).__name__}: {e}")
        return None


async def _fetch_from_pumpfun(session: aiohttp.ClientSession, limit: int = 20) -> Optional[list]:
    """
    Fetch from pump.fun frontend API v3.
    This may be blocked by Cloudflare in server environments but works from browsers/local machines.

    Returns:
        List of normalized tokens, or None if failed
    """
    _log(f"Trying pump.fun API v3: {PUMP_FUN_API_V3_URL}")

    try:
        params = {"limit": limit, "offset": 0, "includeNsfw": "false"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Origin": "https://pump.fun",
            "Referer": "https://pump.fun/",
        }

        async with session.get(PUMP_FUN_API_V3_URL, params=params, headers=headers) as resp:
            _log(f"  pump.fun v3 response: HTTP {resp.status}")

            if resp.status != 200:
                return None

            text = await resp.text()
            if not text or len(text) < 10:
                _log(f"  pump.fun v3 returned empty body ({len(text)} bytes) - likely Cloudflare challenge")
                return None

            import json
            data = json.loads(text)

            tokens_raw = data if isinstance(data, list) else data.get("tokens", data.get("data", []))
            if not tokens_raw:
                _log("  pump.fun v3 returned no token data")
                return None

            normalized = []
            for raw in tokens_raw:
                token = _normalize_pumpfun_token(raw)
                if token:
                    normalized.append(token)

            if normalized:
                _log(f"  Successfully fetched {len(normalized)} tokens from pump.fun v3")
                return normalized

            return None

    except Exception as e:
        _log(f"  pump.fun v3 error: {type(e).__name__}: {e}")
        return None


async def fetch_latest_tokens(limit: int = 20) -> tuple:
    """
    Fetch the latest tokens using multiple public data sources.
    Tries sources in order of reliability, falls back gracefully.

    Args:
        limit: Number of tokens to fetch (default 20)

    Returns:
        Tuple of (tokens_list, data_source_string)
        data_source is one of: "dexscreener_boosts", "dexscreener_profiles",
                               "pumpfun_v3", "fallback"
    """
    global DATA_SOURCE

    _log("=" * 50)
    _log("Starting token fetch (multi-source)")
    _log("=" * 50)

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:

        # Source 1: DexScreener token-boosts/latest (most reliable, has descriptions)
        result = await _fetch_from_dexscreener(session, limit)
        if result:
            DATA_SOURCE = "live"
            _log(f"DATA_SOURCE=live (dexscreener_boosts, {len(result)} tokens)")
            return result, "dexscreener_boosts"

        # Source 2: DexScreener token-profiles/latest (alternate, less descriptions)
        result = await _fetch_from_dexscreener_profiles(session, limit)
        if result:
            DATA_SOURCE = "live"
            _log(f"DATA_SOURCE=live (dexscreener_profiles, {len(result)} tokens)")
            return result, "dexscreener_profiles"

        # Source 3: pump.fun v3 API (may be Cloudflare-blocked in server environments)
        result = await _fetch_from_pumpfun(session, limit)
        if result:
            DATA_SOURCE = "live"
            _log(f"DATA_SOURCE=live (pumpfun_v3, {len(result)} tokens)")
            return result, "pumpfun_v3"

    # All sources failed - use fallback
    DATA_SOURCE = "fallback"
    _log("")
    _log("All live sources failed. Using fallback sample data.")
    _log("DATA_SOURCE=fallback")
    _log("")
    return get_fallback_tokens(), "fallback"


def fetch_latest_tokens_sync(limit: int = 20) -> tuple:
    """
    Synchronous wrapper for fetch_latest_tokens.
    Useful when calling from non-async context (e.g., main.py startup).

    Args:
        limit: Number of tokens to fetch

    Returns:
        Tuple of (tokens_list, data_source_string)
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If event loop is already running, use fallback
            global DATA_SOURCE
            DATA_SOURCE = "fallback"
            return get_fallback_tokens(), "fallback"
        return loop.run_until_complete(fetch_latest_tokens(limit))
    except RuntimeError:
        return asyncio.run(fetch_latest_tokens(limit))


def get_fallback_tokens() -> list:
    """
    Return fallback dummy token data.
    Used when all live APIs are unavailable so the dashboard still works locally.

    Returns:
        List of sample token dictionaries
    """
    return FALLBACK_TOKENS.copy()


def get_data_source() -> str:
    """
    Return the current data source status.

    Returns:
        "live" if real data was loaded, "fallback" if sample data is being used,
        "unknown" if fetch hasn't been called yet
    """
    return DATA_SOURCE
