"""
Scoring module - assigns research scores to tokens based on narrative signals.

This is a research scoring system only.
It does NOT constitute financial advice and is NOT a trading system.

Final Score Formula:
    Final Score = Narrative Score * 0.30
                + Momentum Score * 0.25
                + Social Score * 0.15
                + Safety Score * 0.20
                + Freshness Score * 0.10
"""

from modules.narrative_detector import detect_narrative, is_high_risk_narrative


# Weights for final score calculation
WEIGHTS = {
    "narrative": 0.30,
    "momentum": 0.25,
    "social": 0.15,
    "safety": 0.20,
    "freshness": 0.10,
}

# Narrative category base scores (research heuristics)
NARRATIVE_BASE_SCORES = {
    "disease_virus": 0.95,
    "lockdown_pandemic": 0.90,
    "war": 0.88,
    "breaking_news": 0.85,
    "finance_panic": 0.82,
    "politics": 0.75,
    "ai": 0.80,
    "celebrity": 0.70,
    "animal_meme": 0.55,
    "absurd_meme": 0.50,
    "unknown": 0.20,
}


def calculate_narrative_score(token_data: dict) -> float:
    """
    Calculate the Narrative Score based on token metadata and detected narrative.

    Factors:
        - Narrative category strength (base score from category)
        - Detection confidence
        - Keyword density in name/description

    Args:
        token_data: Dictionary with token metadata (name, symbol, description)

    Returns:
        Score between 0.0 and 1.0
    """
    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    description = token_data.get("description", "")

    detection = detect_narrative(name, symbol, description)
    category = detection["category"]
    confidence = detection["confidence"]

    base_score = NARRATIVE_BASE_SCORES.get(category, 0.2)

    # Adjust by confidence - higher confidence means stronger signal
    score = base_score * (0.6 + 0.4 * confidence)

    return round(min(score, 1.0), 4)


def calculate_hantavirus_like_score(token_data: dict) -> float:
    """
    Calculate the Hantavirus-like Score - measures how closely a token resembles
    known pump-and-dump patterns (named after the Hantavirus token pump pattern).

    Factors:
        - High-risk narrative category
        - Urgency/fear keywords in description
        - Missing website or social links
        - Very short descriptions (low effort)

    Args:
        token_data: Dictionary with token metadata

    Returns:
        Score between 0.0 and 1.0 (higher = more pump-like)
    """
    score = 0.0

    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    description = token_data.get("description", "")

    detection = detect_narrative(name, symbol, description)
    category = detection["category"]

    # High-risk narrative categories get higher pump-like scores
    if is_high_risk_narrative(category):
        score += 0.35

    # Urgency/fear keywords suggest pump tactics
    urgency_keywords = [
        "urgent", "hurry", "limited", "last chance", "moon", "100x",
        "1000x", "guaranteed", "next", "buy now", "don't miss",
        "early", "presale", "airdrop", "free",
    ]
    text = f"{name} {description}".lower()
    urgency_matches = sum(1 for kw in urgency_keywords if kw in text)
    score += min(urgency_matches * 0.1, 0.3)

    # Missing website is a red flag
    if not token_data.get("website"):
        score += 0.15

    # Missing both twitter and telegram is suspicious
    if not token_data.get("twitter") and not token_data.get("telegram"):
        score += 0.1

    # Very short or empty description is low-effort (pump indicator)
    if len(description) < 20:
        score += 0.1

    return round(min(score, 1.0), 4)


