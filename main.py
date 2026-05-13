"""
Pump Narrative Scanner - Entry Point
A local Python research dashboard for monitoring newly created Solana meme tokens.
This tool is for research and screening only. It does not provide investment advice
and does not execute trades.
"""

import uvicorn
from config import APP_HOST, APP_PORT
from modules.storage import init_db, insert_token, get_tokens


SAMPLE_TOKENS = [
    {
        "name": "DogWifHat",
        "symbol": "WIF",
        "mint_address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "description": "A dog with a hat. The internet's favorite meme.",
        "image_url": "https://example.com/wif.png",
        "website": "https://dogwifhat.com",
        "twitter": "https://twitter.com/dogwifcoin",
        "telegram": "",
        "pump_url": "https://pump.fun/EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "narrative_category": "meme",
        "narrative_score": 0.85,
        "hantavirus_like_score": 0.1,
        "momentum_score": 0.72,
        "social_score": 0.9,
        "safety_score": 0.6,
        "freshness_score": 0.3,
        "final_score": 0.74,
        "risk_level": "medium",
        "reason": "Strong meme narrative with high social presence",
        "created_at": "2025-01-15 10:30:00",
        "scanned_at": "2025-01-15 10:35:00",
    },
    {
        "name": "AI Agent Token",
        "symbol": "AIGT",
        "mint_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "description": "Decentralized AI agent framework on Solana.",
        "image_url": "https://example.com/aigt.png",
        "website": "https://aiagenttoken.io",
        "twitter": "https://twitter.com/aigt_sol",
        "telegram": "",
        "pump_url": "https://pump.fun/7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "narrative_category": "ai",
        "narrative_score": 0.92,
        "hantavirus_like_score": 0.05,
        "momentum_score": 0.88,
        "social_score": 0.75,
        "safety_score": 0.7,
        "freshness_score": 0.95,
        "final_score": 0.82,
        "risk_level": "low",
        "reason": "Trending AI narrative with fresh launch and strong momentum",
        "created_at": "2025-01-16 08:00:00",
        "scanned_at": "2025-01-16 08:05:00",
    },
    {
        "name": "TrumpMAGA2025",
        "symbol": "MAGA25",
        "mint_address": "9nEqaUcb16sQ3Tn1psbkWqyhPdLmfHWjKGymREjsAgTE",
        "description": "Political meme token supporting Trump 2025.",
        "image_url": "https://example.com/maga25.png",
        "website": "",
        "twitter": "https://twitter.com/maga25sol",
        "telegram": "",
        "pump_url": "https://pump.fun/9nEqaUcb16sQ3Tn1psbkWqyhPdLmfHWjKGymREjsAgTE",
        "narrative_category": "political",
        "narrative_score": 0.78,
        "hantavirus_like_score": 0.65,
        "momentum_score": 0.55,
        "social_score": 0.6,
        "safety_score": 0.3,
        "freshness_score": 0.4,
        "final_score": 0.48,
        "risk_level": "high",
        "reason": "Political narrative with high pump risk and low safety signals",
        "created_at": "2025-01-16 12:00:00",
        "scanned_at": "2025-01-16 12:10:00",
    },
    {
        "name": "CatSolana",
        "symbol": "CATSOL",
        "mint_address": "3Kz9bQiEjY7pGmMJFbNHFxGL3n5HERxQ4nRGkfm5VoXy",
        "description": "Cats rule Solana. Community-driven cat meme.",
        "image_url": "https://example.com/catsol.png",
        "website": "https://catsol.meme",
        "twitter": "https://twitter.com/catsolana",
        "telegram": "",
        "pump_url": "https://pump.fun/3Kz9bQiEjY7pGmMJFbNHFxGL3n5HERxQ4nRGkfm5VoXy",
        "narrative_category": "animal",
        "narrative_score": 0.7,
        "hantavirus_like_score": 0.2,
        "momentum_score": 0.45,
        "social_score": 0.5,
        "safety_score": 0.55,
        "freshness_score": 0.8,
        "final_score": 0.58,
        "risk_level": "medium",
        "reason": "Animal meme narrative, moderately fresh with average social presence",
        "created_at": "2025-01-17 06:00:00",
        "scanned_at": "2025-01-17 06:02:00",
    },
    {
        "name": "ElonRocket",
        "symbol": "ELON",
        "mint_address": "5pBz8Gxd4kEuj3Uvtwi9MxF72RcFhKUmj3cYzW9K4tRe",
        "description": "To the moon with Elon. Rocket-themed meme token.",
        "image_url": "https://example.com/elonrocket.png",
        "website": "",
        "twitter": "https://twitter.com/elonrocket_sol",
        "telegram": "",
        "pump_url": "https://pump.fun/5pBz8Gxd4kEuj3Uvtwi9MxF72RcFhKUmj3cYzW9K4tRe",
        "narrative_category": "celebrity",
        "narrative_score": 0.68,
        "hantavirus_like_score": 0.8,
        "momentum_score": 0.35,
        "social_score": 0.4,
        "safety_score": 0.2,
        "freshness_score": 0.6,
        "final_score": 0.38,
        "risk_level": "high",
        "reason": "Celebrity-bait narrative with very high pump signals and low safety",
        "created_at": "2025-01-17 14:30:00",
        "scanned_at": "2025-01-17 14:32:00",
    },
]


def seed_sample_data():
    """Insert sample tokens into the database for testing."""
    existing = get_tokens()
    if len(existing) > 0:
        print(f"Database already contains {len(existing)} tokens. Skipping seed.")
        return

    print("Inserting sample tokens for testing...")
    for token in SAMPLE_TOKENS:
        insert_token(token)
    print(f"Inserted {len(SAMPLE_TOKENS)} sample tokens.")


def main():
    """Start the Pump Narrative Scanner dashboard."""
    print("Starting Pump Narrative Scanner...")

    # Initialize database and seed sample data
    init_db()
    seed_sample_data()

    print(f"Dashboard available at: http://{APP_HOST}:{APP_PORT}")
    uvicorn.run("web.app:app", host=APP_HOST, port=APP_PORT, reload=True)


if __name__ == "__main__":
    main()
