"""
CivicMind AI -- Unified Analysis Pipeline
One entry point for Person 4's FastAPI backend

This module is the SINGLE INTEGRATION POINT for Person 4's backend.
Person 4 only needs to call:

    from civicmind_pipeline import CivicMindPipeline
    pipeline = CivicMindPipeline()

    # When a new complaint is submitted (POST /complaints)
    result = pipeline.analyse_complaint(
        text="There is a dangerous pothole near college gate since 2 months",
        existing_complaints=existing_db_texts  # list[str] from DB
    )

    # result is a plain dict -- JSON serialisable, ready for API response
    print(result["category"])         # "Road"
    print(result["priority_score"])   # 72.4
    print(result["priority_level"])   # "HIGH"
    print(result["recommendation"])   # {...}

Modules orchestrated:
    Person 5:  ai_engine.py             -- Category Detection & NLP Analysis
    Person 5:  similarity.py            -- Duplicate Detection
    Person 6:  sentiment_engine.py      -- Sentiment Analysis
    Person 6:  priority_engine.py       -- Priority Score Calculation
    Person 6:  recommendation_engine.py -- Actionable Recommendations
"""

import logging
from typing import Optional
from datetime import datetime, timezone

from ai_engine             import AIEngine,              get_engine
from similarity            import SimilarityEngine,      get_similarity_engine
from sentiment_engine      import SentimentEngine,       get_sentiment_engine
from priority_engine       import PriorityEngine,        get_priority_engine
from recommendation_engine import RecommendationEngine,  get_recommendation_engine

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _empty_result(text: str, error: str) -> dict:
    return {
        "status": "error",
        "error": error,
        "original_text": text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# CivicMind Pipeline
# ──────────────────────────────────────────────────────────────────────────────

class CivicMindPipeline:
    """
    Unified pipeline orchestrating all Person 5 & Person 6 modules.
    Fault-tolerant: handles empty inputs, missing DB corpus, emojis, and typos gracefully.
    """

    def __init__(self):
        self._ai        = get_engine()
        self._sim       = get_similarity_engine()
        self._sentiment = get_sentiment_engine()
        self._priority  = get_priority_engine()
        self._rec       = get_recommendation_engine()
        logger.info("CivicMind Pipeline ready -- all engines loaded")

    # ── Main API ──────────────────────────────────────────────────────────────

    def analyse_complaint(
        self,
        text: Optional[str],
        existing_complaints: Optional[list] = None
    ) -> dict:
        """
        Run the full AI analysis pipeline on a submitted complaint.

        Args:
            text:                Raw complaint text from the user.
            existing_complaints: List of previously stored complaint texts (from DB).
        """
        safe_text = str(text).strip() if text is not None else ""
        if not safe_text:
            return _empty_result(safe_text, "Complaint text cannot be empty.")

        try:
            # Step 1: NLP Analysis (Person 5)
            nlp = self._ai.analyse(safe_text)
            category       = nlp.category.category
            sub_category   = nlp.category.sub_category
            confidence     = nlp.category.confidence
            keywords       = nlp.keywords
            locations      = nlp.location_mentions
            urgency_list   = nlp.urgency_indicators
            complaint_type = nlp.complaint_type
            explanation    = nlp.category.explanation

            # Step 2: Duplicate Detection (Person 5)
            sim_data  = {}
            has_dup   = False
            dup_count = 0
            if existing_complaints:
                batch = self._sim.check_against_corpus(
                    safe_text, existing_complaints, top_k=5
                )
                has_dup   = batch.has_duplicate
                dup_count = batch.duplicate_count
                sim_data  = self._sim.batch_to_dict(batch)
            else:
                sim_data = {
                    "new_complaint": safe_text,
                    "top_matches": [],
                    "has_duplicate": False,
                    "duplicate_count": 0,
                    "related_count": 0,
                }

            # Step 3: Sentiment Analysis (Person 6)
            sentiment_result = self._sentiment.analyse(safe_text)
            sentiment_score  = self._sentiment.sentiment_score_for_priority(sentiment_result)
            sentiment_data   = self._sentiment.to_dict(sentiment_result)

            # Step 4: Priority Scoring (Person 6)
            priority_result = self._priority.compute(
                text=safe_text,
                category=category,
                sentiment_priority_score=sentiment_score,
                duplicate_count=dup_count,
                urgency_indicator_count=len(urgency_list)
            )
            priority_data = self._priority.to_dict(priority_result)

            # Step 5: Recommendation (Person 6)
            rec = self._rec.recommend(
                category=category,
                severity=priority_result.severity_level,
                priority_level=priority_result.priority_level
            )
            rec_data = self._rec.to_dict(rec)

            # Assemble Result
            result = {
                "status": "success",
                "original_text": safe_text,

                # Category & NLP (Person 5)
                "category": category,
                "sub_category": sub_category,
                "category_confidence": confidence,
                "category_explanation": explanation,
                "keywords": keywords,
                "location_mentions": locations,
                "urgency_indicators": urgency_list,
                "complaint_type": complaint_type,
                "detected_entities": nlp.detected_entities,

                # Duplicate Detection (Person 5)
                "similarity": sim_data,
                "is_duplicate": has_dup,

                # Sentiment (Person 6)
                "sentiment": sentiment_data,

                # Priority & Severity (Person 6)
                "priority_score":     priority_result.priority_score,
                "priority_level":     priority_result.priority_level,
                "severity_level":     priority_result.severity_level,
                "priority_reasoning": priority_result.priority_reasoning,
                "score_breakdown":    priority_result.score_breakdown,

                # Recommendation & Dispatch (Person 6)
                "recommendation": rec_data,

                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                "Pipeline complete | Category: %s (%.0f%%) | Priority: %.1f/100 [%s] | Duplicate: %s",
                category, confidence * 100,
                priority_result.priority_score, priority_result.priority_level,
                has_dup
            )
            return result

        except Exception as e:
            logger.error("Pipeline error: %s", e, exc_info=True)
            return _empty_result(safe_text, str(e))

    # ── Convenience Shortcuts ─────────────────────────────────────────────────

    def quick_category(self, text: Optional[str]) -> dict:
        """Fast category detection only (skip other engines)."""
        cat = self._ai.detect_category(text)
        return {
            "category":          cat.category,
            "sub_category":      cat.sub_category,
            "confidence":        cat.confidence,
            "matched_keywords":  cat.matched_keywords,
            "explanation":       cat.explanation,
        }

    def quick_similarity(self, text_a: Optional[str], text_b: Optional[str]) -> dict:
        """Compare two complaint texts for similarity."""
        result = self._sim.compare(text_a, text_b)
        return self._sim.result_to_dict(result)

    def health_check(self) -> dict:
        """Return engine availability status (for GET /health)."""
        return {
            "status": "healthy",
            "engines": {
                "ai_engine":             "ready (fuzzy + NLP + Hinglish)",
                "similarity_engine":     f"ready ({self._sim._strategy})",
                "sentiment_engine":      f"ready ({self._sentiment._strategy})",
                "priority_engine":       "ready (multi-factor + vulnerability booster)",
                "recommendation_engine": "ready (SLA + officer assignment + dispatch)",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Module Singleton
# ──────────────────────────────────────────────────────────────────────────────
_pipeline_instance: Optional[CivicMindPipeline] = None

def get_pipeline() -> CivicMindPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = CivicMindPipeline()
    return _pipeline_instance


if __name__ == "__main__":
    import json

    pipeline = CivicMindPipeline()
    existing_db = [
        "Pothole near the college gate is causing vehicle damage",
        "No water supply in Block 5 for the past 3 days",
        "Street lights not working near the bus stand",
        "Garbage dumped near the children's park",
    ]

    test_complaints = [
        "There is a big pothol near college gate. Bikes are skidding! Urgent! [SOS]",
        "Pani ki pipeline phat gayi hai near City Hospital, bahut pareshan hain log",
        "Open electricity wire hanging near school! Children could die! SOS",
        "Street light not working in Sector 4",
    ]

    print("\n" + "="*70)
    print("  CivicMind AI -- Enhanced Fault-Tolerant Pipeline Demo")
    print("="*70)

    for complaint in test_complaints:
        print("\n" + "-"*70)
        print("COMPLAINT: " + complaint)
        print("-"*70)

        result = pipeline.analyse_complaint(complaint, existing_db)

        if result["status"] == "success":
            print(f"  Category    : {result['category']} ({result['category_confidence']:.0%}) -> {result['sub_category']}")
            print(f"  Explanation : {result['category_explanation']}")
            print(f"  Locations   : {result['location_mentions']}")
            print(f"  Sentiment   : {result['sentiment']['sentiment_label']} (polarity={result['sentiment']['polarity']:.2f})")
            print(f"  Duplicate?  : {'Yes (' + str(result['similarity']['duplicate_count']) + ' found)' if result['is_duplicate'] else 'No'}")
            print(f"  Priority    : {result['priority_score']}/100 [{result['priority_level']}]")
            print(f"  Reasoning   : {result['priority_reasoning']}")
            print(f"  Action      : {result['recommendation']['action_title']}")
            print(f"  Officer     : {result['recommendation']['target_officer']}")
            print(f"  Dispatch SOS: {result['recommendation']['dispatch_immediate_field_team']}")
            print(f"  SLA         : {result['recommendation']['sla_label']}")
        else:
            print(f"  ERROR: {result['error']}")

    print("\n" + "-"*70)
    print("  Health Check:")
    print(json.dumps(pipeline.health_check(), indent=2))
