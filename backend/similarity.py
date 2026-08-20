# Person 5 -- Duplicate Detection
# Sentence Transformers embeddings + Cosine Similarity & TF-IDF hybrid with full fault tolerance.

import re
import math
import logging
from typing import Optional
from dataclasses import dataclass, field
from collections import Counter

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_DUPLICATE_THRESHOLD = 0.75   # similarity >= 75% = potential duplicate
DEFAULT_RELATED_THRESHOLD   = 0.50   # similarity >= 50% = related complaint
MODEL_NAME = "paraphrase-MiniLM-L6-v2"


# ──────────────────────────────────────────────────────────────────────────────
# Data Structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SimilarityResult:
    """Result of comparing two complaint texts."""
    text_a: str
    text_b: str
    similarity_score: float
    similarity_percent: int
    is_duplicate: bool
    is_related: bool
    verdict: str
    verdict_detail: str
    embedding_strategy: str

@dataclass
class BatchDuplicateResult:
    """Result of checking a new complaint against a corpus of existing ones."""
    new_complaint: str
    top_matches: list
    has_duplicate: bool
    duplicate_count: int
    related_count: int
    cluster_id: Optional[int] = None


# ──────────────────────────────────────────────────────────────────────────────
# TF-IDF Vectoriser (Fault-Tolerant, zero external deps)
# ──────────────────────────────────────────────────────────────────────────────

class TFIDFVectoriser:
    STOP_WORDS = {
        "i","me","my","we","our","you","your","he","she","it","they","them",
        "this","that","these","those","am","is","are","was","were","be","been",
        "have","has","had","do","does","did","will","would","could","should",
        "a","an","the","and","but","or","for","at","by","from","in","into",
        "on","to","of","with","as","not","also","about","very","just","so"
    }

    def __init__(self):
        self._vocab = []
        self._idf = {}
        self._is_fitted = False
        self._corpus = []

    def _tokenise(self, text: Optional[str]) -> list:
        if not text or not isinstance(text, str):
            return []
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return [w for w in text.split() if w not in self.STOP_WORDS and len(w) > 2]

    def _tf(self, tokens: list) -> dict:
        if not tokens:
            return {}
        count = Counter(tokens)
        total = sum(count.values()) or 1
        return {w: c / total for w, c in count.items()}

    def _compute_idf(self, docs: list) -> None:
        N = len(docs) + 1
        all_terms = set()
        for doc in docs:
            all_terms.update(doc)
        df = {term: sum(1 for doc in docs if term in doc) for term in all_terms}
        self._idf = {term: math.log(N / (df[term] + 1)) + 1 for term in all_terms}
        self._vocab = sorted(all_terms)

    def _vectorise(self, tokens: list) -> list:
        if not self._vocab:
            return []
        tf = self._tf(tokens)
        return [tf.get(t, 0.0) * self._idf.get(t, 0.0) for t in self._vocab]

    def fit(self, texts: list) -> "TFIDFVectoriser":
        valid_texts = [str(t) for t in texts if t]
        tokenised = [self._tokenise(t) for t in valid_texts]
        self._compute_idf(tokenised)
        self._corpus = valid_texts
        self._is_fitted = True
        return self

    def transform(self, text: Optional[str]) -> list:
        if not self._is_fitted:
            return []
        return self._vectorise(self._tokenise(text))

    def fit_transform(self, texts: list) -> list:
        self.fit(texts)
        return [self.transform(t) for t in texts]

    def is_fitted(self) -> bool:
        return self._is_fitted


# ──────────────────────────────────────────────────────────────────────────────
# Similarity Metrics
# ──────────────────────────────────────────────────────────────────────────────

def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Compute cosine similarity between two vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot   = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def jaccard_word_similarity(text_a: str, text_b: str) -> float:
    """Fallback Jaccard token overlap for zero-vector edge cases."""
    words_a = set(re.findall(r'\w+', text_a.lower()))
    words_b = set(re.findall(r'\w+', text_b.lower()))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    return len(intersection) / len(union)


# ──────────────────────────────────────────────────────────────────────────────
# Sentence Transformer Backend
# ──────────────────────────────────────────────────────────────────────────────

