"""
FastAPI web application for the Pump Narrative Scanner dashboard.
Reads token data from SQLite via modules/storage.py.
"""

import sys
import os
import time
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

# Add project root to path so modules can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from modules.storage import get_tokens, insert_token
from modules.pump_client import fetch_latest_tokens, get_data_source
from modules.scoring import score_token

app = FastAPI(title="Pump Narrative Scanner", version="0.1.0")

# Setup paths
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": "Pump Narrative Scanner",
        "data_source": get_data_source(),
    }


@app.get("/api/tokens")
async def api_tokens(
    search: Optional[str] = Query(None, description="Search by name or symbol"),
    min_score: Optional[float] = Query(None, description="Minimum final score"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(100, description="Max tokens to return"),
):
    """
    API endpoint to retrieve tokens with optional filtering.

    Query params:
        search: Filter by name or symbol (case-insensitive partial match)
        min_score: Minimum final_score threshold
        risk_level: Filter by risk level (low, medium, high)
        limit: Maximum number of results
    """
    tokens = get_tokens(limit=limit)

    # Apply filters
    if search:
        search_lower = search.lower()
        tokens = [
            t for t in tokens
            if search_lower in (t.get("name") or "").lower()
            or search_lower in (t.get("symbol") or "").lower()
        ]

    if min_score is not None:
        tokens = [t for t in tokens if (t.get("final_score") or 0) >= min_score]

    if risk_level:
        risk_lower = risk_level.lower()
        tokens = [t for t in tokens if (t.get("risk_level") or "").lower() == risk_lower]

    return {"tokens": tokens, "count": len(tokens), "data_source": get_data_source()}


@app.post("/api/refresh")
async def api_refresh():
    """
    Fetch latest live token data, score it, and save to database.
    Returns summary of what was fetched and processed.
    """
    start_time = time.time()

    try:
        # Fetch live data using existing pump_client logic
        raw_tokens, source = await fetch_latest_tokens(limit=20)

        if not raw_tokens:
            return {
                "success": False,
                "data_source": "fallback",
                "raw_tokens_count": 0,
                "saved_tokens_count": 0,
                "scan_time": round(time.time() - start_time, 2),
                "message": "No token data available from any source.",
            }

        # Score and save each token
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        saved = 0

        for token_data in raw_tokens:
            scores = score_token(token_data)
            full_record = {
                **token_data,
                **scores,
                "scanned_at": now,
            }
            if not full_record.get("created_at"):
                full_record["created_at"] = now
            insert_token(full_record)
            saved += 1

        scan_time = round(time.time() - start_time, 2)

        return {
            "success": True,
            "data_source": "live" if source != "fallback" else "fallback",
            "raw_tokens_count": len(raw_tokens),
            "saved_tokens_count": saved,
            "scan_time": scan_time,
            "message": f"Fetched {len(raw_tokens)} tokens from {source}, scored and saved {saved} in {scan_time}s.",
        }

    except Exception as e:
        return {
            "success": False,
            "data_source": "error",
            "raw_tokens_count": 0,
            "saved_tokens_count": 0,
            "scan_time": round(time.time() - start_time, 2),
            "message": f"Refresh failed: {str(e)}",
        }
