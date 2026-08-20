SAFETY_CATEGORIES = {"Road", "Public Safety", "Infrastructure"}

CATEGORY_BASE_SEVERITY = {
    "Road": 20, "Water": 18, "Electricity": 16, "Garbage": 10,
    "Noise": 8, "Public Safety": 25, "Infrastructure": 22, "Other": 10,
}


def calculate_priority(
    category: str,
    sentiment: str,
    is_duplicate: bool,
    similarity_score: float,
    text: str,
) -> tuple[float, str]:
    severity = min(CATEGORY_BASE_SEVERITY.get(category, 10), 30)
    sentiment_scores = {"Neutral": 5, "Negative": 15, "Critical": 25}
    sentiment_score = sentiment_scores.get(sentiment, 5)

    dup_boost = 0
    if is_duplicate:
        dup_boost = min(10 + (similarity_score * 10), 20)

    safety_score = 0
    if category in SAFETY_CATEGORIES:
        safety_score = 15
    if sentiment == "Critical":
        safety_score = min(safety_score + 10, 25)

    total = severity + sentiment_score + dup_boost + safety_score
    total = min(max(total, 0), 100)

    if total >= 80:
        level = "Critical"
    elif total >= 60:
        level = "High"
    elif total >= 40:
        level = "Medium"
    else:
        level = "Low"

    return total, level
