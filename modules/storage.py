"""
Storage module - handles SQLite database operations for token research data.
"""

import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "coins.db")


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema with the tokens table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            symbol TEXT,
            mint_address TEXT UNIQUE NOT NULL,
            description TEXT,
            image_url TEXT,
            website TEXT,
            twitter TEXT,
            telegram TEXT,
            pump_url TEXT,
            narrative_category TEXT,
            narrative_score REAL DEFAULT 0.0,
            hantavirus_like_score REAL DEFAULT 0.0,
            momentum_score REAL DEFAULT 0.0,
            social_score REAL DEFAULT 0.0,
            safety_score REAL DEFAULT 0.0,
            freshness_score REAL DEFAULT 0.0,
            final_score REAL DEFAULT 0.0,
            risk_level TEXT,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DATABASE_PATH}")


def insert_token(token_data: dict):
    """
    Insert a token record into the database.

    Args:
        token_data: Dictionary containing token fields.
                    Must include 'mint_address' at minimum.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO tokens (
            name, symbol, mint_address, description, image_url,
            website, twitter, telegram, pump_url,
            narrative_category, narrative_score, hantavirus_like_score,
            momentum_score, social_score, safety_score, freshness_score,
            final_score, risk_level, reason, created_at, scanned_at
        ) VALUES (
            :name, :symbol, :mint_address, :description, :image_url,
            :website, :twitter, :telegram, :pump_url,
            :narrative_category, :narrative_score, :hantavirus_like_score,
            :momentum_score, :social_score, :safety_score, :freshness_score,
            :final_score, :risk_level, :reason, :created_at, :scanned_at
        )
    """, {
        "name": token_data.get("name"),
        "symbol": token_data.get("symbol"),
        "mint_address": token_data["mint_address"],
        "description": token_data.get("description"),
        "image_url": token_data.get("image_url"),
        "website": token_data.get("website"),
        "twitter": token_data.get("twitter"),
        "telegram": token_data.get("telegram"),
        "pump_url": token_data.get("pump_url"),
        "narrative_category": token_data.get("narrative_category"),
        "narrative_score": token_data.get("narrative_score", 0.0),
        "hantavirus_like_score": token_data.get("hantavirus_like_score", 0.0),
        "momentum_score": token_data.get("momentum_score", 0.0),
        "social_score": token_data.get("social_score", 0.0),
        "safety_score": token_data.get("safety_score", 0.0),
        "freshness_score": token_data.get("freshness_score", 0.0),
        "final_score": token_data.get("final_score", 0.0),
        "risk_level": token_data.get("risk_level"),
        "reason": token_data.get("reason"),
        "created_at": token_data.get("created_at"),
        "scanned_at": token_data.get("scanned_at"),
    })
    conn.commit()
    conn.close()


def get_tokens(limit: int = 100) -> list:
    """
    Retrieve tokens from the database, ordered by most recently scanned.

    Args:
        limit: Maximum number of tokens to return (default 100).

    Returns:
        List of token dictionaries.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tokens ORDER BY scanned_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
