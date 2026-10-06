from similarity import find_duplicates
from sentiment_engine import analyze_sentiment
from priority_engine import calculate_priority
from recommendation_engine import recommend_action

CATEGORY_KEYWORDS = {
    "Road": ["pothole", "road", "street", "pavement", "traffic", "signal", "speed breaker", "asphalt"],
    "Water": ["water", "leak", "pipe", "drainage", "flood", "sewage", "tap", "borewell"],
    "Electricity": ["power", "electric", "light", "wire", "outage", "transformer", "current", "bulb"],
    "Garbage": ["garbage", "waste", "trash", "dump", "clean", "bin", "overflow", "litter"],
    "Noise": ["noise", "loud", "sound", "music", "construction", "honking", "factory"],
    "Public Safety": ["danger", "unsafe", "crime", "assault", "theft", "attack", "goons", "drug"],
    "Infrastructure": ["building", "bridge", "collapse", "crack", "wall", "structure", "demolition"],
}


def detect_category(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return "Other"


def analyze_complaint(complaint_text: str, existing_complaints: list[dict]) -> dict:
    category = detect_category(complaint_text)
    sentiment = analyze_sentiment(complaint_text)
    is_dup, dup_id, sim_score = find_duplicates(complaint_text, existing_complaints)
    priority_score, priority_level = calculate_priority(
        category=category,
        sentiment=sentiment,
        is_duplicate=is_dup,
        similarity_score=sim_score,
        text=complaint_text,
    )
    action = recommend_action(category, priority_level)

    return {
        "category": category,
        "sentiment": sentiment,
        "is_duplicate": is_dup,
        "duplicate_of": dup_id,
        "similarity_score": round(sim_score, 4),
        "priority_score": round(priority_score, 2),
        "priority_level": priority_level,
        "recommended_action": action,
    }
