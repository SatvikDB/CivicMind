# Person 5 -- AI/NLP Engine
# Automatic category detection, entity extraction, fuzzy spelling resilience, Hinglish support & Explainability.

import re
import math
import logging
from typing import Optional
from collections import Counter
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Data Structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class CategoryResult:
    """Result of automatic category detection."""
    category: str
    confidence: float
    sub_category: Optional[str] = None
    matched_keywords: list = field(default_factory=list)
    all_scores: dict = field(default_factory=dict)
    explanation: str = ""

@dataclass
class ComplaintAnalysis:
    """Full NLP analysis of a complaint text."""
    original_text: str
    cleaned_text: str
    category: CategoryResult
    keywords: list
    location_mentions: list
    urgency_indicators: list
    complaint_type: str          # "infrastructure" | "social" | "environmental" | "other"
    language_quality: str        # "clear" | "moderate" | "poor"
    word_count: int
    char_count: int
    detected_entities: dict = field(default_factory=dict)

# ──────────────────────────────────────────────────────────────────────────────
# Category Knowledge Base (English + Hinglish + Synonyms)
# ──────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Road": [
        "road", "pothole", "street", "highway", "pavement", "tarmac",
        "asphalt", "footpath", "sidewalk", "lane", "traffic", "signal",
        "speed breaker", "damaged road", "cracked road", "broken road",
        "divider", "median", "junction", "intersection", "crossroad",
        "flyover", "underpass", "overbridge", "road repair", "road broken",
        "road damage", "bad road", "rough road", "bumpy road", "crater",
        # Hinglish / Regional terms
        "sadak", "gaddha", "rasta", "khadda", "gadhe", "sadke", "patthar"
    ],
    "Water": [
        "water", "leak", "leaking", "pipe", "pipeline", "drain", "drainage",
        "flood", "flooding", "sewage", "sewer", "stagnant", "overflow",
        "tap", "supply", "shortage", "contamination", "dirty water",
        "muddy water", "no water", "water problem", "water issue",
        "waterlogging", "blocked drain", "broken pipe", "burst pipe",
        "water tank", "borewell", "tubewell", "hand pump", "puddle",
        "drinking water", "chlorine", "gutter",
        # Hinglish / Regional terms
        "pani", "paani", "nalka", "nal", "nalli", "nalla", "gutter ka pani", "jal"
    ],
    "Electricity": [
        "electricity", "power", "light", "streetlight", "street light",
        "electric", "wire", "pole", "transformer", "outage", "blackout",
        "power cut", "no power", "no light", "voltage", "short circuit",
        "spark", "naked wire", "dangling wire", "electric shock",
        "power failure", "load shedding", "meter", "bill", "connection",
        "high voltage", "low voltage", "fuse",
        # Hinglish / Regional terms
        "bijli", "batti", "khamba", "taar", "bijli gul", "light chali gayi", "current"
    ],
    "Garbage": [
        "garbage", "waste", "trash", "rubbish", "litter", "dumping",
        "dustbin", "bin", "collection", "sweeping", "dirty", "filth",
        "heap", "pile", "burning waste", "open dump", "solid waste",
        "waste disposal", "sanitation", "cleaning", "hygienic", "stink",
        "smell", "odor", "rot", "decompose", "cleanliness", "unhygienic",
        "plastic waste", "debris",
        # Hinglish / Regional terms
        "kachra", "kachra peti", "safai", "badboo", "gandagi", "kooda", "kudedan"
    ],
    "Noise": [
        "noise", "loud", "sound", "music", "speaker", "party", "horn",
        "construction noise", "noise pollution", "disturbance", "disturbing",
        "nuisance", "blasting", "drilling", "honking", "barking", "factory noise",
        "night noise", "generator", "vibration", "decibel", "loudspeaker",
        # Hinglish / Regional terms
        "shor", "awaz", "bhopu", "dhwani pradooshan"
    ],
    "Safety": [
        "accident", "unsafe", "danger", "dangerous", "hazard", "risk",
        "threat", "crime", "theft", "robbery", "assault", "violence",
        "eve teasing", "harassment", "chain snatching", "security",
        "cctv", "camera", "patrol", "police", "dark area", "no light",
        "open manhole", "exposed wire", "falling tree", "collapse",
        "broken fence", "unsafe building", "wall collapse", "snatching",
        # Hinglish / Regional terms
        "chori", "khatra", "khatarnak", "gunda", "marpeet", "suraksha"
    ],
    "Environment": [
        "pollution", "smoke", "air pollution", "dust", "chemical",
        "industrial", "factory", "emission", "toxic", "hazardous",
        "deforestation", "tree cutting", "illegal cutting", "green",
        "environment", "ecological", "soil", "contamination", "effluent",
        "sewage disposal", "burning", "fire", "wildfire", "river pollution",
        # Hinglish / Regional terms
        "dhuan", "dhuwa", "pradooshan", "ped katna", "hawa kharab"
    ],
    "Health": [
        "hospital", "medical", "health", "disease", "infection", "virus",
        "malaria", "dengue", "cholera", "typhoid", "mosquito", "epidemic",
        "outbreak", "doctor", "nurse", "medicine", "ambulance", "emergency",
        "clinic", "dispensary", "sanitation", "hygiene", "contaminated food",
        "food poisoning", "rat", "rodent", "pest", "infestation",
        # Hinglish / Regional terms
        "machhar", "bimari", "swasthya", "davai", "ilaj"
    ],
    "Infrastructure": [
        "building", "construction", "bridge", "wall", "structure",
        "boundary", "park", "playground", "public toilet", "toilet",
        "school", "college", "government office", "post office",
        "library", "community hall", "abandoned", "dilapidated",
        "broken", "maintenance", "repair needed", "renovation",
        # Hinglish / Regional terms
        "shauchalaya", "imarat", "pul", "deewar"
    ],
    "Transport": [
        "bus", "auto", "rickshaw", "taxi", "cab", "vehicle", "parking",
        "illegal parking", "station", "stop", "route", "schedule",
        "frequency", "overcrowding", "public transport", "metro",
        "train", "railway", "platform", "ticket", "fare", "traffic jam",
        # Hinglish / Regional terms
        "gaadi", "chakka jam", "tempo"
    ],
    "Animal": [
        "dog", "stray dog", "stray cat", "animal", "cattle", "cow",
        "buffalo", "pig", "monkey", "snake", "bite", "attack",
        "stray animal", "animal menace", "rabies", "street animal",
        "poultry", "bird flu", "pest control",
        # Hinglish / Regional terms
        "kutta", "kutte", "bandar", "saand", "gay", "saanp"
    ],
    "Civic Services": [
        "certificate", "ration card", "id", "document", "license",
        "permit", "approval", "noc", "grievance", "complaint",
        "government service", "municipality", "panchayat", "ward",
        "corporator", "mla", "mp", "official", "bribe", "corruption",
        "pending", "delay", "slow service", "not responding",
        # Hinglish / Regional terms
        "rishwat", "ghoos", "sarkari daftar", "adhikari"
    ]
}

