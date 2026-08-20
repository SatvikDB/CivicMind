CRITICAL_KEYWORDS = [
    "death", "died", "killed", "injury", "injured", "accident", "dangerous",
    "fatal", "hospital", "bleeding", "unconscious",
]

NEGATIVE_KEYWORDS = [
    "broken", "bad", "terrible", "worst", "horrible", "ugly", "disgusting",
    "annoying", "frustrated", "angry", "furious", "disappointed", "pathetic",
    "damaged", "ruined", "filthy", "stinking", "overflowing",
]


def analyze_sentiment(text: str) -> str:
    text_lower = text.lower()
    critical_count = sum(1 for kw in CRITICAL_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)

    if critical_count >= 2:
        return "Critical"
    if critical_count >= 1 or negative_count >= 3:
        return "Negative"
    if negative_count >= 1:
        return "Negative"
    return "Neutral"
