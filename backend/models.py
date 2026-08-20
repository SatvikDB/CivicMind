from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and len(v) == 24:
            return v
        raise ValueError("Invalid ObjectId")


class ComplaintDocument(BaseModel):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    title: str
    description: str
    category: str = "Unknown"
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "Pending"
    priority_score: float = 0.0
    priority_level: str = "Low"
    sentiment: str = "Neutral"
    recommended_action: str = ""
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    similarity_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


def complaint_doc_to_dict(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if "duplicate_of" in doc and doc["duplicate_of"] is not None:
        doc["duplicate_of"] = str(doc["duplicate_of"])
    return doc