class SentenceTransformerBackend:
    def __init__(self, model_name: str = MODEL_NAME):
        self._model      = None
        self._model_name = model_name
        self._available  = False
        self._try_load()

    def _try_load(self) -> None:
        try:
            import importlib
            st_module = importlib.import_module("sentence_transformers")
            self._model     = st_module.SentenceTransformer(self._model_name)
            self._available = True
            logger.info("sentence-transformers loaded: %s", self._model_name)
        except (ImportError, ModuleNotFoundError):
            logger.info("sentence-transformers not installed -- using TF-IDF + token similarity.")
        except Exception as e:
            logger.warning("Could not load '%s': %s. Using TF-IDF.", self._model_name, e)

    @property
    def is_available(self) -> bool:
        return self._available

    def encode(self, texts: list) -> list:
        if not self._available or self._model is None:
            raise RuntimeError("SentenceTransformer model not available.")
        safe_texts = [str(t) if t is not None else "" for t in texts]
        embeddings = self._model.encode(safe_texts, convert_to_numpy=True)
        return embeddings.tolist()


# ──────────────────────────────────────────────────────────────────────────────
# Verdict Helper
# ──────────────────────────────────────────────────────────────────────────────

def _verdict(score: float, dup_thresh: float, rel_thresh: float):
    is_dup = score >= dup_thresh
    is_rel = (score >= rel_thresh) and not is_dup

    if is_dup:
        verdict = "Duplicate"
        detail  = (f"Similarity {score:.0%} -- these complaints describe the same "
                   f"civic issue at the same/nearby location. Merging recommended.")
    elif is_rel:
        verdict = "Related"
        detail  = (f"Similarity {score:.0%} -- these complaints are related to the "
                   f"same locality or category but may represent distinct tickets.")
    else:
        verdict = "Unique"
        detail  = (f"Similarity {score:.0%} -- complaints appear distinct and independent.")
    return is_dup, is_rel, verdict, detail


# ──────────────────────────────────────────────────────────────────────────────
# Main Similarity Engine Facade
# ──────────────────────────────────────────────────────────────────────────────

