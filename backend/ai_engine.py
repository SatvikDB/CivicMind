import re
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Category Keywords Mapping
CATEGORY_KEYWORDS = {
    "Road": ["pothole", "road", "asphalt", "tar", "speed breaker", "crack", "street", "highway", "lane", "pavement", "crater"],
    "Water": ["water", "pipeline", "leak", "pipe", "supply", "drinking", "tap", "contamination", "low pressure", "burst", "tank"],
    "Waste": ["garbage", "trash", "waste", "dump", "smell", "litter", "debris", "dustbin", "sanitation", "cleanliness", "heap", "stink"],
    "Streetlight": ["lamp", "light", "streetlight", "darkness", "bulb", "pole", "illumination", "night", "dark", "outage"],
    "Drainage": ["drain", "drainage", "sewage", "manhole", "overflow", "gutter", "blockage", "stagnant", "flooding", "sludge"],
    "Safety": ["wire", "electric", "hazard", "accident", "danger", "traffic", "signal", "stray", "crime", "cctv", "security", "fire", "spark"]
}

CRITICAL_KEYWORDS = ["live wire", "open manhole", "sparking", "collapse", "flood", "accident hazard", "toxic", "burst pipe", "high voltage", "electrocution", "fire"]
HIGH_KEYWORDS = ["blocked", "overflowing", "deep pothole", "no water", "dark street", "major", "severe", "hazardous", "stray dogs", "stagnant water"]
LOW_KEYWORDS = ["minor", "cosmetic", "paint", "signboard", "small litter", "leaves", "fade"]

URGENT_SENTIMENT_KEYWORDS = ["immediately", "urgent", "disaster", "terrible", "horrible", "unacceptable", "danger", "risk", "months", "weeks", "dying", "emergency"]
FRUSTRATED_KEYWORDS = ["again", "repeated", "nobody cares", "pathetic", "disappointed", "ignoring", "waste of tax", "worst"]

def classify_category(text: str, user_category: str = "Other") -> str:
    """Classify category if user provided 'Other' or refine matching."""
    text_lower = text.lower()
    
    if user_category and user_category != "Other":
        # Validate if text strongly suggests a different standard category
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(k in text_lower for k in keywords):
                return cat
        return user_category

    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for k in keywords if re.search(r'\b' + re.escape(k) + r'\b', text_lower))
        if score > 0:
            scores[cat] = score

    if scores:
        return max(scores, key=scores.get)
    return "Other"

def compute_similarity(new_text: str, existing_texts: List[str]) -> Tuple[float, int]:
    """Compute maximum cosine similarity with existing complaints using TF-IDF."""
    if not existing_texts:
        return 0.0, -1

    documents = existing_texts + [new_text]
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Cosine similarity of the last document (new_text) against all previous ones
        similarity_vector = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
        
        best_match_idx = int(similarity_vector.argmax())
        max_sim = float(similarity_vector[best_match_idx])
        return round(max_sim * 100, 1), best_match_idx
    except Exception:
        return 0.0, -1

def analyze_severity(text: str) -> str:
    """Determine issue severity level."""
    text_lower = text.lower()
    
    if any(k in text_lower for k in CRITICAL_KEYWORDS):
        return "Critical"
    elif any(k in text_lower for k in HIGH_KEYWORDS):
        return "High"
    elif any(k in text_lower for k in LOW_KEYWORDS):
        return "Low"
    return "Medium"

def analyze_sentiment(text: str) -> str:
    """Analyze citizen sentiment and tone."""
    text_lower = text.lower()
    exclamation_count = text.count("!")
    
    if any(k in text_lower for k in URGENT_SENTIMENT_KEYWORDS) or exclamation_count >= 2:
        return "Urgent"
    elif any(k in text_lower for k in FRUSTRATED_KEYWORDS):
        return "Frustrated"
    elif "not" in text_lower or "bad" in text_lower or "problem" in text_lower:
        return "Negative"
    return "Neutral"

def calculate_priority_score(severity: str, sentiment: str, similarity_score: float) -> Tuple[int, str]:
    """Calculate 0-100 priority score and level."""
    base_scores = {
        "Critical": 88,
        "High": 72,
        "Medium": 50,
        "Low": 25
    }
    score = base_scores.get(severity, 50)

    # Sentiment adjustment
    if sentiment == "Urgent":
        score += 8
    elif sentiment == "Frustrated":
        score += 5

    # Duplicate community volume boost (if score >= 50%)
    if similarity_score >= 75.0:
        score += 12
    elif similarity_score >= 50.0:
        score += 7

    # Ensure bounds
    score = max(10, min(99, int(score)))

    if score >= 80:
        level = "Critical"
    elif score >= 65:
        level = "High"
    elif score >= 45:
        level = "Medium"
    else:
        level = "Low"

    return score, level

