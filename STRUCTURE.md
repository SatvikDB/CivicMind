# CivicMind AI — Project Structure Guide

> This document is for the **backend team** and all team members to understand  
> what each portal controls, which APIs power it, and how the files connect.

---

## 🏛️ System Overview

```
CIVICMIND AI
│
├── 👤 CITIZEN PORTAL          (what a regular user can do)
│   ├── Submit Complaint
│   ├── View AI Analysis Result
│   ├── Track Complaint Status
│   └── View Complaints on Map
│
└── 🛡️ ADMIN PORTAL            (what an administrator can do)
    ├── Dashboard & AI Insights
    ├── Complaint Management (list, search, filter, sort)
    ├── Complaint Details & Status Update
    └── Interactive Complaint Map
```

---

## 👤 CITIZEN PORTAL

### What the Citizen Can Do

| Action | Page | API Called |
|---|---|---|
| View landing page & learn about the system | `/` | None |
| Submit a civic complaint with map pin | `/submit` | `POST /complaints` |
| View AI analysis of their complaint | `/result/:id` | `GET /complaints/{id}` |
| See complaint category, priority, severity, recommendation | `/result/:id` | `GET /complaints/{id}` |
| See if their complaint is a duplicate | `/result/:id` | `GET /complaints/{id}` |
| View all complaints on a map | `/map` | `GET /map/complaints` |

### What the Citizen CANNOT Do

- ❌ Access the Admin Dashboard
- ❌ Change the status of a complaint
- ❌ View aggregate statistics or charts
- ❌ Search/filter/sort the full complaints list (admin-only view)

---

## 🛡️ ADMIN PORTAL

### What the Admin Can Do

| Action | Page | API Called |
|---|---|---|
| View total, high-priority, duplicate, resolved counts | `/dashboard` | `GET /dashboard/stats` |
| View category chart, priority chart, trend chart | `/dashboard` | `GET /dashboard/analytics` |
| Read AI-generated smart insights | `/dashboard` | `GET /dashboard/analytics` |
| Browse all complaints with search, filter, sort | `/complaints` | `GET /complaints` |
| Filter complaints by category | `/complaints` | `GET /complaints` (client-side) |
| Filter complaints by severity level | `/complaints` | `GET /complaints` (client-side) |
| Sort by date, priority score, severity | `/complaints` | `GET /complaints` (client-side) |
| View full complaint details + AI analysis | `/complaints/:id` | `GET /complaints/{id}` |
| Read the AI recommendation for a complaint | `/complaints/:id` | `GET /complaints/{id}` |
| Update complaint status (Open → In Progress → Resolved) | `/complaints/:id` | `PUT /complaints/{id}/status` |
| View all complaints on interactive map with markers | `/map` | `GET /map/complaints` |
| Filter map markers by category | `/map` | `GET /map/complaints` (client-side) |

---

## 🔗 Backend API — Full Endpoint Reference

> All endpoints are served by **FastAPI** running on `http://localhost:8000`

### Core Complaint Endpoints (Person 4)

| Method | Endpoint | Who Uses It | What It Does |
|---|---|---|---|
| `POST` | `/complaints` | Citizen | Submit a new complaint. Triggers the full AI pipeline before returning. |
| `GET` | `/complaints` | Admin | Get all complaints (list view, search, filter, sort on frontend). |
| `GET` | `/complaints/{id}` | Citizen + Admin | Get a single complaint by ID with all AI fields. |
| `PUT` | `/complaints/{id}/status` | Admin | Update status to `Open`, `In Progress`, or `Resolved`. |
| `GET` | `/health` | System | Health check — returns `{"status": "ok"}`. |

### Dashboard Endpoints (Person 3 + Person 4)

| Method | Endpoint | Who Uses It | What It Does |
|---|---|---|---|
| `GET` | `/dashboard/stats` | Admin | Returns total, high_priority, duplicates, resolved counts. |
| `GET` | `/dashboard/analytics` | Admin | Returns per-category counts, per-severity counts, complaints by date. |

### Map Endpoint (Person 7 + Person 4)

| Method | Endpoint | Who Uses It | What It Does |
|---|---|---|---|
| `GET` | `/map/complaints` | Citizen + Admin | Returns id, title, category, severity_level, latitude, longitude for all complaints. |

---

## 🤖 AI Pipeline — What Happens When a Complaint is Submitted

When a citizen hits `POST /complaints`, the backend runs this pipeline **automatically** before responding:

```
Complaint submitted
        │
        ▼
1. ai_engine.py        → Detects category (Roads / Water / Electricity / etc.)
        │
        ▼
2. similarity.py       → Checks if complaint is duplicate using cosine similarity
        │
        ▼
3. sentiment_engine.py → Scores sentiment of description (-1.0 to +1.0)
        │
        ▼
4. priority_engine.py  → Calculates priority score (0–100) + severity level
        │
        ▼
5. recommendation_engine.py → Generates resolution recommendation text
        │
        ▼
All results saved to database + returned to citizen
```

