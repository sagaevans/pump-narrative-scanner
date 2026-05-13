"""
Scoring module - assigns research scores to tokens based on narrative signals.
This is for research purposes only and does not constitute investment advice.
"""


def calculate_score(token_data: dict) -> float:
    """
    Calculate a research score for a token based on its characteristics.

    Args:
        token_data: Dictionary containing token metadata

    Returns:
        A score between 0.0 and 1.0 representing narrative strength
    """
    score = 0.0

    # Placeholder scoring logic - to be expanded
    if token_data.get("narrative") and token_data["narrative"] != "unknown":
        score += 0.3

    if token_data.get("name"):
        score += 0.1

    if token_data.get("symbol"):
        score += 0.1

    return min(score, 1.0)