def calculate_momentum_score(token_data: dict) -> float:
    """
    Calculate the Momentum Score - estimates potential viral momentum.

    In a live system this would use real-time trading data.
    For now, this uses heuristic signals from metadata.

    Factors:
        - Trending narrative category (AI, politics currently hot)
        - Description length (more effort = potentially more traction)
        - Has pump.fun URL (active on launchpad)
        - Has image (visual branding effort)

    Args:
        token_data: Dictionary with token metadata

    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0

    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    description = token_data.get("description", "")

    detection = detect_narrative(name, symbol, description)
    category = detection["category"]

    # Trending narratives get momentum bonus
    trending_categories = {"ai": 0.3, "politics": 0.25, "celebrity": 0.2, "disease_virus": 0.3}
    score += trending_categories.get(category, 0.1)

    # Description effort signals community engagement potential
    desc_len = len(description)
    if desc_len > 100:
        score += 0.2
    elif desc_len > 50:
        score += 0.15
    elif desc_len > 20:
        score += 0.1

    # Active on pump.fun launchpad
    if token_data.get("pump_url"):
        score += 0.15

    # Has image (branding effort)
    if token_data.get("image_url"):
        score += 0.1

    # Has website (project effort)
    if token_data.get("website"):
        score += 0.15

    return round(min(score, 1.0), 4)


def calculate_social_score(token_data: dict) -> float:
    """
    Calculate the Social Score - measures social media presence.

    Factors:
        - Has Twitter link
        - Has Telegram link
        - Has website
        - Celebrity/influencer narrative (implied social reach)

    Args:
        token_data: Dictionary with token metadata

    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0

    # Social link presence
    if token_data.get("twitter"):
        score += 0.3

    if token_data.get("telegram"):
        score += 0.25

    if token_data.get("website"):
        score += 0.2

    # Narrative implies social reach
    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    description = token_data.get("description", "")
    detection = detect_narrative(name, symbol, description)

    social_narratives = {"celebrity": 0.2, "politics": 0.15, "ai": 0.1}
    score += social_narratives.get(detection["category"], 0.05)

    return round(min(score, 1.0), 4)


def calculate_safety_score(token_data: dict) -> float:
    """
    Calculate the Safety Score - estimates how safe a token appears for research.

    Higher score = appears safer (less likely to be an obvious scam).

    Factors:
        - Has website (legitimate project indicator)
        - Has multiple social links
        - Description length and quality
        - NOT a high-risk narrative category
        - Not using urgency/FOMO language

    Args:
        token_data: Dictionary with token metadata

    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.3  # Base safety score

    # Website presence is a safety positive
    if token_data.get("website"):
        score += 0.2

    # Social presence adds legitimacy
    social_count = sum(1 for field in ["twitter", "telegram"] if token_data.get(field))
    score += social_count * 0.1

    # Good description suggests effort
    description = token_data.get("description", "")
    if len(description) > 80:
        score += 0.15
    elif len(description) > 40:
        score += 0.1

    # High-risk narratives reduce safety score
    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    detection = detect_narrative(name, symbol, description)

    if is_high_risk_narrative(detection["category"]):
        score -= 0.25

    # Urgency language reduces safety
    urgency_keywords = ["guaranteed", "100x", "1000x", "moon", "hurry", "last chance"]
    text = f"{name} {description}".lower()
    if any(kw in text for kw in urgency_keywords):
        score -= 0.15

    return round(max(min(score, 1.0), 0.0), 4)


def calculate_freshness_score(token_data: dict) -> float:
    """
    Calculate the Freshness Score - measures how new/fresh the token appears.

    In a live system, this would compare created_at against current time.
    For now, uses heuristic signals.

    Factors:
        - Has created_at timestamp (recently created tokens score higher)
        - Narrative timeliness (current events narratives = fresher)
        - Image and description present (newly launched with assets)

    Args:
        token_data: Dictionary with token metadata

    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.5  # Default freshness for dummy data

    # Timely narratives get freshness bonus
    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    description = token_data.get("description", "")
    detection = detect_narrative(name, symbol, description)

    timely_categories = {
        "breaking_news": 0.3,
        "disease_virus": 0.25,
        "war": 0.25,
        "politics": 0.2,
        "ai": 0.2,
    }
    score += timely_categories.get(detection["category"], 0.05)

    # Has image (newly launched tokens often have branding)
    if token_data.get("image_url"):
        score += 0.1

    # Has pump_url (active on launchpad = fresh)
    if token_data.get("pump_url"):
        score += 0.1

    return round(min(score, 1.0), 4)


def calculate_final_score(scores: dict) -> float:
    """
    Calculate the Final Score using the weighted formula.

    Final Score = Narrative Score * 0.30
                + Momentum Score * 0.25
                + Social Score * 0.15
                + Safety Score * 0.20
                + Freshness Score * 0.10

    Args:
        scores: Dictionary with individual score components:
            - narrative_score
            - momentum_score
            - social_score
            - safety_score
            - freshness_score

    Returns:
        Weighted final score between 0.0 and 1.0
    """
    final = (
        scores.get("narrative_score", 0.0) * WEIGHTS["narrative"]
        + scores.get("momentum_score", 0.0) * WEIGHTS["momentum"]
        + scores.get("social_score", 0.0) * WEIGHTS["social"]
        + scores.get("safety_score", 0.0) * WEIGHTS["safety"]
        + scores.get("freshness_score", 0.0) * WEIGHTS["freshness"]
    )
    return round(min(final, 1.0), 4)


