import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
from collections import Counter

import schemas
from ai_engine import process_complaint_ai
from auth import authenticate_user, DEMO_USERS
from database import get_complaints_collection, ping
from models import complaint_defaults, doc_to_dict

app = FastAPI(
    title="CivicMind AI Platform API",
    description="Backend API providing civic complaint intelligence, role-based auth, 48h SLA tracking, escalation engine, and resolution proof. Backed by MongoDB.",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _next_id() -> int:
    """Simple auto-increment using a counters collection."""
    from database import db
    result = db["counters"].find_one_and_update(
        {"_id": "complaint_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return result["seq"]


def _check_and_update_escalations():
    """Auto-escalate overdue complaints."""
    col = get_complaints_collection()
    now = datetime.utcnow()
    unresolved = list(col.find({"status": {"$ne": "Resolved"}}))

    for c in unresolved:
        deadline = c.get("deadline_at")
        if not deadline:
            continue
        if now <= deadline:
            continue

        hours_overdue = (now - deadline).total_seconds() / 3600.0
        new_level = (
            "Level 3: Senior Authority" if hours_overdue >= 24
            else "Level 2: Department Officer"
        )

        updates = {"escalation_level": new_level}
        if c.get("status") in ("Pending", "In Progress"):
            updates["status"] = "OVERDUE"
        if not c.get("escalated_at"):
            updates["escalated_at"] = deadline

        col.update_one({"_id": c["_id"]}, {"$set": updates})


def _serialize(doc) -> dict:
    return doc_to_dict(doc)


# ─────────────────────────────────────────────
# Startup / Health
# ─────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    try:
        ping()
        print("✅ Connected to MongoDB Atlas successfully.")
    except Exception as e:
        print(f"⚠️  MongoDB connection warning: {e}")


@app.get("/health")
def health_check():
    try:
        ping()
        mongo_status = "connected"
    except Exception:
        mongo_status = "unreachable"
    return {
        "status": "ok",
        "service": "CivicMind AI SLA & Auth Engine",
        "database": f"MongoDB Atlas ({mongo_status})",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# Auth Endpoints
# ─────────────────────────────────────────────

@app.post("/auth/login", response_model=schemas.AuthResponse)
def login_user(payload: schemas.LoginRequest):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or credentials")

    if payload.role and payload.role in ("citizen", "admin"):
        user.role = payload.role
        if payload.role == "admin":
            user.name = "Eng. Ramesh V (Ward Officer)"
            user.email = "admin@civicmind.ai"
        else:
            user.name = "Aarav Sharma"
            user.email = "citizen@civicmind.ai"

    return {
        "user": user,
        "token": f"jwt_token_{user.id}_demo",
        "message": f"Successfully authenticated as {user.role.upper()} ({user.name})",
    }


@app.get("/auth/demo-users")
def get_demo_users():
    return list(DEMO_USERS.values())


# ─────────────────────────────────────────────
# Complaints Endpoints
# ─────────────────────────────────────────────

@app.post("/complaints", response_model=schemas.ComplaintResponse, status_code=201)
def create_complaint(payload: schemas.ComplaintCreate):
    col = get_complaints_collection()
    existing_texts = [
        f"{c['title']}. {c['description']}"
        for c in col.find({}, {"title": 1, "description": 1})
    ]

    ai_res = process_complaint_ai(
        title=payload.title,
        description=payload.description,
        category_input=payload.category,
        location=payload.location,
        existing_complaints_texts=existing_texts,
    )

    now = datetime.utcnow()
    doc = {
        **complaint_defaults(),
        "id": _next_id(),
        "name": payload.name,
        "title": payload.title,
        "description": payload.description,
        "category": ai_res["category"],
        "location": payload.location,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "severity": ai_res["severity"],
        "sentiment": ai_res["sentiment"],
        "similarity_score": ai_res["similarity_score"],
        "priority_score": ai_res["priority_score"],
        "priority_level": ai_res["priority_level"],
        "recommendation": ai_res["recommendation"],
        "status": "Pending",
        "created_at": now,
        "deadline_at": now + timedelta(hours=48),
        "escalation_level": "Level 1: Local Authority",
    }

    col.insert_one(doc)
    return _serialize(doc)


@app.get("/complaints", response_model=List[schemas.ComplaintResponse])
def get_complaints(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    _check_and_update_escalations()
    col = get_complaints_collection()
    filt: dict = {}

    if q:
        filt["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"location": {"$regex": q, "$options": "i"}},
            {"name": {"$regex": q, "$options": "i"}},
        ]
    if category and category != "All":
        filt["category"] = category
    if priority and priority != "All":
        filt["priority_level"] = priority
    if status and status != "All":
        filt["status"] = status

    docs = list(col.find(filt).sort("created_at", -1))
    return [_serialize(d) for d in docs]


@app.get("/complaints/{complaint_id}", response_model=schemas.ComplaintResponse)
def get_complaint(complaint_id: int):
    _check_and_update_escalations()
    col = get_complaints_collection()
    doc = col.find_one({"id": complaint_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return _serialize(doc)


@app.put("/complaints/{complaint_id}/status", response_model=schemas.ComplaintResponse)
def update_complaint_status(complaint_id: int, status_update: schemas.ComplaintStatusUpdate):
    col = get_complaints_collection()
    doc = col.find_one({"id": complaint_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")

    updates: dict = {"status": status_update.status}
    if status_update.status == "Resolved" and not doc.get("resolved_at"):
        updates["resolved_at"] = datetime.utcnow()

    col.update_one({"id": complaint_id}, {"$set": updates})
    return _serialize(col.find_one({"id": complaint_id}))


@app.put("/complaints/{complaint_id}/resolve", response_model=schemas.ComplaintResponse)
def resolve_complaint_with_proof(complaint_id: int, payload: schemas.ComplaintResolvePayload):
    col = get_complaints_collection()
    doc = col.find_one({"id": complaint_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")

    updates: dict = {
        "status": payload.status or "Resolved",
        "resolved_at": datetime.utcnow(),
    }
    if payload.resolution_photo:
        updates["resolution_photo"] = payload.resolution_photo
    if payload.resolution_note:
        updates["resolution_note"] = payload.resolution_note
    if payload.resolved_by:
        updates["resolved_by"] = payload.resolved_by

    col.update_one({"id": complaint_id}, {"$set": updates})
    return _serialize(col.find_one({"id": complaint_id}))


# ─────────────────────────────────────────────
# Map Endpoint
# ─────────────────────────────────────────────

@app.get("/map/complaints", response_model=List[schemas.ComplaintResponse])
def get_map_complaints(
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    return get_complaints(q=None, category=category, priority=priority, status=status)


# ─────────────────────────────────────────────
# Dashboard Endpoints
# ─────────────────────────────────────────────

@app.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats():
    _check_and_update_escalations()
    col = get_complaints_collection()
    complaints = list(col.find())
    now = datetime.utcnow()

    total = len(complaints)
    high_priority   = sum(1 for c in complaints if c.get("priority_level") in ("High", "Critical"))
    duplicates      = sum(1 for c in complaints if (c.get("similarity_score") or 0) >= 50.0)
    resolved        = sum(1 for c in complaints if c.get("status") == "Resolved")
    pending         = sum(1 for c in complaints if c.get("status") == "Pending")
    in_progress     = sum(1 for c in complaints if c.get("status") == "In Progress")
    active_sla      = sum(1 for c in complaints if c.get("status") != "Resolved" and c.get("deadline_at") and now <= c["deadline_at"])
    overdue_count   = sum(1 for c in complaints if c.get("status") != "Resolved" and c.get("deadline_at") and now > c["deadline_at"])
    escalated_count = sum(1 for c in complaints if c.get("escalation_level") and "Level 1" not in c["escalation_level"])

    resolution_rate = round((resolved / max(1, total)) * 100.0, 1)

    resolved_items = [
        c for c in complaints
        if c.get("status") == "Resolved" and c.get("resolved_at") and c.get("created_at")
    ]
    if resolved_items:
        total_hours = sum(
            (c["resolved_at"] - c["created_at"]).total_seconds() / 3600.0
            for c in resolved_items
        )
        avg_resolution_hours = round(total_hours / len(resolved_items), 1)
    else:
        avg_resolution_hours = 0.0

    return schemas.DashboardStats(
        total_complaints=total,
        high_priority_count=high_priority,
        duplicate_count=duplicates,
        resolved_count=resolved,
        pending_count=pending,
        in_progress_count=in_progress,
        active_sla_timers=active_sla,
        overdue_count=overdue_count,
        escalated_count=escalated_count,
        resolution_rate=resolution_rate,
        avg_resolution_hours=avg_resolution_hours,
    )


@app.get("/dashboard/analytics", response_model=schemas.AnalyticsResponse)
def get_dashboard_analytics():
    _check_and_update_escalations()
    col = get_complaints_collection()
    complaints = list(col.find())
    stats = get_dashboard_stats()
    now = datetime.utcnow()

    cat_counts = Counter(c.get("category", "Other") for c in complaints)
    category_distribution = [
        schemas.CategoryCount(category=cat, count=cnt)
        for cat, cnt in cat_counts.items()
    ]

    prio_counts = Counter(c.get("priority_level", "Medium") for c in complaints)
    priority_distribution = [
        schemas.PriorityCount(priority_level=p, count=prio_counts.get(p, 0))
        for p in ("Critical", "High", "Medium", "Low")
    ]

    trend_dict: dict = {}
    for i in range(6, -1, -1):
        day_str = (now - timedelta(days=i)).strftime("%b %d")
        trend_dict[day_str] = {"total": 0, "high": 0}

    for c in complaints:
        created = c.get("created_at")
        if created:
            day_str = created.strftime("%b %d")
            if day_str in trend_dict:
                trend_dict[day_str]["total"] += 1
                if c.get("priority_level") in ("High", "Critical"):
                    trend_dict[day_str]["high"] += 1

    complaint_trends = [
        schemas.TrendData(date=k, count=v["total"], high_priority=v["high"])
        for k, v in trend_dict.items()
    ]

    smart_insights: list = []
    if stats.overdue_count > 0:
        smart_insights.append(f"🚨 {stats.overdue_count} SLA Breached issues have been automatically escalated to senior department officers.")
    if stats.escalated_count > 0:
        smart_insights.append(f"⚡ {stats.escalated_count} active complaints are currently under Level 2/Level 3 authority escalation review.")
    if stats.resolution_rate > 0:
        smart_insights.append(f"📈 Municipal resolution efficiency is {stats.resolution_rate}% with avg response time of {stats.avg_resolution_hours} hours.")
    if stats.duplicate_count > 0:
        smart_insights.append(f"🔁 Vector AI engine flagged {stats.duplicate_count} community duplicate reports, aggregating neighborhood urgency.")

    immediate_items = [
        c for c in complaints
        if c.get("status") != "Resolved"
        and (
            c.get("priority_level") in ("Critical", "High")
            or (c.get("deadline_at") and now > c["deadline_at"])
        )
    ]
    immediate_items.sort(
        key=lambda x: (x.get("priority_score", 0), 1 if (x.get("deadline_at") and now > x["deadline_at"]) else 0),
        reverse=True,
    )

    return schemas.AnalyticsResponse(
        stats=stats,
        category_distribution=category_distribution,
        priority_distribution=priority_distribution,
        complaint_trends=complaint_trends,
        smart_insights=smart_insights,
        needs_immediate_attention=[_serialize(c) for c in immediate_items[:6]],
    )
