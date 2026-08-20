from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = "password123"
    role: Optional[str] = None # Optional role override for quick demo switch

class UserSchema(BaseModel):
    id: str
    email: str
    name: str
    role: str
    ward: Optional[str] = None
    avatar: Optional[str] = None

class AuthResponse(BaseModel):
    user: UserSchema
    token: str
    message: str

class ComplaintCreate(BaseModel):
    name: str
    title: str
    description: str
    category: str
    location: str
    latitude: float
    longitude: float

class ComplaintStatusUpdate(BaseModel):
    status: str

class ComplaintResolvePayload(BaseModel):
    status: str = "Resolved"
    resolution_photo: Optional[str] = None
    resolution_note: Optional[str] = None
    resolved_by: Optional[str] = "Ward Municipal Officer"

class ComplaintResponse(BaseModel):
    id: int
    name: str
    title: str
    description: str
    category: str
    location: str
    latitude: float
    longitude: float
    severity: str
    sentiment: str
    similarity_score: float
    priority_score: int
    priority_level: str
    recommendation: str
    status: str
    created_at: datetime
    deadline_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_photo: Optional[str] = None
    resolution_note: Optional[str] = None
    resolved_by: Optional[str] = None
    escalation_level: str = "Level 1: Local Authority"
    escalated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_complaints: int
    high_priority_count: int
    duplicate_count: int
    resolved_count: int
    pending_count: int
    in_progress_count: int
    active_sla_timers: int
    overdue_count: int
    escalated_count: int
    resolution_rate: float
    avg_resolution_hours: float

class CategoryCount(BaseModel):
    category: str
    count: int

class PriorityCount(BaseModel):
    priority_level: str
    count: int

class TrendData(BaseModel):
    date: str
    count: int
    high_priority: int

class AnalyticsResponse(BaseModel):
    stats: DashboardStats
    category_distribution: List[CategoryCount]
    priority_distribution: List[PriorityCount]
    complaint_trends: List[TrendData]
    smart_insights: List[str]
    needs_immediate_attention: List[ComplaintResponse]
