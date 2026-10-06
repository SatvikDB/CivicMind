from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ComplaintCreate(BaseModel):
    name: str
    title: str
    description: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StatusUpdate(BaseModel):
    status: str


class ComplaintResponse(BaseModel):
    id: str
    name: str
    title: str
    description: str
    category: str
    location_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    priority_score: float
    priority_level: str
    sentiment: str
    recommended_action: str
    is_duplicate: bool
    duplicate_of: Optional[str]
    similarity_score: float
    created_at: datetime
    updated_at: datetime


class DashboardStats(BaseModel):
    total_complaints: int
    high_priority: int
    potential_duplicates: int
    resolved: int


class CategoryCount(BaseModel):
    category: str
    count: int


class PriorityCount(BaseModel):
    level: str
    count: int


class TrendPoint(BaseModel):
    date: str
    count: int


class AnalyticsResponse(BaseModel):
    category_distribution: list[CategoryCount]
    priority_distribution: list[PriorityCount]
    trend_data: list[TrendPoint]
