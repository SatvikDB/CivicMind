from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def find_duplicates(
    new_text: str,
    existing_complaints: list[dict],
    threshold: float = 0.70,
) -> tuple[bool, str | None, float]:
    if not existing_complaints:
        return False, None, 0.0

    new_embedding = model.encode([new_text])
    existing_texts = [c["description"] for c in existing_complaints]
    existing_embeddings = model.encode(existing_texts)

    similarities = cosine_similarity(new_embedding, existing_embeddings)[0]

    max_idx = int(np.argmax(similarities))
    max_score = float(similarities[max_idx])

    if max_score >= threshold:
        return True, existing_complaints[max_idx]["id"], max_score

    return False, None, max_score
