# Person 6 -- Priority Engine
# Severity detection, safety risk assessment & priority calculation (0-100) with vulnerability multipliers and explainability.

import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Data Structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SeverityResult:
    """Result of severity detection for a complaint."""
    level: str              # "Low" | "Medium" | "High" | "Critical"
    score: float            # 0.0 – 1.0
    matched_indicators: list
    safety_risk: float      # 0.0 – 1.0
    vulnerability_detected: list = field(default_factory=list)


@dataclass
class PriorityResult:
    """Final priority computation result."""
    complaint_text: str
    category: str
    severity_score: float
    sentiment_score: float
    safety_risk_score: float
    duplicate_frequency_score: float
    urgency_signal_score: float
    priority_score: float          # 0 – 100
    priority_level: str            # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    severity_level: str            # "Low" | "Medium" | "High" | "Critical"
    score_breakdown: dict          # component weights & contributions
    priority_reasoning: str = ""
    assigned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ──────────────────────────────────────────────────────────────────────────────
# Severity Lexicons
# ──────────────────────────────────────────────────────────────────────────────

SEVERITY_INDICATORS = [
    # CRITICAL — immediate life risk
    ("death",              1.0,  1.0),
    ("died",               1.0,  1.0),
    ("killed",             1.0,  1.0),
    ("life threatening",   1.0,  1.0),
    ("risk to life",       1.0,  1.0),
    ("collapse",           0.95, 1.0),
    ("collapsed",          0.95, 1.0),
    ("explosion",          1.0,  1.0),
    ("fire",               0.9,  0.95),
    ("electric shock",     0.95, 1.0),
    ("naked wire",         0.9,  1.0),
    ("exposed wire",       0.9,  1.0),
    ("dangling wire",      0.85, 0.95),
    ("open manhole",       0.9,  1.0),
    ("wall collapse",      0.9,  0.95),
    ("building collapse",  0.95, 1.0),
    ("injury",             0.8,  0.9),
    ("injured",            0.8,  0.9),
    ("accident",           0.85, 0.9),
    ("flood",              0.8,  0.85),
    ("gas leak",           0.95, 1.0),
    ("sewage contamination",0.8, 0.85),
    ("jaan ka khatra",     1.0,  1.0),
    # HIGH
    ("very bad",           0.7,  0.5),
    ("extremely",          0.65, 0.45),
    ("severe",             0.7,  0.55),
    ("serious",            0.65, 0.5),
    ("dangerous",          0.75, 0.7),
    ("hazard",             0.7,  0.65),
    ("unsafe",             0.65, 0.6),
    ("broken pipe",        0.6,  0.5),
    ("burst pipe",         0.7,  0.6),
    ("major pothole",      0.65, 0.55),
    ("deep pothole",       0.6,  0.5),
    ("months",             0.55, 0.3),
    ("years",              0.65, 0.3),
    ("khatarnak",          0.75, 0.7),
    # MEDIUM
    ("bad",                0.4,  0.2),
    ("broken",             0.45, 0.3),
    ("damaged",            0.45, 0.3),
    ("leak",               0.4,  0.25),
    ("no water",           0.45, 0.25),
    ("no power",           0.45, 0.25),
    ("pothole",            0.4,  0.3),
    ("garbage",            0.35, 0.15),
    ("dirty",              0.3,  0.15),
    ("blocked drain",      0.4,  0.2),
    ("overflow",           0.45, 0.3),
    ("stagnant water",     0.5,  0.35),
    ("mosquito",           0.5,  0.35),
    ("weeks",              0.4,  0.2),
    ("repeated",           0.45, 0.2),
    # LOW
    ("minor",              0.15, 0.05),
    ("small",              0.1,  0.05),
    ("little",             0.1,  0.05),
    ("slight",             0.1,  0.05),
    ("noise",              0.2,  0.05),
    ("litter",             0.15, 0.05),
    ("complaint",          0.1,  0.0),
    ("issue",              0.15, 0.05),
    ("problem",            0.2,  0.1),
]

# Vulnerability hotspots (boosts safety risk)
VULNERABILITY_KEYWORDS = [
    "school", "college", "children", "kids", "student", "hospital",
    "clinic", "elderly", "old age", "baby", "nursery", "patient", "playground"
]

