"""
MongoDB document helpers for CivicMind AI.

MongoDB stores complaints as plain dicts. This module provides:
  - field defaults
  - a helper to serialise a raw Mongo document into the shape
    that the Pydantic response schemas expect (converts ObjectId → int id, etc.)
"""

from datetime import datetime, timedelta
from bson import ObjectId


def complaint_defaults() -> dict:
    """Return default field values for a new complaint document."""
    now = datetime.utcnow()
    return {
        "severity": "Medium",
        "sentiment": "Neutral",
        "similarity_score": 0.0,
        "priority_score": 50,
        "priority_level": "Medium",
        "recommendation": "",
        "status": "Pending",
        "created_at": now,
        "deadline_at": now + timedelta(hours=48),
        "resolved_at": None,
        "resolution_photo": None,
        "resolution_note": None,
        "resolved_by": None,
        "escalation_level": "Level 1: Local Authority",
        "escalated_at": None,
    }


def doc_to_dict(doc: dict) -> dict:
    """
    Convert a raw MongoDB document to a plain dict compatible with
    ComplaintResponse schema.  MongoDB uses '_id' (ObjectId); we expose
    an integer 'id' by using a separate auto-increment counter stored in
    the document itself.
    """
    if doc is None:
        return None
    d = dict(doc)
    # Map the stored integer 'id' field (or fall back to ObjectId hash)
    if "_id" in d:
        if "id" not in d:
            d["id"] = abs(hash(str(d["_id"]))) % (10 ** 6)
        del d["_id"]
    return d
