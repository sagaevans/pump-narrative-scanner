"""
Narrative Detector module - identifies narrative patterns in token metadata.
"""


def detect_narrative(name: str, symbol: str, description: str = "") -> str:
    """
    Analyze token metadata to detect narrative category.

    Args:
        name: Token name
        symbol: Token symbol/ticker
        description: Optional token description

    Returns:
        Detected narrative category string
    """
    # Placeholder - will be expanded with pattern matching logic
    text = f"{name} {symbol} {description}".lower()

    categories = {
        "meme": ["pepe", "doge", "shib", "wojak", "chad", "meme"],
        "ai": ["ai", "gpt", "neural", "bot", "agent"],
        "political": ["trump", "biden", "maga", "political"],
        "animal": ["cat", "dog", "frog", "bird", "fish"],
        "celebrity": ["elon", "musk", "celebrity"],
    }

    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "unknown"
