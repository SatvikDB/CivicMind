# Backend Testing Guide

## Prerequisites

### 1. MongoDB Atlas Setup
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/) and create a free cluster
2. In **Database Access**, create a database user (username + password)
3. In **Network Access**, add your IP address (or `0.0.0.0/0` for dev)
4. Get your connection string:
   ```
   mongodb+srv://<username>:<password>@<cluster>.mongodb.net/civicmind?retryWrites=true&w=majority
   ```

### 2. Configure .env
Edit `backend/.env` with your actual Atlas connection string:
```
MONGO_URI=mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/civicmind?retryWrites=true&w=majority
DB_NAME=civicmind
```

### 3. Install Dependencies
```bash
cd backend
source venv/Scripts/activate
pip install -r requirements.txt
```

---

## Step-by-Step Testing

### Step 1: Start the Server
```bash
cd backend
source venv/Scripts/activate
uvicorn main:app --reload --port 8000
```
**Expected output:**
```
Connected to MongoDB: civicmind
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Health Check
```bash
curl http://localhost:8000/health
```
**Expected:**
```json
{"status": "healthy", "service": "CivicMind AI"}
```

### Step 3: Swagger UI (Manual Testing)
Open browser: **http://localhost:8000/docs**

This gives you an interactive UI to test every endpoint.

---

## Endpoint-by-Endpoint Tests

### A. Submit Complaint (POST /api/complaints)
**The core endpoint — triggers AI analysis.**

```bash
curl -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ravi Kumar",
    "title": "Dangerous pothole on MG Road",
    "description": "There is a large dangerous pothole near the college gate on MG Road. Multiple bikes have fallen here and people are getting injured.",
    "location_name": "MG Road, near City College",
    "latitude": 12.9716,
    "longitude": 77.5946
  }'
```

**Expected response (AI fields should be populated):**
```json
{
  "id": "64a1b2c3...",
  "name": "Ravi Kumar",
  "title": "Dangerous pothole on MG Road",
  "category": "Road",
  "status": "Pending",
  "priority_level": "High",
  "sentiment": "Negative",
  "is_duplicate": false,
  "recommended_action": "Inspect the road within 24 hours...",
  "similarity_score": 0.0,
  "priority_score": <some number>,
  "created_at": "...",
  "updated_at": "..."
}
```

**Verify:** `category` is not "Unknown", `priority_score` > 0, `sentiment` is not "Neutral" (since text has negative words).

### B. Submit a Duplicate Complaint
```bash
curl -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Sharma",
    "title": "Pothole on MG Road causing accidents",
    "description": "The dangerous pothole near college gate on MG Road has caused many bike accidents. People are getting injured regularly.",
    "location_name": "MG Road, near City College",
    "latitude": 12.9720,
    "longitude": 77.5950
  }'
```

**Expected:** `is_duplicate` should be `true`, `duplicate_of` should contain the first complaint's ID, `similarity_score` > 0.70.

### C. List All Complaints (GET /api/complaints)
```bash
curl http://localhost:8000/api/complaints
```
**Expected:** Array of complaints sorted by `created_at` descending.

```bash
curl "http://localhost:8000/api/complaints?skip=0&limit=5"
```
**Expected:** Max 5 results.

### D. Get Single Complaint (GET /api/complaints/{id})
```bash
curl http://localhost:8000/api/complaints/<paste-id-from-step-A>
```
**Expected:** Full complaint object.

**Test 404:**
```bash
curl http://localhost:8000/api/complaints/000000000000000000000000
```
**Expected:** `{"detail": "Complaint not found"}` with 404.

### E. Update Status (PUT /api/complaints/{id}/status)
```bash
curl -X PUT http://localhost:8000/api/complaints/<id>/status \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress"}'
```
**Expected:** Updated complaint with `status: "In Progress"`.

### F. Search Complaints (GET /api/complaints/search)
```bash
curl "http://localhost:8000/api/complaints/search?q=pothole"
curl "http://localhost:8000/api/complaints/search?category=Road"
curl "http://localhost:8000/api/complaints/search?status=Pending"
curl "http://localhost:8000/api/complaints/search?q=road&category=Road"
```

### G. Dashboard Stats (GET /api/dashboard/stats)
```bash
curl http://localhost:8000/api/dashboard/stats
```
**Expected:**
```json
{
  "total_complaints": 2,
  "high_priority": 1,
  "potential_duplicates": 1,
  "resolved": 0
}
```

### H. Dashboard Analytics (GET /api/dashboard/analytics)
```bash
curl http://localhost:8000/api/dashboard/analytics
```
**Expected:** Category distribution, priority distribution, and trend data.

### I. Map Complaints (GET /api/map/complaints)
```bash
curl http://localhost:8000/api/map/complaints
```
**Expected:** Lightweight array with only complaints that have lat/lng.

### J. AI Analyze Standalone (POST /api/ai/analyze)
```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "There is a massive fire near the school. People are trapped and screaming for help."}'
```
**Expected:** Full AI analysis without saving to DB.

---

## Verification Checklist

| Test | What to check |
|------|---------------|
| Health check | Returns "healthy" |
| Submit complaint | AI fields populated (not defaults) |
| Duplicate detection | Second similar complaint flagged |
| List complaints | Sorted by newest first |
| Get by ID | Returns correct complaint |
| Get by ID (bad) | Returns 404 |
| Update status | Status changes, updated_at updates |
| Search | Filters by text, category, status |
| Dashboard stats | Counts are correct |
| Analytics | Has category/priority/trend data |
| Map complaints | Only complaints with coordinates |
| CORS | Frontend at :5173 can call backend |

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'motor'` | Run `pip install -r requirements.txt` in venv |
| `ServerSelectionTimeoutError` | Check Atlas IP whitelist, URI format, credentials |
| `pymongo.errors.ConfigurationError: Password contains @` | URL-encode the `@` as `%40` in .env |
| AI fields stay as defaults | Check `ai_engine.py` imports work, check similarity.py loads model |
| CORS error from frontend | Verify `allow_origins` in main.py includes `http://localhost:5173` |
| `sentence-transformers` slow on first request | Normal — model downloads on first use (~90MB). Subsequent starts are fast. |
| Port 8000 already in use | `uvicorn main:app --port 8001` or kill the other process |

---

## Port Info

| Service | Port |
|---------|------|
| Backend API | `http://localhost:8000` |
| Swagger Docs | `http://localhost:8000/docs` |
| Frontend (Vite) | `http://localhost:5173` |
| Frontend (React) | `http://localhost:3000` |
| MongoDB Atlas | Cloud (configured in .env) |
