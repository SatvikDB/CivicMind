# Person 6 -- Sentiment Analysis Engine
# Sentiment scoring with VADER-style lexicon, Emoji intensity extraction, Hinglish emotion handling & TextBlob blend.

import re
import math
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Data Structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SentimentResult:
    """Full sentiment analysis result for a complaint."""
    text: str
    polarity: float              # -1.0 (very negative) to +1.0 (very positive)
    subjectivity: float          # 0.0 (objective) to 1.0 (subjective)
    sentiment_label: str         # "Critical" | "Negative" | "Neutral" | "Positive"
    intensity: float             # 0.0 -> 1.0, how emotionally charged
    emotion_tags: list           # ["anger", "fear", "frustration", "urgency"]
    negative_phrases: list       # matched negative phrases
    positive_phrases: list       # matched positive phrases
    intensifier_count: int       # count of "very", "extremely" etc.
    analysis_strategy: str       # "textblob" | "lexicon" | "emoji+lexicon"
    urgency_boost_applied: bool = False


# ──────────────────────────────────────────────────────────────────────────────
# Sentiment Lexicons (English + Hinglish + Emojis)
# ──────────────────────────────────────────────────────────────────────────────

# (phrase, polarity_weight, emotion_tag)
NEGATIVE_LEXICON = [
    # Critical / Danger / Life risk
    ("accident",          -0.9,  "fear"),
    ("collapsed",         -1.0,  "fear"),
    ("death",             -1.0,  "fear"),
    ("explosion",         -1.0,  "fear"),
    ("fire",              -0.85, "fear"),
    ("flood",             -0.85, "fear"),
    ("life threatening",  -1.0,  "fear"),
    ("risk to life",      -1.0,  "fear"),
    ("injury",            -0.9,  "fear"),
    ("dangerous",         -0.85, "fear"),
    ("hazard",            -0.8,  "fear"),
    ("unsafe",            -0.75, "fear"),
    ("electric shock",    -0.95, "fear"),
    ("naked wire",        -0.9,  "fear"),
    ("broken wire",       -0.85, "fear"),
    ("open manhole",      -0.9,  "fear"),
    ("khatarnak",         -0.85, "fear"),
    ("jaan ka khatra",    -1.0,  "fear"),

    # Anger / Frustration / Negligence
    ("nobody listening",  -0.8,  "anger"),
    ("no action",         -0.75, "anger"),
    ("ignored",           -0.7,  "anger"),
    ("negligence",        -0.8,  "anger"),
    ("corruption",        -0.85, "anger"),
    ("bribe",             -0.8,  "anger"),
    ("disgusting",        -0.75, "anger"),
    ("pathetic",          -0.7,  "anger"),
    ("terrible",          -0.65, "anger"),
    ("horrible",          -0.7,  "anger"),
    ("awful",             -0.65, "anger"),
    ("outrageous",        -0.8,  "anger"),
    ("intolerable",       -0.75, "anger"),
    ("unacceptable",      -0.7,  "anger"),
    ("shameful",          -0.7,  "anger"),
    ("koi sun nahi raha", -0.85, "anger"),
    ("pareshan ho gaye",  -0.75, "frustration"),
    ("bahut bekar",       -0.7,  "anger"),
    ("sharam karo",       -0.8,  "anger"),

    # Frustration / Persistence
    ("again and again",   -0.65, "frustration"),
    ("repeated",          -0.6,  "frustration"),
    ("weeks",             -0.4,  "frustration"),
    ("months",            -0.55, "frustration"),
    ("years",             -0.65, "frustration"),
    ("long time",         -0.5,  "frustration"),
    ("still not",         -0.55, "frustration"),
    ("not resolved",      -0.6,  "frustration"),
    ("pending",           -0.45, "frustration"),
    ("delay",             -0.45, "frustration"),
    ("waste of time",     -0.6,  "frustration"),
    ("fed up",            -0.65, "frustration"),
    ("baar baar",         -0.6,  "frustration"),

    # General negative
    ("bad",               -0.4,  "negative"),
    ("worst",             -0.7,  "negative"),
    ("poor",              -0.4,  "negative"),
    ("broken",            -0.45, "negative"),
    ("damaged",           -0.45, "negative"),
    ("dirty",             -0.5,  "negative"),
    ("filthy",            -0.6,  "negative"),
    ("stench",            -0.55, "negative"),
    ("smell",             -0.35, "negative"),
    ("stink",             -0.55, "negative"),
    ("leak",              -0.4,  "negative"),
    ("overflow",          -0.5,  "negative"),
    ("blocked",           -0.4,  "negative"),
    ("pothole",           -0.4,  "negative"),
    ("problem",           -0.35, "negative"),
    ("issue",             -0.25, "negative"),

    # Urgency markers
    ("urgent",            -0.6,  "urgency"),
    ("immediately",       -0.55, "urgency"),
    ("emergency",         -0.8,  "urgency"),
    ("sos",               -0.9,  "urgency"),
    ("please help",       -0.6,  "urgency"),
    ("critical",          -0.75, "urgency"),
    ("severe",            -0.7,  "urgency"),
    ("serious",           -0.6,  "urgency"),
    ("extreme",           -0.65, "urgency"),
    ("jaldi karo",        -0.6,  "urgency"),
    ("turant",            -0.65, "urgency"),
]