def determine_risk_level(scores: dict) -> str:
    """
    Determine the risk level based on score components.

    Args:
        scores: Dictionary with score components including hantavirus_like_score
                and safety_score

    Returns:
        Risk level string: "low", "medium", or "high"
    """
    hantavirus = scores.get("hantavirus_like_score", 0.0)
    safety = scores.get("safety_score", 0.0)

    if hantavirus >= 0.6 or safety <= 0.3:
        return "high"
    elif hantavirus >= 0.35 or safety <= 0.5:
        return "medium"
    else:
        return "low"


def generate_reason(category: str, scores: dict, risk_level: str) -> str:
    """
    Generate a human-readable reason summarizing the scoring result.

    Args:
        category: Detected narrative category
        scores: Dictionary with all score components
        risk_level: The determined risk level

    Returns:
        Summary reason string
    """
    parts = []

    # Narrative description
    category_labels = {
        "disease_virus": "Disease/virus narrative",
        "lockdown_pandemic": "Lockdown/pandemic narrative",
        "war": "War/conflict narrative",
        "breaking_news": "Breaking news narrative",
        "finance_panic": "Finance panic narrative",
        "politics": "Political narrative",
        "ai": "AI/tech narrative",
        "celebrity": "Celebrity narrative",
        "animal_meme": "Animal meme narrative",
        "absurd_meme": "Absurd meme narrative",
        "unknown": "Unclassified narrative",
    }
    parts.append(category_labels.get(category, f"{category} narrative"))

    # Score highlights
    if scores.get("hantavirus_like_score", 0) >= 0.5:
        parts.append("high pump-like signals")
    if scores.get("momentum_score", 0) >= 0.7:
        parts.append("strong momentum indicators")
    if scores.get("social_score", 0) >= 0.7:
        parts.append("strong social presence")
    if scores.get("safety_score", 0) <= 0.35:
        parts.append("low safety signals")
    if scores.get("freshness_score", 0) >= 0.8:
        parts.append("very fresh launch")

    # Risk summary
    risk_descriptions = {
        "high": "elevated risk profile",
        "medium": "moderate risk profile",
        "low": "lower risk profile",
    }
    parts.append(risk_descriptions.get(risk_level, ""))

    return ". ".join(p for p in parts if p).capitalize()


def score_token(token_data: dict) -> dict:
    """
    Run the full scoring pipeline on a token.

    Args:
        token_data: Dictionary with token metadata (name, symbol, description, etc.)

    Returns:
        Dictionary with all computed scores, risk level, reason, and narrative category
    """
    # Detect narrative
    name = token_data.get("name", "")
    symbol = token_data.get("symbol", "")
    description = token_data.get("description", "")
    detection = detect_narrative(name, symbol, description)

    # Calculate individual scores
    narrative_score = calculate_narrative_score(token_data)
    hantavirus_like_score = calculate_hantavirus_like_score(token_data)
    momentum_score = calculate_momentum_score(token_data)
    social_score = calculate_social_score(token_data)
    safety_score = calculate_safety_score(token_data)
    freshness_score = calculate_freshness_score(token_data)

    scores = {
        "narrative_score": narrative_score,
        "hantavirus_like_score": hantavirus_like_score,
        "momentum_score": momentum_score,
        "social_score": social_score,
        "safety_score": safety_score,
        "freshness_score": freshness_score,
    }

    # Calculate final score
    final_score = calculate_final_score(scores)

    # Determine risk level
    risk_level = determine_risk_level(scores)

    # Generate reason
    reason = generate_reason(detection["category"], scores, risk_level)

    return {
        "narrative_category": detection["category"],
        "narrative_score": narrative_score,
        "hantavirus_like_score": hantavirus_like_score,
        "momentum_score": momentum_score,
        "social_score": social_score,
        "safety_score": safety_score,
        "freshness_score": freshness_score,
        "final_score": final_score,
        "risk_level": risk_level,
        "reason": reason,
    }