def generate_recommendation(category: str, severity: str, priority_level: str, similarity_score: float, location: str) -> str:
    """Generate dynamic municipal action recommendation."""
    is_duplicate = similarity_score >= 50.0
    
    dup_prefix = f"⚠️ DUPLICATE ALERT ({similarity_score}% match with prior reports): " if is_duplicate else ""
    
    action_map = {
        "Road": {
            "Critical": f"Dispatch PWD Emergency Asphalt Crew within 6h to inspect and repair severe road hazard at {location}.",
            "High": f"Schedule Ward Road Maintenance Unit for asphalt patch work within 24h at {location}.",
            "Medium": f"Log road surface repair in weekly maintenance queue for {location}.",
            "Low": f"Add to routine quarterly PWD road inspection list."
        },
        "Water": {
            "Critical": f"ALERT WATER BOARD: Shut off damaged main line & dispatch repair squad within 4h at {location}.",
            "High": f"Deploy Water Supply Engineer to inspect pipeline leak/contamination at {location} within 12h.",
            "Medium": f"Schedule valve and pipe pressure audit at {location}.",
            "Low": f"Inspect water meter and public tap fittings during standard service run."
        },
        "Waste": {
            "Critical": f"Deploy Heavy Sanitation Truck & Disinfection Team immediately to clear bio-hazard waste at {location}.",
            "High": f"Assign Ward Sanitation Crew for bin clearance and debris removal within 12h at {location}.",
            "Medium": f"Schedule extra garbage collector pickup shift for {location}.",
            "Low": f"Include in standard daily street sweeping routine."
        },
        "Streetlight": {
            "Critical": f"EMERGENCY ELECTRIC: Dispatch Lineman immediately to fix exposed live wire/blackout pole at {location}.",
            "High": f"Assign Municipal Electrical Tech to replace faulty LED streetlight fixtures at {location} within 24h.",
            "Medium": f"Log streetlight maintenance ticket for next night-patrol inspection.",
            "Low": f"Queue non-essential light bulb replacement."
        },
        "Drainage": {
            "Critical": f"URGENT DRAINAGE TEAM: Deploy suction tanker & jetting machine to unblock flooding manhole at {location}.",
            "High": f"Dispatch Stormwater Drain Crew to clear silt and debris blockage at {location} within 12h.",
            "Medium": f"Schedule gutter desilting crew for {location}.",
            "Low": f"Add to pre-monsoon drainage cleaning checklist."
        },
        "Safety": {
            "Critical": f"DISPATCH SAFETY TASK FORCE & POLICE/FIRE ASSISTANCE to {location} immediately.",
            "High": f"Notify Traffic Control & Municipal Safety Inspector to resolve hazard at {location} within 12h.",
            "Medium": f"Inspect traffic signal / public safety installation at {location}.",
            "Low": f"Forward to community safety monitoring panel."
        }
    }

    category_actions = action_map.get(category, {})
    recommendation = category_actions.get(severity, f"Forward complaint to Municipal Ward Officer at {location} for field inspection.")
    
    return dup_prefix + recommendation

def process_complaint_ai(title: str, description: str, category_input: str, location: str, existing_complaints_texts: List[str]) -> Dict[str, Any]:
    """Full AI Engine Pipeline for a new complaint."""
    combined_text = f"{title}. {description}"
    
    # 1. Category Classification
    final_category = classify_category(combined_text, category_input)
    
    # 2. Duplicate Detection
    similarity_score, match_idx = compute_similarity(combined_text, existing_complaints_texts)
    
    # 3. Severity Analysis
    severity = analyze_severity(combined_text)
    
    # 4. Sentiment Analysis
    sentiment = analyze_sentiment(combined_text)
    
    # 5. Priority Score & Level
    priority_score, priority_level = calculate_priority_score(severity, sentiment, similarity_score)
    
    # 6. Action Recommendation
    recommendation = generate_recommendation(final_category, severity, priority_level, similarity_score, location)
    
    return {
        "category": final_category,
        "severity": severity,
        "sentiment": sentiment,
        "similarity_score": similarity_score,
        "matched_index": match_idx,
        "priority_score": priority_score,
        "priority_level": priority_level,
        "recommendation": recommendation
    }
