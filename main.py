"""
Pump Narrative Scanner - Entry Point
A local Python research dashboard for monitoring newly created Solana meme tokens.
This tool is for research and screening only. It does not provide investment advice
and does not execute trades.
"""

import uvicorn
from datetime import datetime, timezone
from config import APP_HOST, APP_PORT
from modules.storage import init_db, insert_token, get_tokens
from modules.scoring import score_token
from modules.pump_client import fetch_latest_tokens_sync, get_data_source


def fetch_and_process_tokens():
    """
    Fetch token data from pump_client, analyze with narrative detector,
    score each token, and save results to SQLite.

    Falls back to sample data if all live sources are unavailable.
    """
    existing = get_tokens()
    if len(existing) > 0:
        print(f"Database already contains {len(existing)} tokens. Skipping initial fetch.")
        print(f"(Delete data/coins.db and restart to re-fetch fresh data)")
        return

    print("Fetching token data...\n")
    raw_tokens, source = fetch_latest_tokens_sync(limit=20)

    if not raw_tokens:
        print("No token data available from any source.")
        return

    # Clear data source summary
    print()
    print("-" * 60)
    if source == "fallback":
        print(f"  DATA_SOURCE = fallback")
        print(f"  Using built-in sample data ({len(raw_tokens)} tokens)")
    else:
        print(f"  DATA_SOURCE = live")
        print(f"  Source: {source} ({len(raw_tokens)} tokens)")
    print("-" * 60)
    print()

    print(f"Processing {len(raw_tokens)} tokens through scoring engine...\n")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0

    for token_data in raw_tokens:
        # Run through the narrative detection and scoring pipeline
        scores = score_token(token_data)

        # Merge raw token metadata with computed scores
        full_record = {
            **token_data,
            **scores,
            "scanned_at": now,
        }

        # Ensure created_at is set
        if not full_record.get("created_at"):
            full_record["created_at"] = now

        # Insert into database
        insert_token(full_record)
        inserted += 1

        print(
            f"  [{scores['risk_level'].upper():6s}] {token_data.get('name', '?')[:25]:25s} "
            f"| {scores['narrative_category']:18s} "
            f"| final={scores['final_score']:.4f}"
        )

    print(f"\nProcessed and saved {inserted} tokens to database.")


def main():
    """Start the Pump Narrative Scanner dashboard."""
    print("=" * 60)
    print("  Pump Narrative Scanner")
    print("  Research & Screening Tool (NOT financial advice)")
    print("=" * 60)
    print()

    # Initialize database
    init_db()

    # Fetch, analyze, score, and save tokens
    fetch_and_process_tokens()

    # Final status
    data_source = get_data_source()
    print()
    print(f"  DATA_SOURCE = {data_source}")
    print(f"  Dashboard available at: http://{APP_HOST}:{APP_PORT}")
    print()
    print("Press Ctrl+C to stop.\n")
    uvicorn.run("web.app:app", host=APP_HOST, port=APP_PORT, reload=True)


if __name__ == "__main__":
    main()