POSITIVE_LEXICON = [
    ("resolved",       +0.7,  "positive"),
    ("fixed",          +0.65, "positive"),
    ("improved",       +0.6,  "positive"),
    ("clean",          +0.5,  "positive"),
    ("working",        +0.4,  "positive"),
    ("good",           +0.5,  "positive"),
    ("excellent",      +0.7,  "positive"),
    ("thank",          +0.6,  "positive"),
    ("appreciate",     +0.65, "positive"),
    ("satisfied",      +0.6,  "positive"),
    ("great",          +0.6,  "positive"),
    ("well maintained",+0.7,  "positive"),
    ("repaired",       +0.65, "positive"),
    ("dhanyavad",      +0.6,  "positive"),
    ("shukriya",       +0.6,  "positive"),
]

EMOJI_SENTIMENT_MAP = {
    "🚨": (-0.8, "urgency"),
    "⚠️": (-0.6, "urgency"),
    "🔥": (-0.7, "fear"),
    "😡": (-0.8, "anger"),
    "🤬": (-0.9, "anger"),
    "💀": (-1.0, "fear"),
    "😭": (-0.6, "frustration"),
    "🤮": (-0.7, "anger"),
    "💩": (-0.6, "negative"),
    "👍": (+0.6, "positive"),
    "🙏": (+0.5, "positive"),
    "😊": (+0.5, "positive"),
    "❤️": (+0.7, "positive"),
    "✅": (+0.6, "positive"),
}

INTENSIFIERS = [
    "very", "extremely", "highly", "severely", "badly", "terribly",
    "awfully", "absolutely", "completely", "totally", "utterly",
    "dangerously", "critically", "deeply", "strongly", "bahut", "bohot"
]

NEGATORS = ["not", "no", "never", "neither", "nothing", "without", "nahi", "mat"]


# ──────────────────────────────────────────────────────────────────────────────
# Lexicon-based Sentiment Scorer
# ──────────────────────────────────────────────────────────────────────────────

class LexiconSentimentScorer:
    def __init__(self):
        self._neg_lex = NEGATIVE_LEXICON
        self._pos_lex = POSITIVE_LEXICON
        self._intensifiers = set(INTENSIFIERS)
        self._negators = set(NEGATORS)

    def score(self, text: Optional[str]) -> SentimentResult:
        if not text or not str(text).strip():
            return SentimentResult(
                text="", polarity=0.0, subjectivity=0.0,
                sentiment_label="Neutral", intensity=0.0, emotion_tags=[],
                negative_phrases=[], positive_phrases=[], intensifier_count=0,
                analysis_strategy="lexicon"
            )

        text_str = str(text)
        text_lower = text_str.lower()
        tokens = text_lower.split()

        neg_hits = []
        pos_hits = []
        emoji_tags = []

        # 1. Emoji Sentiment
        for char, (e_weight, e_tag) in EMOJI_SENTIMENT_MAP.items():
            if char in text_str:
                if e_weight < 0:
                    neg_hits.append((char, e_weight, e_tag))
                else:
                    pos_hits.append((char, e_weight, e_tag))
                emoji_tags.append(e_tag)

        # 2. Text Phrases
        for phrase, weight, emotion in sorted(
            self._neg_lex + self._pos_lex,
            key=lambda x: -len(x[0])
        ):
            if phrase in text_lower:
                phrase_start = text_lower.find(phrase)
                preceding = text_lower[max(0, phrase_start-20):phrase_start].split()
                negated = any(neg in preceding[-3:] for neg in self._negators)
                effective_weight = -weight if negated else weight

                if effective_weight < 0:
                    neg_hits.append((phrase, effective_weight, emotion))
                else:
                    pos_hits.append((phrase, effective_weight, emotion))

        intensifier_count = sum(1 for t in tokens if t in self._intensifiers)
        intensifier_boost = 1.0 + intensifier_count * 0.15

        neg_total = sum(w for _, w, _ in neg_hits)
        pos_total = sum(w for _, w, _ in pos_hits)
        raw_polarity = (neg_total + pos_total) * intensifier_boost
        polarity = max(-1.0, min(1.0, raw_polarity))

        total_words = len(tokens) or 1
        subjectivity = min(1.0, (len(neg_hits) + len(pos_hits)) / total_words * 3)
        intensity = min(1.0, abs(polarity) * (0.5 + 0.5 * subjectivity))

        emotion_tags = list(dict.fromkeys(
            e for _, _, e in neg_hits + pos_hits
            if e not in ("positive", "negative")
        ))
        label = self._label(polarity, intensity)

        return SentimentResult(
            text=text_str,
            polarity=round(polarity, 4),
            subjectivity=round(subjectivity, 4),
            sentiment_label=label,
            intensity=round(intensity, 4),
            emotion_tags=emotion_tags[:5],
            negative_phrases=[p for p, _, _ in neg_hits[:6]],
            positive_phrases=[p for p, _, _ in pos_hits[:4]],
            intensifier_count=intensifier_count,
            analysis_strategy="emoji+lexicon",
            urgency_boost_applied="urgency" in emotion_tags or "fear" in emotion_tags
        )

    def _label(self, polarity: float, intensity: float) -> str:
        if polarity <= -0.55 or (polarity <= -0.35 and intensity >= 0.65):
            return "Critical"
        elif polarity <= -0.15:
            return "Negative"
        elif polarity >= 0.2:
            return "Positive"
        else:
            return "Neutral"


