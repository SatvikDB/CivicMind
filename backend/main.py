from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import connect_db, close_db
from schemas import (
    ComplaintCreate, ComplaintResponse, StatusUpdate,
    DashboardStats, AnalyticsResponse,
)
from crud import (
    create_complaint, get_complaint, get_all_complaints,
    update_complaint_status, update_complaint_ai_fields,
    get_complaints_for_similarity, search_complaints,
    get_map_complaints, get_dashboard_stats, get_analytics,
)
from models import complaint_doc_to_dict
from ai_engine import analyze_complaint


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="CivicMind AI",
    description="AI-powered civic complaint management system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CivicMind AI"}


@app.get("/")
async def root():
    return {"message": "CivicMind AI Backend", "docs": "/docs"}


@app.post("/api/complaints", response_model=ComplaintResponse)
async def submit_complaint(complaint: ComplaintCreate):
    doc = await create_complaint(complaint.model_dump())
    existing = await get_complaints_for_similarity()
    ai_result = analyze_complaint(complaint.description, existing)
    doc = await update_complaint_ai_fields(str(doc["_id"]), ai_result)
    return complaint_doc_to_dict(doc)


@app.get("/api/complaints", response_model=list[ComplaintResponse])
async def list_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    docs = await get_all_complaints(skip=skip, limit=limit)
    return [complaint_doc_to_dict(d) for d in docs]


@app.get("/api/complaints/{complaint_id}", response_model=ComplaintResponse)
async def get_single_complaint(complaint_id: str):
    doc = await get_complaint(complaint_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint_doc_to_dict(doc)


@app.put("/api/complaints/{complaint_id}/status", response_model=ComplaintResponse)
async def update_status(complaint_id: str, update: StatusUpdate):
    doc = await update_complaint_status(complaint_id, update.status)
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint_doc_to_dict(doc)


@app.get("/api/complaints/search", response_model=list[ComplaintResponse])
async def search(
    q: str = Query("", description="Search in title and description"),
    category: str = Query("", description="Filter by category"),
    status: str = Query("", description="Filter by status"),
):
    docs = await search_complaints(query=q, category=category, status=status)
    return [complaint_doc_to_dict(d) for d in docs]


@app.get("/api/map/complaints")
async def map_complaints():
    return await get_map_complaints()


@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def stats():
    return await get_dashboard_stats()


@app.get("/api/dashboard/analytics", response_model=AnalyticsResponse)
async def analytics():
    return await get_analytics()


class AnalyzeRequest(BaseModel):
    text: str


@app.post("/api/ai/analyze")
async def analyze(request: AnalyzeRequest):
    return analyze_complaint(request.text, existing_complaints=[])