LOCATION_INDICATORS = [
    "near", "beside", "behind", "opposite", "in front of", "adjacent",
    "around", "at", "on", "along", "between", "next to", "close to",
    "road", "street", "lane", "colony", "nagar", "sector", "block",
    "ward", "area", "zone", "district", "city", "town", "village",
    "mohalla", "locality", "neighborhood", "circle", "chowk", "crossing",
    "market", "bazaar", "gate", "junction"
]

URGENCY_KEYWORDS = [
    "urgent", "immediately", "emergency", "danger", "critical", "severe",
    "serious", "accident", "injury", "death", "collapsed", "broken",
    "explosion", "fire", "flood", "very bad", "worst", "extreme",
    "weeks", "months", "years", "long time", "repeated", "again and again",
    "nobody listening", "no action", "ignored", "please help", "sos",
    "life threatening", "risk to life", "jaldi", "turant", "khatra"
]

# ──────────────────────────────────────────────────────────────────────────────
# Fuzzy Matching / Typo Resilience (Levenshtein Distance)
# ──────────────────────────────────────────────────────────────────────────────

def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute edit distance between two short strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def is_fuzzy_match(word: str, target: str, max_dist: int = 1) -> bool:
    """Check if word is within allowed edit distance of target (ignores tiny words)."""
    if len(target) <= 4:
        return word == target
    if abs(len(word) - len(target)) > max_dist:
        return False
    return _levenshtein_distance(word, target) <= max_dist


# ──────────────────────────────────────────────────────────────────────────────
# Text Preprocessing (Fault-Tolerant)
# ──────────────────────────────────────────────────────────────────────────────

