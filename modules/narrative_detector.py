"""
Narrative Detector module - identifies narrative patterns in token metadata.
Categorizes tokens into narrative types based on name, symbol, and description keywords.

This is a research tool only. It does not provide investment advice.
"""


# Narrative category definitions with associated keywords
NARRATIVE_KEYWORDS = {
    "disease_virus": [
        "virus", "hanta", "hantavirus", "covid", "corona", "ebola", "plague",
        "pandemic", "infection", "pathogen", "flu", "monkeypox", "disease",
        "outbreak", "contagion", "epidemic", "sars", "mrsa", "anthrax",
        "smallpox", "cholera", "tuberculosis", "malaria", "dengue",
    ],
    "lockdown_pandemic": [
        "lockdown", "quarantine", "mask", "vaccine", "vaxx", "pfizer",
        "moderna", "booster", "mandate", "isolation", "curfew",
        "social distancing", "wuhan", "lab leak", "gain of function",
        "shutdown", "stay home",
    ],
    "war": [
        "war", "missile", "bomb", "nuke", "nuclear", "military", "army",
        "invasion", "drone", "strike", "conflict", "battle", "attack",
        "defense", "weapon", "tank", "soldier", "combat", "airstrike",
        "sanctions", "nato", "troops",
    ],
    "politics": [
        "trump", "biden", "maga", "democrat", "republican", "election",
        "congress", "senate", "political", "president", "governor",
        "vote", "campaign", "impeach", "liberal", "conservative",
        "legislation", "policy", "capitol", "whitehouse",
    ],
    "ai": [
        "ai", "gpt", "neural", "bot", "agent", "llm", "openai", "chatgpt",
        "machine learning", "deep learning", "artificial intelligence",
        "transformer", "model", "cognitive", "sentient", "agi", "compute",
        "inference", "training", "nvidia",
    ],
    "celebrity": [
        "elon", "musk", "kanye", "drake", "taylor", "swift", "kardashian",
        "celebrity", "famous", "star", "influencer", "youtuber", "streamer",
        "mr beast", "mrbeast", "rogan", "podcast", "viral",
    ],
    "breaking_news": [
        "breaking", "urgent", "alert", "flash", "just in", "developing",
        "exclusive", "leaked", "confirmed", "official", "announcement",
        "revelation", "exposed", "scandal", "shocking",
    ],
    "finance_panic": [
        "crash", "recession", "inflation", "fed", "interest rate", "bank run",
        "collapse", "bailout", "default", "debt ceiling", "bear market",
        "liquidation", "margin call", "bubble", "panic", "dump", "rug",
        "bankrupt", "insolvent", "crisis",
    ],
    "animal_meme": [
        "dog", "doge", "shib", "cat", "frog", "pepe", "bird", "fish",
        "ape", "monkey", "bear", "bull", "whale", "hamster", "penguin",
        "panda", "tiger", "lion", "snake", "bonk", "wif", "hat",
        "floki", "inu", "neko", "meow", "bark", "quack",
    ],
    "absurd_meme": [
        "wojak", "chad", "based", "cope", "seethe", "ratio", "npc",
        "gigachad", "sigma", "grindset", "420", "69", "yolo", "moon",
        "lambo", "wagmi", "ngmi", "hodl", "diamond hands", "paper hands",
        "degen", "wen", "ser", "gm", "probably nothing", "goblin",
        "clown", "honk", "brrr", "stonks",
    ],
}

# Priority order: higher-priority narratives are matched first
NARRATIVE_PRIORITY = [
    "disease_virus",
    "lockdown_pandemic",
    "war",
    "breaking_news",
    "finance_panic",
    "politics",
    "ai",
    "celebrity",
    "animal_meme",
    "absurd_meme",
]


def detect_narrative(name: str, symbol: str, description: str = "") -> dict:
    """
    Analyze token metadata to detect narrative category.

    Args:
        name: Token name
        symbol: Token symbol/ticker
        description: Optional token description

    Returns:
        Dictionary with:
            - category: The detected narrative category string
            - matched_keywords: List of keywords that triggered the match
            - confidence: Confidence score (0.0-1.0) based on keyword density
    """
    text = f"{name} {symbol} {description}".lower()

    best_category = "unknown"
    best_matches = []
    best_confidence = 0.0

    for category in NARRATIVE_PRIORITY:
        keywords = NARRATIVE_KEYWORDS[category]
        matches = [kw for kw in keywords if kw in text]

        if matches:
            # Confidence based on number of keyword matches relative to category size
            confidence = min(len(matches) / 3.0, 1.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_category = category
                best_matches = matches

    return {
        "category": best_category,
        "matched_keywords": best_matches,
        "confidence": round(best_confidence, 3),
    }


def get_all_categories() -> list:
    """Return all supported narrative categories."""
    return NARRATIVE_PRIORITY + ["unknown"]


def is_high_risk_narrative(category: str) -> bool:
    """
    Determine if a narrative category is considered high-risk for pump schemes.

    Args:
        category: The narrative category string

    Returns:
        True if the category is commonly associated with pump-and-dump patterns
    """
    high_risk = {"disease_virus", "lockdown_pandemic", "war", "breaking_news", "finance_panic"}
    return category in high_risk