CATEGORY_BASE_SEVERITY = {
    "Safety":        0.7,
    "Water":         0.5,
    "Road":          0.5,
    "Electricity":   0.6,
    "Health":        0.65,
    "Environment":   0.45,
    "Garbage":       0.35,
    "Noise":         0.25,
    "Infrastructure":0.4,
    "Transport":     0.3,
    "Animal":        0.35,
    "Civic Services":0.2,
    "Other":         0.3,
}


# ──────────────────────────────────────────────────────────────────────────────
# Severity Detector
# ──────────────────────────────────────────────────────────────────────────────

class SeverityDetector:
    def detect(self, text: Optional[str], category: str = "Other") -> SeverityResult:
        if not text or not str(text).strip():
            return SeverityResult(
                level="Low", score=0.2, matched_indicators=[], safety_risk=0.1, vulnerability_detected=[]
            )

        text_lower = str(text).lower()
        matched = []
        vuln_found = []

        # Check vulnerability context
        for v in VULNERABILITY_KEYWORDS:
            if v in text_lower:
                vuln_found.append(v)

        for phrase, sev_w, safety_w in sorted(
            SEVERITY_INDICATORS, key=lambda x: -len(x[0])
        ):
            if phrase in text_lower:
                matched.append((phrase, sev_w, safety_w))

        if matched:
            total_sev = sum(w for _, w, _ in matched)
            total_saf = sum(w for _, _, w in matched)
            count = len(matched)
            avg_sev = total_sev / count
            avg_saf = total_saf / count

            max_sev = max(w for _, w, _ in matched)
            max_saf = max(w for _, _, w in matched)

            sev_score = 0.6 * max_sev + 0.4 * avg_sev
            saf_score = 0.6 * max_saf + 0.4 * avg_saf
        else:
            sev_score = CATEGORY_BASE_SEVERITY.get(category, 0.3)
            saf_score = sev_score * 0.5

        # Vulnerability boost (e.g. school/hospital presence increases risk)
        if vuln_found:
            saf_score = min(1.0, saf_score + 0.15)
            sev_score = min(1.0, sev_score + 0.08)

        level = self._level(sev_score)

        return SeverityResult(
            level=level,
            score=round(sev_score, 4),
            matched_indicators=[p for p, _, _ in matched[:6]],
            safety_risk=round(saf_score, 4),
            vulnerability_detected=vuln_found[:4]
        )

    def _level(self, score: float) -> str:
        if score >= 0.78:
            return "Critical"
        elif score >= 0.52:
            return "High"
        elif score >= 0.28:
            return "Medium"
        else:
            return "Low"


# ──────────────────────────────────────────────────────────────────────────────
# Priority Score Calculator
# ──────────────────────────────────────────────────────────────────────────────

PRIORITY_WEIGHTS = {
    "severity":             0.35,
    "sentiment":            0.25,
    "safety_risk":          0.20,
    "duplicate_frequency":  0.10,
    "urgency_signals":      0.10,
}