class TextPreprocessor:
    STOP_WORDS = {
        "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
        "he","she","it","they","them","what","which","who","this","that","these",
        "those","am","is","are","was","were","be","been","being","have","has","had",
        "do","does","did","will","would","could","should","may","might","shall","can",
        "a","an","the","and","but","or","nor","for","yet","so","at","by","from","up",
        "as","in","into","through","during","before","after","above","below","to","of",
        "on","off","over","under","again","then","here","there","when","where","why",
        "how","both","each","few","more","most","other","some","such","no","only",
        "same","than","too","very","just","not","also","about","with","while",
        "hai","hain","ko","se","ka","ki","ke","par","mein","ye","woh"
    }

    def clean(self, text: Optional[str]) -> str:
        if not text or not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenise(self, text: Optional[str]) -> list:
        if not text:
            return []
        cleaned = self.clean(text)
        return [w for w in cleaned.split() if w not in self.STOP_WORDS and len(w) > 2]

    def extract_ngrams(self, tokens: list, n: int = 2) -> list:
        if len(tokens) < n:
            return []
        return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


# ──────────────────────────────────────────────────────────────────────────────
# TF-IDF Keyword Extractor
# ──────────────────────────────────────────────────────────────────────────────

class TFIDFExtractor:
    def __init__(self, preprocessor: TextPreprocessor):
        self._prep = preprocessor
        self._corpus_freq = self._build_corpus_freq()
        self._num_docs = len(CATEGORY_KEYWORDS)

    def _build_corpus_freq(self) -> Counter:
        freq: Counter = Counter()
        for keywords in CATEGORY_KEYWORDS.values():
            for kw in keywords:
                freq.update(kw.lower().split())
        return freq

    def _idf(self, term: str) -> float:
        df = self._corpus_freq.get(term, 0) + 1
        return math.log((self._num_docs + 1) / df)

    def top_keywords(self, text: Optional[str], top_n: int = 8) -> list:
        if not text:
            return []
        cleaned = self._prep.clean(text)
        tokens = self._prep.tokenise(cleaned)
        if not tokens:
            return []
        tf = Counter(tokens)
        total = sum(tf.values()) or 1
        scores = {t: (c / total) * self._idf(t) for t, c in tf.items()}
        return [w for w, _ in sorted(scores.items(), key=lambda x: -x[1])[:top_n]]


# ──────────────────────────────────────────────────────────────────────────────
# Category Detector with Fuzzy + Subcategory Logic
# ──────────────────────────────────────────────────────────────────────────────

