"""
Comprehensive Fault-Tolerance & Unit Test Suite for Person 5 & 6 Modules.
Tests:
  - Empty string, whitespace, None inputs
  - Typos & spelling mistakes (e.g. 'pothol', 'drane')
  - Regional & Hinglish complaints ('sadak par gaddha', 'pani nahi aa raha')
  - Emoji sentiment extraction (🚨, 😡, 💀, 👍)
  - Duplicate detection with empty DB corpus vs populated corpus
  - High-vulnerability priority boosting (schools, hospitals)
  - Recommendation SLA and officer assignment validation
"""

import unittest
from ai_engine import get_engine, AIEngine
from similarity import get_similarity_engine, SimilarityEngine
from sentiment_engine import get_sentiment_engine, SentimentEngine
from priority_engine import get_priority_engine, PriorityEngine
from recommendation_engine import get_recommendation_engine, RecommendationEngine
from civicmind_pipeline import get_pipeline, CivicMindPipeline


class TestCivicMindAIEngines(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ai = get_engine()
        cls.sim = get_similarity_engine()
        cls.sentiment = get_sentiment_engine()
        cls.priority = get_priority_engine()
        cls.rec = get_recommendation_engine()
        cls.pipeline = get_pipeline()

    # ── Test 1: Fault Tolerance with Empty / None Inputs ───────────────────────
    def test_empty_and_none_inputs(self):
        # Empty string
        res_empty = self.pipeline.analyse_complaint("")
        self.assertEqual(res_empty["status"], "error")

        # None input
        res_none = self.pipeline.analyse_complaint(None)
        self.assertEqual(res_none["status"], "error")

        # Whitespace only
        res_spaces = self.pipeline.analyse_complaint("    ")
        self.assertEqual(res_spaces["status"], "error")

        # Sub-engines handling empty/None safely
        cat_none = self.ai.detect_category(None)
        self.assertEqual(cat_none.category, "Other")

        sim_none = self.sim.compare(None, "")
        self.assertEqual(sim_none.similarity_score, 0.0)

        sent_none = self.sentiment.analyse("")
        self.assertEqual(sent_none.sentiment_label, "Neutral")

    # ── Test 2: Category Detection with Typos & Spelling Mistakes ─────────────
    def test_fuzzy_and_typo_matching(self):
        # 'pothol' typo should still resolve to Road
        res = self.ai.analyse("There is a large pothol on MG road")
        self.assertEqual(res.category.category, "Road")

        # 'drinage' typo should resolve to Water
        res_water = self.ai.analyse("Dirty drinage is overflowing near market")
        self.assertEqual(res_water.category.category, "Water")

    # ── Test 3: Hinglish & Multilingual Civic Support ─────────────────────────
    def test_hinglish_civic_detection(self):
        res_road = self.ai.analyse("sadak par bahut bada gaddha hai Sector 12 mein")
        self.assertEqual(res_road.category.category, "Road")

        res_water = self.ai.analyse("pani ki pipeline phat gayi hai")
        self.assertEqual(res_water.category.category, "Water")

        res_elec = self.ai.analyse("bijli chali gayi hai aur khamba toot gaya hai")
        self.assertEqual(res_elec.category.category, "Electricity")

        res_garb = self.ai.analyse("kachra bohot faila hua hai kudedan ke paas")
        self.assertEqual(res_garb.category.category, "Garbage")

    # ── Test 4: Emoji Sentiment & Urgency Boost ──────────────────────────────
    def test_emoji_and_critical_sentiment(self):
        res_crit = self.sentiment.analyse("Dangerous open manhole! Children are playing nearby 🚨💀😡")
        self.assertEqual(res_crit.sentiment_label, "Critical")
        self.assertIn("fear", res_crit.emotion_tags)

        res_pos = self.sentiment.analyse("Thank you so much for repairing the street light! Great work 👍🙏")
        self.assertEqual(res_pos.sentiment_label, "Positive")
        self.assertGreater(res_pos.polarity, 0.0)

    # ── Test 5: Duplicate Detection & Empty Corpus Resilience ─────────────────
    def test_duplicate_detection(self):
        corpus = [
            "Pothole near the college gate causing accidents",
            "Water shortage in Block 4 colony",
            "Garbage dumping near temple"
        ]

        # Duplicate case
        batch_dup = self.sim.check_against_corpus(
            "There is a deep pothole near college gate, bikes skidding", corpus
        )
        self.assertTrue(batch_dup.has_duplicate or batch_dup.related_count > 0)
        self.assertGreater(len(batch_dup.top_matches), 0)

        # Empty corpus check
        batch_empty = self.sim.check_against_corpus("Any complaint", [])
        self.assertFalse(batch_empty.has_duplicate)
        self.assertEqual(batch_empty.duplicate_count, 0)

    # ── Test 6: Priority Scoring & Sensitive Area Vulnerability Boost ──────────
    def test_priority_and_vulnerability_boost(self):
        # Road pothole in general area
        res_normal = self.priority.compute(
            text="Pothole on the lane",
            category="Road",
            sentiment_priority_score=10.0
        )

        # Road pothole near hospital/school (should have higher safety risk & priority)
        res_school = self.priority.compute(
            text="Deep dangerous pothole right outside school gate where children cross",
            category="Road",
            sentiment_priority_score=20.0
        )
        self.assertGreater(res_school.priority_score, res_normal.priority_score)
        self.assertGreaterEqual(res_school.safety_risk_score, res_normal.safety_risk_score)
        self.assertIn("school", res_school.priority_reasoning.lower())

    # ── Test 7: Recommendation Engine & Dispatch Trigger ─────────────────────
    def test_recommendation_and_dispatch(self):
        rec_crit = self.rec.recommend("Electricity", "Critical", "CRITICAL")
        self.assertEqual(rec_crit.department, "Electricity Distribution Company (DISCOM)")
        self.assertTrue(rec_crit.dispatch_immediate_field_team)
        self.assertLessEqual(rec_crit.sla_hours, 6)

        rec_med = self.rec.recommend("Road", "Medium", "MEDIUM")
        self.assertFalse(rec_med.dispatch_immediate_field_team)
        self.assertGreater(rec_med.sla_hours, 24)

    # ── Test 8: End-to-End Pipeline Full Contract Verification ────────────────
    def test_full_pipeline_contract(self):
        complaint = "Water pipe burst near City Hospital. Flooding on the main road! 🚨"
        result = self.pipeline.analyse_complaint(complaint, ["Water pipe leak on road"])

        # Check required fields for Person 4 backend
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["category"], "Water")
        self.assertIn("priority_score", result)
        self.assertIn("priority_level", result)
        self.assertIn("sentiment", result)
        self.assertIn("recommendation", result)
        self.assertIn("location_mentions", result)
        self.assertIn("category_explanation", result)
        self.assertIn("priority_reasoning", result)


if __name__ == "__main__":
    unittest.main()
