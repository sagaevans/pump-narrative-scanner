"""
Pump Narrative Scanner - Entry Point
A local Python research dashboard for monitoring newly created Solana meme tokens.
This tool is for research and screening only. It does not provide investment advice
and does not execute trades.
"""

import uvicorn
from datetime import datetime
from config import APP_HOST, APP_PORT
from modules.storage import init_db, insert_token, get_tokens
from modules.scoring import score_token


# Raw dummy token data (simulating data from a scanner before scoring)
RAW_SAMPLE_TOKENS = [
    {
        "name": "HantaCoin",
        "symbol": "HANTA",
        "mint_address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "description": "Hantavirus awareness token. Urgent public health alert on Solana.",
        "image_url": "https://example.com/hanta.png",
        "website": "",
        "twitter": "",
        "telegram": "",
        "pump_url": "https://pump.fun/EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
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
        "pump_url": "https://pump.fun/7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
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
        "pump_url": "https://pump.fun/9nEqaUcb16sQ3Tn1psbkWqyhPdLmfHWjKGymREjsAgTE",
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
        "pump_url": "https://pump.fun/3Kz9bQiEjY7pGmMJFbNHFxGL3n5HERxQ4nRGkfm5VoXy",
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
        "pump_url": "https://pump.fun/5pBz8Gxd4kEuj3Uvtwi9MxF72RcFhKUmj3cYzW9K4tRe",
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
        "pump_url": "https://pump.fun/A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2",
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
        "pump_url": "https://pump.fun/B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8s9T0u1V2w3",
    },
]


def process_and_seed_tokens():
    """
    Process raw token data through the narrative detector and scoring engine,
    then save scored results to SQLite.
    """
    existing = get_tokens()
    if len(existing) > 0:
        print(f"Database already contains {len(existing)} tokens. Skipping seed.")
        return

    print("Processing sample tokens through scoring engine...")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for token_data in RAW_SAMPLE_TOKENS:
        # Run through the scoring pipeline
        scores = score_token(token_data)

        # Merge raw token data with computed scores
        full_record = {
            **token_data,
            **scores,
            "created_at": now,
            "scanned_at": now,
        }

        # Insert into database
        insert_token(full_record)

        print(
            f"  [{scores['risk_level'].upper():6s}] {token_data['name']:20s} "
            f"| narrative={scores['narrative_category']:18s} "
            f"| final={scores['final_score']:.3f}"
        )

    print(f"\nInserted {len(RAW_SAMPLE_TOKENS)} scored tokens into database.")


def main():
    """Start the Pump Narrative Scanner dashboard."""
    print("=" * 60)
    print("  Pump Narrative Scanner")
    print("  Research & Screening Tool (NOT financial advice)")
    print("=" * 60)
    print()

    # Initialize database
    init_db()

    # Process and seed sample data
    process_and_seed_tokens()

    print(f"\nDashboard available at: http://{APP_HOST}:{APP_PORT}")
    print("Press Ctrl+C to stop.\n")
    uvicorn.run("web.app:app", host=APP_HOST, port=APP_PORT, reload=True)


if __name__ == "__main__":
    main()