class CategoryDetector:
    def __init__(self, preprocessor: TextPreprocessor):
        self._prep = preprocessor

    def detect(self, text: Optional[str]) -> CategoryResult:
        if not text or not str(text).strip():
            return CategoryResult(
                category="Other",
                confidence=0.0,
                matched_keywords=[],
                all_scores={},
                explanation="No text provided for categorization."
            )

        cleaned = self._prep.clean(str(text))
        tokens = cleaned.split()
        bigrams = self._prep.extract_ngrams(tokens, 2)
        trigrams = self._prep.extract_ngrams(tokens, 3)
        all_terms = set(tokens + bigrams + trigrams)

        scores = {}
        matched_kws = {}

        for category, keywords in CATEGORY_KEYWORDS.items():
            score = 0.0
            hits = []
            for kw in keywords:
                kw_lower = kw.lower()
                
                # 1. Exact ngram match
                if kw_lower in all_terms:
                    wcount = len(kw_lower.split())
                    weight = 1.0 + (wcount - 1) * 0.6
                    score += weight
                    hits.append(kw)
                # 2. Substring match
                elif kw_lower in cleaned:
                    score += 0.5
                    hits.append(kw)
                # 3. Fuzzy match for single token typos (e.g., 'pothol' -> 'pothole')
                elif len(kw_lower.split()) == 1 and len(kw_lower) >= 5:
                    for t in tokens:
                        if is_fuzzy_match(t, kw_lower, max_dist=1):
                            score += 0.75
                            hits.append(f"{kw} (typo: {t})")
                            break

            scores[category] = score
            matched_kws[category] = hits

        total_score = sum(scores.values()) or 1.0
        best_cat = max(scores, key=scores.get)
        best_score = scores[best_cat]

        if best_score < 0.4:
            return CategoryResult(
                category="Other",
                confidence=0.25,
                matched_keywords=[],
                all_scores={k: round(v, 3) for k, v in scores.items()},
                explanation="Insufficient matching civic keywords detected. Classified as General/Other."
            )

        confidence = min(round(best_score / max(total_score * 0.55, 1.0), 3), 1.0)
        sub_category = self._get_sub_category(best_cat, matched_kws[best_cat])
        
        hit_summary = ", ".join(matched_kws[best_cat][:3])
        explanation = f"Classified as '{best_cat}' ({int(confidence*100)}% confidence) based on matches: {hit_summary}."

        return CategoryResult(
            category=best_cat,
            confidence=confidence,
            sub_category=sub_category,
            matched_keywords=matched_kws[best_cat][:6],
            all_scores={k: round(v, 3) for k, v in sorted(scores.items(), key=lambda x: -x[1])[:5]},
            explanation=explanation
        )

    def _get_sub_category(self, category: str, keywords: list) -> Optional[str]:
        sub_map = {
            "Road": {
                "pothole": "Pothole / Road Damage", "gaddha": "Pothole / Road Damage",
                "signal": "Traffic Signal Malfunction", "footpath": "Footpath Obstruction",
                "flyover": "Bridge/Flyover Maintenance", "speed breaker": "Speed Breaker Issue"
            },
            "Water": {
                "leak": "Pipeline Leak", "pipeline": "Pipeline Leak", "flood": "Waterlogging / Flooding",
                "sewage": "Sewage Overflow", "gutter": "Drainage / Gutter Clog",
                "shortage": "Water Supply Shortage", "contamination": "Water Contamination"
            },
            "Electricity": {
                "streetlight": "Street Light Defect", "outage": "Power Outage", "bijli": "Power Cut",
                "wire": "Faulty/Dangerous Wiring", "transformer": "Transformer Spark/Damage"
            },
            "Garbage": {
                "dumping": "Illegal Waste Dumping", "burning": "Open Waste Burning",
                "bin": "Overflowing Dustbin", "collection": "Garbage Collection Delay"
            },
            "Safety": {
                "open manhole": "Open Manhole Danger", "accident": "Accident Hazard",
                "theft": "Theft / Security Threat", "snatching": "Street Crime"
            }
        }
        cat_sub = sub_map.get(category, {})
        for kw in keywords:
            kw_clean = kw.split()[0].lower()
            for key, label in cat_sub.items():
                if key in kw.lower():
                    return label
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Location Extractor
# ──────────────────────────────────────────────────────────────────────────────

class LocationExtractor:
    LOCATION_PATTERN = re.compile(
        r'\b(?:near|beside|at|in|on|behind|opposite|next to|close to|adjacent to|along|between)\s+([A-Za-z0-9\s]{2,35})',
        re.IGNORECASE
    )
    PROPER_NOUN_PATTERN = re.compile(
        r'\b([A-Z][a-z0-9]+(?:\s[A-Z][a-z0-9]+)*)\s*(?:road|street|lane|nagar|colony|sector|block|ward|area|circle|chowk|crossing|park|market|bazaar|school|college|hospital|station|gate)\b',
        re.IGNORECASE
    )

    def extract(self, text: Optional[str]) -> list:
        if not text:
            return []
        text_str = str(text)
        locations = []
        for m in self.LOCATION_PATTERN.finditer(text_str):
            loc = m.group(1).strip()
            # Clean up trailing punctuation or conjunctions
            loc = re.split(r'[,.\n]| and | with ', loc)[0].strip()
            if 2 < len(loc) < 40 and not loc.lower() in ("the", "a", "an", "this", "that"):
                locations.append(loc)

        for m in self.PROPER_NOUN_PATTERN.finditer(text_str):
            loc = m.group(0).strip()
            if loc not in locations:
                locations.append(loc)

        return list(dict.fromkeys(locations))[:5]


# ──────────────────────────────────────────────────────────────────────────────
# Urgency Detector
# ──────────────────────────────────────────────────────────────────────────────

class UrgencyDetector:
    def detect(self, text: Optional[str]) -> list:
        if not text:
            return []
        text_lower = str(text).lower()
        return [kw for kw in URGENCY_KEYWORDS if kw in text_lower]


# ──────────────────────────────────────────────────────────────────────────────
# Complaint Type & Language Quality
# ──────────────────────────────────────────────────────────────────────────────