> ⚠️ If any AI step fails, the complaint is still saved with safe defaults.  
> The citizen always gets a response — the system never blocks on AI errors.

---

## 🗃️ Database — What Gets Stored Per Complaint

> Managed by **SQLAlchemy + SQLite** in `backend/models.py`

| Field | Type | Set By |
|---|---|---|
| `id` | Integer (auto) | Database |
| `name` | String | Citizen |
| `title` | String | Citizen |
| `description` | Text | Citizen |
| `category` | String | **AI Engine** (or Citizen override) |
| `location_name` | String | Citizen |
| `latitude` | Float | Citizen (map pin) |
| `longitude` | Float | Citizen (map pin) |
| `status` | String | Admin (default: `Open`) |
| `priority_score` | Integer 0–100 | **Priority Engine** |
| `severity_level` | String | **Priority Engine** |
| `sentiment_score` | Float | **Sentiment Engine** |
| `recommendation` | Text | **Recommendation Engine** |
| `is_duplicate` | Boolean | **Similarity Engine** |
| `related_id` | Integer (FK) | **Similarity Engine** |
| `created_at` | DateTime | Database (auto) |

---

## 📁 File Ownership — Who Builds What

### Frontend (`frontend/src/`)

| File | Owner | Portal |
|---|---|---|
| `pages/LandingPage.jsx` | Person 1 | Citizen |
| `components/Navbar.jsx` | Person 1 | Both |
| `components/Hero.jsx` | Person 1 | Citizen |
| `components/Features.jsx` | Person 1 | Citizen |
| `components/HowItWorks.jsx` | Person 1 | Citizen |
| `components/Footer.jsx` | Person 1 | Both |
| `pages/SubmitComplaint.jsx` | Person 2 | Citizen |
| `pages/ComplaintResult.jsx` | Person 2 | Citizen |
| `components/ComplaintForm.jsx` | Person 2 | Citizen |
| `components/AnalysisResult.jsx` | Person 2 | Citizen |
| `pages/Dashboard.jsx` | Person 3 | **Admin** |
| `components/StatCards.jsx` | Person 3 | **Admin** |
| `components/CategoryChart.jsx` | Person 3 | **Admin** |
| `components/PriorityChart.jsx` | Person 3 | **Admin** |
| `components/TrendChart.jsx` | Person 3 | **Admin** |
| `components/SmartInsights.jsx` | Person 3 | **Admin** |
| `pages/Complaints.jsx` | Person 7 | **Admin** |
| `pages/ComplaintDetails.jsx` | Person 7 | **Admin** |
| `pages/ComplaintMap.jsx` | Person 7 | Both |

### Backend (`backend/`)

| File | Owner | Responsibility |
|---|---|---|
| `main.py` | Person 4 | FastAPI app, all routes, AI pipeline orchestration |
| `database.py` | Person 4 | SQLAlchemy engine + session setup |
| `models.py` | Person 4 | `Complaint` ORM model (defines the database table) |
| `schemas.py` | Person 4 | Pydantic request/response schemas |
| `crud.py` | Person 4 | All database read/write operations |
| `ai_engine.py` | Person 5 | Category detection using NLP |
| `similarity.py` | Person 5 | Duplicate detection using sentence embeddings |
| `priority_engine.py` | Person 6 | Priority score (0–100) + severity level |
| `sentiment_engine.py` | Person 6 | Sentiment scoring of complaint description |
| `recommendation_engine.py` | Person 6 | Generates resolution recommendation text |

---

## ⚡ Severity Level Reference

| Priority Score | Severity Level | Map Marker Color |
|---|---|---|
| 0 – 24 | 🟢 Low | Green |
| 25 – 49 | 🟡 Medium | Yellow |
| 50 – 74 | 🟠 High | Orange |
| 75 – 100 | 🔴 Critical | Red |

---

## 🔄 Complaint Status Lifecycle

```
Open  ──►  In Progress  ──►  Resolved
  │                               ▲
  └───────────────────────────────┘
        (can close directly)
```

Only **Admins** can change the status.  
Valid values: `Open` | `In Progress` | `Resolved`

---

## 🚀 How to Run

```bash
# Backend (Person 4 starts this first)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# → Runs on http://localhost:8000
# → API docs at http://localhost:8000/docs

# Frontend
cd frontend
npm install
npm run dev
# → Runs on http://localhost:5173
```

> **Person 4 must set up `database.py` and `models.py` first.**  
> All other backend modules depend on the database being ready.