class SimilarityEngine:
    def __init__(self,
                 duplicate_threshold: float = DEFAULT_DUPLICATE_THRESHOLD,
                 related_threshold:   float = DEFAULT_RELATED_THRESHOLD):
        self._dup_thresh = duplicate_threshold
        self._rel_thresh = related_threshold
        self._st_backend = SentenceTransformerBackend()
        self._tfidf      = TFIDFVectoriser()
        self._strategy   = (
            "sentence-transformers" if self._st_backend.is_available else "tfidf"
        )
        logger.info("SimilarityEngine ready -- strategy: %s", self._strategy)

    def compare(self, text_a: Optional[str], text_b: Optional[str]) -> SimilarityResult:
        sa = str(text_a).strip() if text_a is not None else ""
        sb = str(text_b).strip() if text_b is not None else ""

        if not sa or not sb:
            return SimilarityResult(
                text_a=sa, text_b=sb, similarity_score=0.0,
                similarity_percent=0, is_duplicate=False, is_related=False,
                verdict="Unique", verdict_detail="One or both texts are empty.",
                embedding_strategy=self._strategy
            )

        score = self._compute_similarity(sa, sb)
        is_dup, is_rel, verdict, detail = _verdict(score, self._dup_thresh, self._rel_thresh)

        return SimilarityResult(
            text_a=sa,
            text_b=sb,
            similarity_score=round(score, 4),
            similarity_percent=round(score * 100),
            is_duplicate=is_dup,
            is_related=is_rel,
            verdict=verdict,
            verdict_detail=detail,
            embedding_strategy=self._strategy
        )

    def check_against_corpus(
        self,
        new_complaint: Optional[str],
        existing_complaints: Optional[list],
        top_k: int = 5
    ) -> BatchDuplicateResult:
        nc = str(new_complaint).strip() if new_complaint is not None else ""
        if not nc or not existing_complaints:
            return BatchDuplicateResult(
                new_complaint=nc,
                top_matches=[],
                has_duplicate=False,
                duplicate_count=0,
                related_count=0
            )

        valid_existing = [str(e) for e in existing_complaints if e and str(e).strip()]
        if not valid_existing:
            return BatchDuplicateResult(
                new_complaint=nc,
                top_matches=[],
                has_duplicate=False,
                duplicate_count=0,
                related_count=0
            )

        matches = []
        for idx, existing in enumerate(valid_existing):
            score = self._compute_similarity(nc, existing)
            is_dup, is_rel, verdict, detail = _verdict(score, self._dup_thresh, self._rel_thresh)
            matches.append({
                "index": idx,
                "text": existing,
                "similarity_score":   round(score, 4),
                "similarity_percent": round(score * 100),
                "is_duplicate": is_dup,
                "is_related":   is_rel,
                "verdict":      verdict,
                "verdict_detail": detail,
            })

        matches.sort(key=lambda x: -x["similarity_score"])
        top_matches = matches[:top_k]
        dup_count   = sum(1 for m in matches if m["is_duplicate"])
        rel_count   = sum(1 for m in matches if m["is_related"])

        return BatchDuplicateResult(
            new_complaint=nc,
            top_matches=top_matches,
            has_duplicate=dup_count > 0,
            duplicate_count=dup_count,
            related_count=rel_count
        )

    def batch_similarity_matrix(self, complaints: Optional[list]) -> list:
        if not complaints or len(complaints) == 0:
            return []
        valid = [str(c) for c in complaints]
        n = len(valid)
        matrix = [[0.0] * n for _ in range(n)]

        if self._st_backend.is_available:
            try:
                embeddings = self._st_backend.encode(valid)
                for i in range(n):
                    for j in range(n):
                        matrix[i][j] = cosine_similarity(embeddings[i], embeddings[j])
                return matrix
            except Exception as e:
                logger.warning("Embedding matrix error: %s. Falling back to TF-IDF.", e)

        vectors = self._tfidf.fit_transform(valid)
        for i in range(n):
            for j in range(n):
                c_sim = cosine_similarity(vectors[i], vectors[j])
                if c_sim == 0.0 and i != j:
                    c_sim = jaccard_word_similarity(valid[i], valid[j])
                elif i == j:
                    c_sim = 1.0
                matrix[i][j] = round(c_sim, 4)
        return matrix

    def find_duplicate_clusters(self, complaints: Optional[list], threshold: Optional[float] = None) -> list:
        if not complaints or len(complaints) < 2:
            return []
        thresh = threshold or self._dup_thresh
        matrix = self.batch_similarity_matrix(complaints)
        n = len(complaints)
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            parent[find(x)] = find(y)

        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] >= thresh:
                    union(i, j)

        clusters = {}
        for i in range(n):
            root = find(i)
            clusters.setdefault(root, []).append(i)

        return [c for c in clusters.values() if len(c) > 1]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _compute_similarity(self, text_a: str, text_b: str) -> float:
        if self._st_backend.is_available:
            try:
                embeddings = self._st_backend.encode([text_a, text_b])
                return cosine_similarity(embeddings[0], embeddings[1])
            except Exception:
                pass

        tokens_a = self._tfidf._tokenise(text_a)
        tokens_b = self._tfidf._tokenise(text_b)
        if not tokens_a or not tokens_b:
            return 0.0

        set_a, set_b = set(tokens_a), set(tokens_b)
        overlap = len(set_a.intersection(set_b))
        dice_sim = (2.0 * overlap) / (len(set_a) + len(set_b)) if (len(set_a) + len(set_b)) > 0 else 0.0

        vectors = self._tfidf.fit_transform([text_a, text_b])
        cos_score = cosine_similarity(vectors[0], vectors[1])
        jaccard_score = jaccard_word_similarity(text_a, text_b)

        return round(max(dice_sim, cos_score, jaccard_score), 4)

    def result_to_dict(self, result: SimilarityResult) -> dict:
        return {
            "text_a":             result.text_a,
            "text_b":             result.text_b,
            "similarity_score":   result.similarity_score,
            "similarity_percent": result.similarity_percent,
            "is_duplicate":       result.is_duplicate,
            "is_related":         result.is_related,
            "verdict":            result.verdict,
            "verdict_detail":     result.verdict_detail,
            "embedding_strategy": result.embedding_strategy,
        }

    def batch_to_dict(self, result: BatchDuplicateResult) -> dict:
        return {
            "new_complaint":   result.new_complaint,
            "top_matches":     result.top_matches,
            "has_duplicate":   result.has_duplicate,
            "duplicate_count": result.duplicate_count,
            "related_count":   result.related_count,
            "cluster_id":      result.cluster_id,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Module Singleton
# ──────────────────────────────────────────────────────────────────────────────
_similarity_instance: Optional[SimilarityEngine] = None

def get_similarity_engine() -> SimilarityEngine:
    global _similarity_instance
    if _similarity_instance is None:
        _similarity_instance = SimilarityEngine()
    return _similarity_instance