COMPLAINT_TYPE_MAP = {
    "infrastructure": ["Road", "Water", "Electricity", "Infrastructure", "Transport"],
    "social":         ["Safety", "Noise", "Animal", "Civic Services"],
    "environmental":  ["Garbage", "Environment", "Health"],
}

def classify_complaint_type(category: str) -> str:
    for ctype, cats in COMPLAINT_TYPE_MAP.items():
        if category in cats:
            return ctype
    return "other"

def assess_language_quality(text: Optional[str]) -> str:
    if not text:
        return "poor"
    wc = len(str(text).split())
    if wc >= 15:
        return "clear"
    elif wc >= 6:
        return "moderate"
    return "poor"


# ──────────────────────────────────────────────────────────────────────────────
# Main AI Engine Facade
# ──────────────────────────────────────────────────────────────────────────────

class AIEngine:
    """
    Facade orchestrating all Person 5 NLP sub-modules.
    Fault-tolerant against empty, non-string, typo-ridden, and Hinglish inputs.
    """

    def __init__(self):
        self._preprocessor       = TextPreprocessor()
        self._category_detector  = CategoryDetector(self._preprocessor)
        self._keyword_extractor  = TFIDFExtractor(self._preprocessor)
        self._location_extractor = LocationExtractor()
        self._urgency_detector   = UrgencyDetector()
        logger.info("AIEngine initialised (fault-tolerant NLP pipeline ready)")

    def analyse(self, text: Optional[str]) -> ComplaintAnalysis:
        safe_text = str(text).strip() if text is not None else ""
        if not safe_text:
            safe_text = "No description provided"

        cleaned        = self._preprocessor.clean(safe_text)
        category       = self._category_detector.detect(safe_text)
        keywords       = self._keyword_extractor.top_keywords(safe_text)
        locations      = self._location_extractor.extract(safe_text)
        urgency        = self._urgency_detector.detect(safe_text)
        complaint_type = classify_complaint_type(category.category)
        lang_quality   = assess_language_quality(safe_text)

        analysis = ComplaintAnalysis(
            original_text=safe_text,
            cleaned_text=cleaned,
            category=category,
            keywords=keywords,
            location_mentions=locations,
            urgency_indicators=urgency,
            complaint_type=complaint_type,
            language_quality=lang_quality,
            word_count=len(safe_text.split()),
            char_count=len(safe_text),
            detected_entities={
                "locations": locations,
                "urgency_signals": urgency,
                "sub_category": category.sub_category or "General"
            }
        )
        return analysis

    def detect_category(self, text: Optional[str]) -> CategoryResult:
        return self._category_detector.detect(text)

    def extract_keywords(self, text: Optional[str], top_n: int = 8) -> list:
        return self._keyword_extractor.top_keywords(text, top_n)

    def to_dict(self, analysis: ComplaintAnalysis) -> dict:
        return {
            "original_text": analysis.original_text,
            "cleaned_text": analysis.cleaned_text,
            "category": {
                "category": analysis.category.category,
                "confidence": analysis.category.confidence,
                "sub_category": analysis.category.sub_category,
                "matched_keywords": analysis.category.matched_keywords,
                "all_scores": analysis.category.all_scores,
                "explanation": analysis.category.explanation,
            },
            "keywords": analysis.keywords,
            "location_mentions": analysis.location_mentions,
            "urgency_indicators": analysis.urgency_indicators,
            "complaint_type": analysis.complaint_type,
            "language_quality": analysis.language_quality,
            "word_count": analysis.word_count,
            "char_count": analysis.char_count,
            "detected_entities": analysis.detected_entities,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Module Singleton
# ──────────────────────────────────────────────────────────────────────────────
_engine_instance: Optional[AIEngine] = None

def get_engine() -> AIEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AIEngine()
    return _engine_instance


if __name__ == "__main__":
    engine = AIEngine()
    tests = [
        "There is a big pothol near college gate",  # typo test
        "sadak par bahut bada gaddha hai Sector 12 mein",  # Hinglish test
        "Open electric wire hanging near school gate! EMERGENCY",
        "",  # empty test
    ]
    for t in tests:
        res = engine.analyse(t)
        print(f"\nText: {t}")
        print(f"Category: {res.category.category} ({res.category.confidence:.0%}) -> {res.category.sub_category}")
        print(f"Explanation: {res.category.explanation}")
        print(f"Locations: {res.location_mentions}")