class PriorityCalculator:
    WEIGHTS = PRIORITY_WEIGHTS

    def calculate(
        self,
        complaint_text: str,
        category: str,
        severity_result: SeverityResult,
        sentiment_priority_score: float,   # 0–25
        duplicate_count: int = 0,
        urgency_indicator_count: int = 0
    ) -> PriorityResult:
        # Clamp inputs
        dup_cnt = max(0, duplicate_count)
        urg_cnt = max(0, urgency_indicator_count)
        sent_contrib = max(0.0, min(25.0, sentiment_priority_score))

        sev_score  = severity_result.score * 100
        sent_score = min(100.0, sent_contrib * 4.0)
        saf_score  = severity_result.safety_risk * 100
        dup_score  = min(100.0, dup_cnt * 20.0)
        urg_score  = min(100.0, urg_cnt * 20.0)

        weighted = (
            self.WEIGHTS["severity"]            * sev_score  +
            self.WEIGHTS["sentiment"]           * sent_score +
            self.WEIGHTS["safety_risk"]         * saf_score  +
            self.WEIGHTS["duplicate_frequency"] * dup_score  +
            self.WEIGHTS["urgency_signals"]     * urg_score
        )

        priority_score = round(min(100.0, max(0.0, weighted)), 1)
        priority_level = self._level(priority_score)

        breakdown = {
            "severity": {
                "raw_score": round(sev_score, 1),
                "weight": self.WEIGHTS["severity"],
                "contribution": round(self.WEIGHTS["severity"] * sev_score, 1)
            },
            "sentiment": {
                "raw_score": round(sent_score, 1),
                "weight": self.WEIGHTS["sentiment"],
                "contribution": round(self.WEIGHTS["sentiment"] * sent_score, 1)
            },
            "safety_risk": {
                "raw_score": round(saf_score, 1),
                "weight": self.WEIGHTS["safety_risk"],
                "contribution": round(self.WEIGHTS["safety_risk"] * saf_score, 1)
            },
            "duplicate_frequency": {
                "raw_score": round(dup_score, 1),
                "weight": self.WEIGHTS["duplicate_frequency"],
                "contribution": round(self.WEIGHTS["duplicate_frequency"] * dup_score, 1)
            },
            "urgency_signals": {
                "raw_score": round(urg_score, 1),
                "weight": self.WEIGHTS["urgency_signals"],
                "contribution": round(self.WEIGHTS["urgency_signals"] * urg_score, 1)
            },
        }

        # Human-readable reasoning for dashboards
        reasons = []
        if severity_result.level in ("Critical", "High"):
            reasons.append(f"High severity issue ({severity_result.level})")
        if severity_result.vulnerability_detected:
            reasons.append(f"Affects sensitive area ({', '.join(severity_result.vulnerability_detected)})")
        if dup_cnt > 0:
            reasons.append(f"Reported {dup_cnt} times by multiple citizens")
        if urg_cnt > 0:
            reasons.append(f"{urg_cnt} urgency signals detected")
        if not reasons:
            reasons.append(f"Standard priority maintenance ticket")
        
        reasoning = "; ".join(reasons)

        return PriorityResult(
            complaint_text=complaint_text,
            category=category,
            severity_score=round(sev_score, 1),
            sentiment_score=round(sent_score, 1),
            safety_risk_score=round(saf_score, 1),
            duplicate_frequency_score=round(dup_score, 1),
            urgency_signal_score=round(urg_score, 1),
            priority_score=priority_score,
            priority_level=priority_level,
            severity_level=severity_result.level,
            score_breakdown=breakdown,
            priority_reasoning=reasoning
        )

    def _level(self, score: float) -> str:
        if score >= 75:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        else:
            return "LOW"


# ──────────────────────────────────────────────────────────────────────────────
# Main Priority Engine Facade
# ──────────────────────────────────────────────────────────────────────────────

class PriorityEngine:
    def __init__(self):
        self._severity_detector = SeverityDetector()
        self._calculator        = PriorityCalculator()
        logger.info("PriorityEngine initialised")

    def compute(
        self,
        text: Optional[str],
        category: str = "Other",
        sentiment_priority_score: float = 5.0,
        duplicate_count: int = 0,
        urgency_indicator_count: int = 0
    ) -> PriorityResult:
        safe_text = str(text).strip() if text is not None else ""
        severity = self._severity_detector.detect(safe_text, category)
        result = self._calculator.calculate(
            complaint_text=safe_text,
            category=category,
            severity_result=severity,
            sentiment_priority_score=sentiment_priority_score,
            duplicate_count=duplicate_count,
            urgency_indicator_count=urgency_indicator_count
        )
        return result

    def detect_severity(self, text: Optional[str], category: str = "Other") -> SeverityResult:
        return self._severity_detector.detect(text, category)

    def to_dict(self, result: PriorityResult) -> dict:
        return {
            "complaint_text": result.complaint_text,
            "category": result.category,
            "priority_score": result.priority_score,
            "priority_level": result.priority_level,
            "severity_level": result.severity_level,
            "severity_score": result.severity_score,
            "sentiment_score": result.sentiment_score,
            "safety_risk_score": result.safety_risk_score,
            "duplicate_frequency_score": result.duplicate_frequency_score,
            "urgency_signal_score": result.urgency_signal_score,
            "score_breakdown": result.score_breakdown,
            "priority_reasoning": result.priority_reasoning,
            "assigned_at": result.assigned_at,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Module Singleton
# ──────────────────────────────────────────────────────────────────────────────
_priority_instance: Optional[PriorityEngine] = None

def get_priority_engine() -> PriorityEngine:
    global _priority_instance
    if _priority_instance is None:
        _priority_instance = PriorityEngine()
    return _priority_instance