# ──────────────────────────────────────────────────────────────────────────────
# TextBlob Backend
# ──────────────────────────────────────────────────────────────────────────────

class TextBlobBackend:
    def __init__(self):
        self._available = False
        self._TextBlob = None
        self._try_load()

    def _try_load(self) -> None:
        try:
            import importlib
            tb_module = importlib.import_module("textblob")
            self._TextBlob = tb_module.TextBlob
            self._available = True
            logger.info("TextBlob available for sentiment analysis")
        except (ImportError, ModuleNotFoundError):
            pass

    @property
    def is_available(self) -> bool:
        return self._available

    def score(self, text: str) -> tuple:
        blob = self._TextBlob(text)
        return float(blob.sentiment.polarity), float(blob.sentiment.subjectivity)


# ──────────────────────────────────────────────────────────────────────────────
# Main Sentiment Engine Facade
# ──────────────────────────────────────────────────────────────────────────────

class SentimentEngine:
    def __init__(self):
        self._textblob = TextBlobBackend()
        self._lexicon  = LexiconSentimentScorer()
        self._strategy = "textblob+lexicon" if self._textblob.is_available else "lexicon"
        logger.info("SentimentEngine ready -- strategy: %s", self._strategy)

    def analyse(self, text: Optional[str]) -> SentimentResult:
        if not text or not str(text).strip():
            return self._lexicon.score("")

        safe_text = str(text)
        lexicon_res = self._lexicon.score(safe_text)

        if self._textblob.is_available:
            try:
                tb_polarity, tb_subjectivity = self._textblob.score(safe_text)
                blended_polarity = 0.6 * tb_polarity + 0.4 * lexicon_res.polarity
                blended_subjectivity = 0.6 * tb_subjectivity + 0.4 * lexicon_res.subjectivity
                intensity = min(1.0, abs(blended_polarity) * (0.5 + 0.5 * blended_subjectivity))
                label = self._label(blended_polarity, intensity)

                return SentimentResult(
                    text=safe_text,
                    polarity=round(blended_polarity, 4),
                    subjectivity=round(blended_subjectivity, 4),
                    sentiment_label=label,
                    intensity=round(intensity, 4),
                    emotion_tags=lexicon_res.emotion_tags,
                    negative_phrases=lexicon_res.negative_phrases,
                    positive_phrases=lexicon_res.positive_phrases,
                    intensifier_count=lexicon_res.intensifier_count,
                    analysis_strategy="textblob+lexicon",
                    urgency_boost_applied=lexicon_res.urgency_boost_applied
                )
            except Exception:
                pass

        return lexicon_res

    def sentiment_score_for_priority(self, result: SentimentResult) -> float:
        """Convert sentiment to 0-25 priority contribution score."""
        label_base = {
            "Critical": 25.0,
            "Negative": 15.0,
            "Neutral":   5.0,
            "Positive":  0.0,
        }
        base = label_base.get(result.sentiment_label, 5.0)
        bonus = result.intensity * 5.0
        return round(min(25.0, base + bonus), 2)

    def _label(self, polarity: float, intensity: float) -> str:
        if polarity <= -0.55 or (polarity <= -0.35 and intensity >= 0.65):
            return "Critical"
        elif polarity <= -0.15:
            return "Negative"
        elif polarity >= 0.2:
            return "Positive"
        else:
            return "Neutral"

    def to_dict(self, result: SentimentResult) -> dict:
        return {
            "text": result.text,
            "polarity": result.polarity,
            "subjectivity": result.subjectivity,
            "sentiment_label": result.sentiment_label,
            "intensity": result.intensity,
            "emotion_tags": result.emotion_tags,
            "negative_phrases": result.negative_phrases,
            "positive_phrases": result.positive_phrases,
            "intensifier_count": result.intensifier_count,
            "analysis_strategy": result.analysis_strategy,
            "priority_contribution": self.sentiment_score_for_priority(result),
            "urgency_boost_applied": result.urgency_boost_applied
        }


# ──────────────────────────────────────────────────────────────────────────────
# Module Singleton
# ──────────────────────────────────────────────────────────────────────────────
_sentiment_instance: Optional[SentimentEngine] = None

def get_sentiment_engine() -> SentimentEngine:
    global _sentiment_instance
    if _sentiment_instance is None:
        _sentiment_instance = SentimentEngine()
    return _sentiment_instance
