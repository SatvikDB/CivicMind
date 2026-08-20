# Design Document — CivicMind AI

## Overview

CivicMind AI is a civic complaint management platform that automates the intake, classification, and prioritisation of citizen-reported issues. Citizens submit complaints through a React-based web UI; the FastAPI backend immediately runs an AI pipeline (category detection → duplicate detection → priority/sentiment scoring → recommendation generation) before persisting the enriched record and returning the result. Administrators then interact with the system through a dashboard with charts, a filterable complaints list, individual complaint detail pages, and an interactive geographic map.

### Key Design Goals

- **Separation of concerns** — Frontend, backend API, database layer, and each AI module are independent and communicate through well-defined interfaces.
- **AI-first enrichment** — Every complaint is fully analysed before the API response is returned, so the citizen immediately sees results.
- **Graceful degradation** — If any AI module fails, the complaint is still persisted with safe defaults; the citizen is never blocked.
- **Team autonomy** — Each of the seven sub-teams owns clearly delimited files and can develop in parallel with minimal merge conflicts.

---

## Architecture

The system follows a three-tier layered architecture with an embedded AI pipeline.

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite + Tailwind)        │
│                                                                   │
│  Pages: LandingPage · SubmitComplaint · ComplaintResult           │
│         Dashboard · Complaints · ComplaintDetails · ComplaintMap  │
│  Components: Navbar · Forms · Charts (Chart.js) · Map (Leaflet)  │
└───────────────────────────┬─────────────────────────────────────┘
                            │  HTTP/REST (JSON)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                    │
│                                                                   │
│  Routers: /complaints · /dashboard · /map · /health              │
│  Layer:   schemas.py (Pydantic) → crud.py → models.py            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   AI PIPELINE (inline)                   │   │
│  │  ai_engine.py ──► similarity.py                          │   │
│  │  priority_engine.py ──► sentiment_engine.py              │   │
│  │  recommendation_engine.py                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │  SQLAlchemy ORM
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (SQLite via SQLAlchemy)               │
│                   complaints table (single-table design)          │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow — Complaint Submission

```
Browser
  │─── POST /complaints ──────────────────────────────────────────►
                                                          FastAPI Router
                                                              │
                                                     Pydantic validation
                                                              │
                                                     CRUD: INSERT complaint (status=Open)
                                                              │
                                                       ┌──────▼───────┐
                                                       │  AI PIPELINE  │
                                                       │  1. ai_engine │
                                                       │     category  │
                                                       │  2. similarity│
                                                       │     duplicate │
                                                       │  3. sentiment │
                                                       │     score     │
                                                       │  4. priority  │
                                                       │     score +   │
                                                       │     severity  │
                                                       │  5. recommend │
                                                       └──────┬───────┘
                                                              │
                                                     CRUD: UPDATE complaint
                                                       (AI fields)
                                                              │
  ◄────────── HTTP 201 + enriched complaint JSON ────────────┘
```

### Technology Choices

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React 18 + Vite + Tailwind CSS | Fast HMR, utility-first styling, large ecosystem |
| Routing | React Router v6 | Client-side SPA navigation |
| Charts | Chart.js (via react-chartjs-2) | Mature, customisable, lightweight |
| Map | Leaflet + OpenStreetMap (via react-leaflet) | Open-source, no API key required |
| Backend | FastAPI (Python 3.11+) | Async I/O, auto OpenAPI docs, Pydantic integration |
| ORM | SQLAlchemy 2.0 (synchronous session for simplicity) | Declarative models, migrations-ready |
| Database | SQLite | Zero-config for team development; swap path for production Postgres |
| NLP Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | 384-dim dense vectors, fast CPU inference, 80 MB model |
| Sentiment | `VADER` (nltk) or `transformers` pipeline | Lexicon-based VADER is lightweight; upgrade path to transformer-based |
| PBT library | `hypothesis` (Python) | Native Python, excellent integration with pytest |

---

## Components and Interfaces

### Frontend Components

#### Page Components

| Component | Route | Responsibility |
|---|---|---|
| `LandingPage.jsx` | `/` | Renders Hero, Features, HowItWorks, Footer |
| `SubmitComplaint.jsx` | `/submit` | Hosts `ComplaintForm`, handles POST, redirects on success |
| `ComplaintResult.jsx` | `/result/:id` | Displays `AnalysisResult` for a complaint ID |
| `Dashboard.jsx` | `/dashboard` | Fetches stats + analytics, renders Stat_Cards + charts |
| `Complaints.jsx` | `/complaints` | Fetches complaint list, search/filter/sort/pagination |
| `ComplaintDetails.jsx` | `/complaints/:id` | Full detail view + status update control |
| `ComplaintMap.jsx` | `/map` | Leaflet map with markers, popups, category filter |

#### Reusable Components

| Component | Props Interface | Responsibility |
|---|---|---|
| `Navbar.jsx` | — | Top nav, active route highlight, mobile menu toggle |
| `ComplaintForm.jsx` | `onSuccess(complaint)` | Controlled form, field validation, map pin picker |
| `AnalysisResult.jsx` | `complaint: ComplaintDetail` | Displays AI fields, duplicate notice, success message |
| `StatCards.jsx` | `stats: DashboardStats` | Four metric cards |
| `CategoryChart.jsx` | `data: CategoryCount[]` | Doughnut/bar chart of categories |
| `PriorityChart.jsx` | `data: SeverityCount[]` | Bar chart of severity levels |
| `TrendChart.jsx` | `data: DateCount[]` | Line chart of complaints over time |
| `SmartInsights.jsx` | `analytics: AnalyticsPayload` | Derived text insights panel |

#### API Client (`frontend/src/api/`)

All HTTP calls are centralised in an `api.js` module that wraps `fetch` (or Axios). Endpoints mirror the backend routes listed in the requirements.

```js
// api.js interface (TypeScript-style notation for clarity)
submitComplaint(payload: ComplaintCreate): Promise<ComplaintDetail>
getComplaints(): Promise<ComplaintDetail[]>
getComplaintById(id: number): Promise<ComplaintDetail>
updateComplaintStatus(id: number, status: string): Promise<ComplaintDetail>
getDashboardStats(): Promise<DashboardStats>
getDashboardAnalytics(): Promise<AnalyticsPayload>
getMapComplaints(): Promise<MapComplaint[]>
```

---

### Backend Components

#### Module Responsibilities

| File | Responsibility |
|---|---|
| `main.py` | FastAPI app factory, router registration, CORS config, startup event |
| `database.py` | SQLAlchemy engine + session factory, `get_db` dependency |
| `models.py` | SQLAlchemy ORM `Complaint` model |
| `schemas.py` | Pydantic `ComplaintCreate`, `ComplaintDetail`, `DashboardStats`, `AnalyticsPayload`, `MapComplaint`, `StatusUpdate` |
| `crud.py` | All database operations: `create_complaint`, `update_complaint_ai_fields`, `get_complaint`, `get_complaints`, `update_status`, `get_stats`, `get_analytics`, `get_map_complaints` |
| `ai_engine.py` | `detect_category(title, description) → str` |
| `similarity.py` | `check_duplicate(description, existing_complaints) → (bool, int | None)` |
| `priority_engine.py` | `compute_priority(category, description, sentiment_score) → (int, str)` |
| `sentiment_engine.py` | `analyze_sentiment(description) → float` |
| `recommendation_engine.py` | `generate_recommendation(category, severity, sentiment_score) → str` |

#### AI Pipeline Orchestration (inside `main.py` POST /complaints handler)

```python
def run_ai_pipeline(complaint_text: str, title: str, existing: list[Complaint]) -> AIResult:
    try:
        category = ai_engine.detect_category(title, complaint_text)
    except Exception:
        category = "General"

    try:
        is_dup, related_id = similarity.check_duplicate(complaint_text, existing)
    except Exception:
        is_dup, related_id = False, None

    try:
        sentiment = sentiment_engine.analyze_sentiment(complaint_text)
    except Exception:
        sentiment = 0.0

    try:
        priority, severity = priority_engine.compute_priority(category, complaint_text, sentiment)
    except Exception:
        priority, severity = 0, "Low"

    try:
        recommendation = recommendation_engine.generate_recommendation(category, severity, sentiment)
    except Exception:
        recommendation = "Please review this complaint manually."

    return AIResult(category, is_dup, related_id, sentiment, priority, severity, recommendation)
```

#### API Endpoint Summary

| Method | Path | Handler | Auth |
|---|---|---|---|
| POST | `/complaints` | `create_complaint` | None |
| GET | `/complaints` | `list_complaints` | None |
| GET | `/complaints/{id}` | `get_complaint` | None |
| PUT | `/complaints/{id}/status` | `update_status` | None |
| GET | `/health` | `health_check` | None |
| GET | `/dashboard/stats` | `dashboard_stats` | None |
| GET | `/dashboard/analytics` | `dashboard_analytics` | None |
| GET | `/map/complaints` | `map_complaints` | None |

---

## Data Models

### SQLAlchemy ORM Model (`models.py`)

```python
class Complaint(Base):
    __tablename__ = "complaints"

    id               = Column(Integer, primary_key=True, index=True)
    name             = Column(String, nullable=False)
    title            = Column(String, nullable=False)
    description      = Column(Text, nullable=False)
    category         = Column(String, nullable=False, default="General")
    location_name    = Column(String, nullable=False)
    latitude         = Column(Float, nullable=True)
    longitude        = Column(Float, nullable=True)
    status           = Column(String, nullable=False, default="Open")
    priority_score   = Column(Integer, nullable=True)       # 0–100
    severity_level   = Column(String, nullable=True)        # Low/Medium/High/Critical
    sentiment_score  = Column(Float, nullable=True)
    recommendation   = Column(Text, nullable=True)
    is_duplicate     = Column(Boolean, nullable=False, default=False)
    related_id       = Column(Integer, ForeignKey("complaints.id"), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
```

### Pydantic Schemas (`schemas.py`)

```python
# Request
class ComplaintCreate(BaseModel):
    name: str
    title: str
    description: str
    category: str
    location_name: str
    latitude: float | None = None
    longitude: float | None = None

# Response (full record)
class ComplaintDetail(ComplaintCreate):
    id: int
    status: str
    priority_score: int | None
    severity_level: str | None
    sentiment_score: float | None
    recommendation: str | None
    is_duplicate: bool
    related_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True

# Status update
class StatusUpdate(BaseModel):
    status: Literal["Open", "In Progress", "Resolved"]

# Dashboard
class DashboardStats(BaseModel):
    total: int
    high_priority: int   # severity High or Critical
    duplicates: int
    resolved: int

class CategoryCount(BaseModel):
    category: str
    count: int

class SeverityCount(BaseModel):
    severity_level: str
    count: int

class DateCount(BaseModel):
    date: str   # ISO date string
    count: int

class AnalyticsPayload(BaseModel):
    by_category: list[CategoryCount]
    by_severity: list[SeverityCount]
    by_date: list[DateCount]

# Map
class MapComplaint(BaseModel):
    id: int
    title: str
    category: str
    severity_level: str | None
    latitude: float | None
    longitude: float | None
```

### Severity Mapping

| Priority Score Range | Severity Level |
|---|---|
| 0 – 24 | Low |
| 25 – 49 | Medium |
| 50 – 74 | High |
| 75 – 100 | Critical |

### Status Lifecycle

```
Open ──► In Progress ──► Resolved
  │                         ▲
  └─────────────────────────┘  (direct close)
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Priority score is always within bounds

*For any* complaint description, category, and sentiment score (in the valid range), the `compute_priority` function SHALL return a Priority_Score that is an integer in the closed interval [0, 100].

**Validates: Requirements 9.1**

---

### Property 2: Severity level mapping is total and consistent with priority score

*For any* integer Priority_Score in [0, 100], the `score_to_severity` function SHALL return exactly one of {"Low", "Medium", "High", "Critical"} according to the defined four-band mapping: 0–24 → Low, 25–49 → Medium, 50–74 → High, 75–100 → Critical. No score may yield a label outside this set, and every integer in [0, 100] must map to exactly one label.

**Validates: Requirements 9.2**

---

### Property 3: Category detection always returns a valid, non-empty category

*For any* complaint title and description (including edge-case inputs such as empty strings, numeric text, or nonsensical content), `detect_category` SHALL return a non-empty string that is a member of the predefined category set ∪ {"General"}. It SHALL never return `None` or raise an unhandled exception.

**Validates: Requirements 7.1, 7.3**

---

### Property 4: Duplicate detection output is consistent with the similarity threshold

*For any* new complaint description and any list of existing complaint descriptions, the output of `check_duplicate` must agree with a manual threshold comparison: if the maximum cosine similarity between the new embedding and all existing embeddings is strictly below the Similarity_Threshold then the result SHALL be `(False, None)`; if it is at or above the threshold the result SHALL be `(True, <id of the most-similar complaint>)`. The two cases are exhaustive and mutually exclusive.

**Validates: Requirements 8.1, 8.2**

---

### Property 5: AI pipeline failure does not block complaint persistence

*For any* valid complaint payload, if any single AI module (category detection, duplicate detection, sentiment analysis, priority scoring, or recommendation) raises an unhandled exception, the Backend SHALL still persist the complaint record with safe default values for the affected fields and return HTTP 201. No combination of AI module failures should cause a non-201 response for an otherwise valid payload.

**Validates: Requirements 17.3**

---

### Property 6: Complaint round-trip preserves all submitted and AI-enriched fields

*For any* valid `ComplaintCreate` payload, submitting it via POST `/complaints` and retrieving the result via GET `/complaints/{id}` SHALL return a record where (a) the user-submitted fields (`name`, `title`, `description`, `category`, `location_name`, `latitude`, `longitude`) are identical to the submitted values, and (b) all AI enrichment fields (`category`, `priority_score`, `severity_level`, `sentiment_score`, `recommendation`, `is_duplicate`) are present and not `None` (or contain their defined safe defaults when AI modules run with defaults).

**Validates: Requirements 5.1, 5.4, 6.1, 17.1, 17.2**

---

### Property 7: Status update is idempotent

*For any* complaint and any valid status value from {"Open", "In Progress", "Resolved"}, sending a PUT `/complaints/{id}/status` request twice in succession with the same status value SHALL produce the same resulting complaint state as sending it once — the status in the database and in the response SHALL equal the submitted value after both the first and second request.

**Validates: Requirements 5.6**

---

### Property 8: Dashboard stats are non-negative and internally consistent with the database state

*For any* database state containing N complaint records, the four counts returned by GET `/dashboard/stats` (`total`, `high_priority`, `duplicates`, `resolved`) SHALL each be non-negative integers, `total` SHALL equal N, `high_priority ≤ total`, `duplicates ≤ total`, and `resolved ≤ total`.

**Validates: Requirements 12.4**

---

### Property 9: Client-side complaint filtering is sound

*For any* list of complaints and any active filter (by Category, by Severity_Level, or by text search term), every complaint displayed after filtering SHALL satisfy the filter predicate: its `category` equals the selected category filter (if applied), its `severity_level` equals the selected severity filter (if applied), and its `title` or `description` contains the search term as a substring (if applied). No complaint that fails any active predicate SHALL appear in the filtered results.

**Validates: Requirements 14.2, 14.3, 14.4**

---

### Property 10: Map markers correspond one-to-one with complaints and are color-coded correctly

*For any* list of N map complaints returned by GET `/map/complaints`, the Map component SHALL render exactly N markers. *For any* marker corresponding to a complaint with a given Severity_Level, the marker SHALL use the color defined by the severity-to-color mapping: Low → green, Medium → yellow, High → orange, Critical → red.

**Validates: Requirements 16.1, 16.4**

---

### Property 11: AI fields are rendered on both the Analysis Result and Complaint Details pages

*For any* valid `ComplaintDetail` object, rendering both `AnalysisResult` and `ComplaintDetails` with that object SHALL produce DOM output containing all five AI fields: Category, Severity_Level, Priority_Score, Sentiment_Score, and Recommendation. None of these fields SHALL be absent or empty in the rendered output when the underlying data is non-null.

**Validates: Requirements 4.1, 11.3, 15.1, 15.2**

---

## Error Handling

### Backend Error Strategy

| Scenario | HTTP Status | Response Body |
|---|---|---|
| Missing / invalid request fields | 422 | Pydantic validation detail |
| Complaint ID not found | 404 | `{"detail": "Complaint not found"}` |
| Invalid status value in PUT | 422 | Pydantic validation detail |
| AI module unhandled exception | — | Logged; complaint saved with defaults; HTTP 201 returned |
| Database connection error | 500 | `{"detail": "Internal server error"}` |
| Unhandled server exception | 500 | `{"detail": "Internal server error"}` |

All unhandled exceptions are caught by a global FastAPI exception handler registered in `main.py`. Errors are logged to stdout using Python's standard `logging` module at ERROR level.

### Frontend Error Strategy

| Scenario | UI Behaviour |
|---|---|
| Form field missing on submit | Inline field-level error message; submission blocked |
| POST /complaints network error | Toast/alert with descriptive message; form remains editable |
| GET `/complaints/{id}` 404 | "Complaint not found" page message |
| PUT status update failure | Error message shown; displayed status not changed |
| Dashboard stats/analytics error | Error state displayed in place of cards/charts |

### AI Graceful Defaults

| Module | Default on failure |
|---|---|
| `ai_engine` (category) | `"General"` |
| `similarity` (duplicate) | `is_duplicate=False, related_id=None` |
| `sentiment_engine` | `sentiment_score=0.0` |
| `priority_engine` | `priority_score=0, severity_level="Low"` |
| `recommendation_engine` | `"Please review this complaint manually."` |

---

## Testing Strategy

### Overview

Testing follows a dual-layer approach:

1. **Unit / example-based tests** — verify specific behaviours, integration points, edge cases, and error conditions.
2. **Property-based tests** — verify universal correctness properties across randomly generated inputs using the `hypothesis` library.

### Backend Unit Tests (`pytest`)

| Test Module | What it covers |
|---|---|
| `test_crud.py` | CRUD operations against an in-memory SQLite test database |
| `test_api.py` | FastAPI endpoint integration tests using `TestClient` |
| `test_ai_engine.py` | Category detection output is always a known label |
| `test_similarity.py` | Threshold logic; known similar/dissimilar pairs |
| `test_priority_engine.py` | Score-to-severity mapping correctness |
| `test_sentiment_engine.py` | Positive/negative/neutral descriptions |
| `test_recommendation_engine.py` | Non-empty recommendation for all category × severity combinations |

### Property-Based Tests (`pytest` + `hypothesis`)

Each of the 11 correctness properties maps to exactly one `@given`-decorated test. Minimum 100 iterations per test (Hypothesis `settings(max_examples=100)` applied globally). Each test is tagged with a comment referencing the design property number and text.

```python
# Feature: civicmind-ai, Property 1: Priority score is always within bounds
@given(
    category=st.sampled_from(CATEGORIES),
    description=st.text(min_size=1),
    sentiment=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False)
)
def test_priority_score_bounds(category, description, sentiment):
    score, _ = compute_priority(category, description, sentiment)
    assert 0 <= score <= 100
```

```python
# Feature: civicmind-ai, Property 2: Severity level mapping is total and consistent with priority score
@given(st.integers(min_value=0, max_value=100))
def test_severity_mapping_completeness(score):
    severity = score_to_severity(score)
    assert severity in {"Low", "Medium", "High", "Critical"}
    if 0 <= score <= 24:   assert severity == "Low"
    elif 25 <= score <= 49: assert severity == "Medium"
    elif 50 <= score <= 74: assert severity == "High"
    else:                   assert severity == "Critical"
```

```python
# Feature: civicmind-ai, Property 3: Category detection always returns a valid, non-empty category
@given(title=st.text(), description=st.text())
def test_category_always_valid(title, description):
    result = detect_category(title, description)
    assert result is not None
    assert result != ""
    assert result in VALID_CATEGORIES | {"General"}
```

```python
# Feature: civicmind-ai, Property 4: Duplicate detection output is consistent with the similarity threshold
@given(
    new_desc=st.text(min_size=5, max_size=200),
    existing_descs=st.lists(st.text(min_size=5, max_size=200), min_size=0, max_size=10)
)
def test_duplicate_detection_threshold_consistency(new_desc, existing_descs):
    # Build mock existing complaints with sequential IDs
    existing = [SimpleNamespace(id=i, description=d) for i, d in enumerate(existing_descs)]
    is_dup, related_id = check_duplicate(new_desc, existing)
    # Structural consistency
    if not is_dup:
        assert related_id is None
    else:
        assert related_id is not None
        assert any(c.id == related_id for c in existing)
```

```python
# Feature: civicmind-ai, Property 5: AI pipeline failure does not block complaint persistence
@pytest.mark.parametrize("failing_module", ["ai_engine", "similarity", "sentiment_engine",
                                             "priority_engine", "recommendation_engine"])
@given(payload=complaint_create_strategy())
def test_ai_failure_still_returns_201(failing_module, payload, test_client, monkeypatch):
    monkeypatch.setattr(failing_module, MOCK_RAISE)
    resp = test_client.post("/complaints", json=payload.dict())
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
```

```python
# Feature: civicmind-ai, Property 6: Complaint round-trip preserves all submitted and AI-enriched fields
@given(payload=complaint_create_strategy())
def test_complaint_roundtrip(payload, test_client):
    post_resp = test_client.post("/complaints", json=payload.dict())
    assert post_resp.status_code == 201
    cid = post_resp.json()["id"]
    get_resp = test_client.get(f"/complaints/{cid}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["name"] == payload.name
    assert data["title"] == payload.title
    assert data["description"] == payload.description
    assert data["location_name"] == payload.location_name
    # AI fields present (may be defaults but not absent)
    for field in ("category", "priority_score", "severity_level", "sentiment_score", "recommendation"):
        assert field in data
```

```python
# Feature: civicmind-ai, Property 7: Status update is idempotent
@given(status=st.sampled_from(["Open", "In Progress", "Resolved"]))
def test_status_update_idempotent(status, test_client, seeded_complaint_id):
    url = f"/complaints/{seeded_complaint_id}/status"
    r1 = test_client.put(url, json={"status": status})
    r2 = test_client.put(url, json={"status": status})
    assert r1.status_code == r2.status_code == 200
    assert r1.json()["status"] == r2.json()["status"] == status
```

```python
# Feature: civicmind-ai, Property 8: Dashboard stats are non-negative and consistent with DB state
@given(n=st.integers(min_value=0, max_value=30))
def test_dashboard_stats_consistency(n, test_client, fresh_db):
    for _ in range(n):
        test_client.post("/complaints", json=random_complaint_payload())
    stats = test_client.get("/dashboard/stats").json()
    assert stats["total"] == n
    assert 0 <= stats["high_priority"] <= n
    assert 0 <= stats["duplicates"] <= n
    assert 0 <= stats["resolved"] <= n
```

```python
# Feature: civicmind-ai, Property 9: Client-side complaint filtering is sound
@given(
    complaints=st.lists(complaint_detail_strategy(), min_size=0, max_size=20),
    category_filter=st.one_of(st.none(), st.sampled_from(CATEGORIES)),
    severity_filter=st.one_of(st.none(), st.sampled_from(SEVERITY_LEVELS)),
    search_term=st.one_of(st.none(), st.text(max_size=20))
)
def test_filter_soundness(complaints, category_filter, severity_filter, search_term):
    result = apply_filters(complaints, category_filter, severity_filter, search_term)
    for c in result:
        if category_filter:   assert c.category == category_filter
        if severity_filter:   assert c.severity_level == severity_filter
        if search_term:       assert search_term.lower() in (c.title + c.description).lower()
```

```python
# Feature: civicmind-ai, Property 10: Map markers correspond one-to-one with complaints and are color-coded correctly
@given(complaints=st.lists(map_complaint_strategy(), min_size=0, max_size=20))
def test_map_markers_count_and_color(complaints):
    markers = build_markers(complaints)  # pure function under test
    assert len(markers) == len(complaints)
    for complaint, marker in zip(complaints, markers):
        expected_color = SEVERITY_COLOR_MAP[complaint.severity_level]
        assert marker["color"] == expected_color
```

```python
# Feature: civicmind-ai, Property 11: AI fields are rendered on both analysis result and complaint details pages
@given(complaint=complaint_detail_strategy())
def test_ai_fields_rendered(complaint):
    for render_fn in (render_analysis_result, render_complaint_details):
        html = render_fn(complaint)
        assert str(complaint.category) in html
        assert str(complaint.severity_level) in html
        assert str(complaint.priority_score) in html
        assert str(complaint.sentiment_score) in html
        assert complaint.recommendation in html
```

### Frontend Tests (`vitest` + `@testing-library/react`)

| Test | Type | Coverage |
|---|---|---|
| Complaint form validation prevents empty submit | Unit | Req 3.3 |
| Loading indicator shown while POST in-flight | Unit | Req 3.4 |
| AnalysisResult renders all AI fields | Unit | Req 4.1 |
| Duplicate notice appears when `is_duplicate=true` | Unit | Req 4.2 |
| StatCards render four metrics | Unit | Req 12.2 |
| Charts render without crashing | Snapshot | Req 13.2–4 |
| Map markers render with correct colours | Unit | Req 16.4 |
| Status dropdown sends PUT request | Unit | Req 15.4 |

### Test Configuration

- Hypothesis: `settings(max_examples=100, deadline=None)` applied globally via `conftest.py`
- FastAPI `TestClient` used with an in-memory SQLite override (`sqlite:///:memory:`)
- Sentence Transformers model is mocked in unit tests to avoid 80 MB download in CI
- Frontend test runner: `vitest --run` (single pass, no watch mode)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

**Property Reflection Summary:** After prework analysis, duplicate and overlapping properties from requirements 2.1/2.4, 5.1/5.4/6.1/17.1/17.2, 5.2/6.4, 4.1/15.1/15.2, and 14.2/14.3/14.4 were each consolidated into single comprehensive properties. The final set of 11 properties covers all testable acceptance criteria with no redundancy.

---

### Property 1: Valid Form Submission Sends Correct POST Payload

*For any* valid complaint form data (any name, title, description, location, category, and lat/lon coordinates), submitting the form must trigger exactly one POST request to `/complaints` whose JSON body contains all submitted field values unchanged.

**Validates: Requirements 3.2**

---

### Property 2: Form Validation Rejects Incomplete Submissions

*For any* complaint form where at least one required field (name, title, description, category, location name, or map pin) is empty or contains only whitespace characters, the form submission should be blocked — no POST request is made and a field-level validation error is displayed for each offending field.

**Validates: Requirements 3.3**

---

### Property 3: Analysis Result Renders All AI Fields

*For any* complaint record returned from the backend with any combination of AI field values (category, severity level, priority score, sentiment score, recommendation), the `AnalysisResult` component must render all five of those fields visibly in the UI.

**Validates: Requirements 4.1, 11.3**

---

### Property 4: Complaint Creation Round-Trip

*For any* valid `ComplaintCreate` payload (varying names, titles, descriptions, categories, location names, and geographic coordinates), a POST to `/complaints` must: (a) return HTTP 201, (b) return a response body containing all submitted field values with an auto-assigned integer `id` and a `created_at` timestamp, and (c) make the record retrievable via GET `/complaints/{id}` with identical field values.

**Validates: Requirements 5.1, 5.4, 6.1**

---

### Property 5: Invalid Payload Rejected with 422

*For any* POST request to `/complaints` that is missing one or more required fields (name, title, description, category, location_name, latitude, or longitude), the backend must return HTTP 422 and must not create a new database record.

**Validates: Requirements 5.2**

---

### Property 6: Status Update Round-Trip

*For any* existing complaint and *for any* valid status value from the set `{"Open", "In Progress", "Resolved"}`, a PUT request to `/complaints/{id}/status` must return HTTP 200 with the complaint record showing the new status, and a subsequent GET `/complaints/{id}` must reflect the same updated status.

**Validates: Requirements 5.6, 15.3, 15.4**

---

### Property 7: Category Detection Output Is Always In-Vocabulary

*For any* (title, description) text pair, `detect_category()` must return a value that is a member of the predefined `CATEGORIES` list (`["Roads", "Water", "Electricity", "Sanitation", "Public Safety", "Parks", "Noise", "General"]`). The function must never return a string outside this set, and must fall back to `"General"` when no category can be determined with sufficient confidence.

**Validates: Requirements 7.1, 7.3**

---

### Property 8: Duplicate Detection Threshold Invariant

*For any* new complaint description and any list of existing complaint descriptions:
- When the maximum cosine similarity between the new description's embedding and any existing embedding is **above** `SIMILARITY_THRESHOLD` (0.75), `detect_duplicate()` must return `(True, id_of_most_similar)`.
- When the maximum cosine similarity is **at or below** `SIMILARITY_THRESHOLD`, `detect_duplicate()` must return `(False, None)`.

In particular, for any description `d`, `detect_duplicate(d, [(1, d)])` must return `(True, 1)` (identical text is always a duplicate).

**Validates: Requirements 8.1, 8.2**

---

### Property 9: Sentiment Score Is In Valid Range

*For any* non-empty text string, `compute_sentiment()` must return a float value `s` such that `-1.0 <= s <= 1.0`.

**Validates: Requirements 10.1**

---

### Property 10: Priority Score Range and Severity Mapping Consistency

*For any* valid inputs `(category, description, sentiment_score)`, `compute_priority()` must return a `(priority_score, severity_level)` pair such that:
- `0.0 <= priority_score <= 100.0`
- `severity_level` is exactly the label defined by the mapping: score 0–24 → `"Low"`, 25–49 → `"Medium"`, 50–74 → `"High"`, 75–100 → `"Critical"`

These two conditions must hold simultaneously — the score and its derived label must never be inconsistent.

**Validates: Requirements 9.1, 9.2**

---

### Property 11: Recommendation Is Always Non-Empty

*For any* valid `(category, severity_level, sentiment_score)` input — where `category` is any member of `CATEGORIES` and `severity_level` is any member of `{"Low", "Medium", "High", "Critical"}` — `generate_recommendation()` must return a non-empty string of at least one word.

**Validates: Requirements 11.1**

---

### Property 12: Dashboard Stats Are Consistent with Database State

*For any* set of complaints in the database, a GET request to `/dashboard/stats` must return counts such that:
- `total` equals the actual count of all complaints,
- `high_priority` equals the count of complaints with severity_level `"High"` or `"Critical"`,
- `duplicates` equals the count of complaints where `is_duplicate = True`,
- `resolved` equals the count of complaints where `status = "Resolved"`.

None of these values may be under- or over-counted relative to the database state at request time.

**Validates: Requirements 12.4**

---

### Property 13: Dashboard Analytics Category and Severity Counts Are Accurate

*For any* set of complaints in the database, a GET request to `/dashboard/analytics` must return `category_counts` and `severity_counts` dictionaries such that the count for each key equals the exact number of complaints in the database with that category or severity level, respectively. No category or severity level present in the database may be omitted from the response.

**Validates: Requirements 13.6**

---

### Property 14: Client-Side Text Search Returns Only Matching Complaints

*For any* list of complaints and *for any* non-empty search query string, every complaint in the filtered display result must contain the query string (case-insensitive) in either its `title` or `description` field. No complaint that does not match the query may appear in the filtered results.

**Validates: Requirements 14.2, 16.5**

---

### Property 15: Map Complaints Endpoint Returns Complete Location Data

*For any* set of complaints in the database, every record returned by GET `/map/complaints` must have non-null values for all of: `id`, `title`, `category`, `latitude`, `longitude`. The count of records returned must equal the total number of complaints in the database.

**Validates: Requirements 16.2**

---

### Property 16: Marker Color Mapping Is Total and Correct

*For any* severity level value in `{"Low", "Medium", "High", "Critical"}`, the marker color function must return exactly the corresponding color: Low → `green`, Medium → `yellow`, High → `orange`, Critical → `red`. The function must never return an unrecognized color string and must cover all four severity values.

**Validates: Requirements 16.4**

---

### Property 17: AI Pipeline Always Enriches Submitted Complaints

*For any* valid complaint payload submitted to POST `/complaints`, when all AI components execute without exception, the response body must contain non-null, non-empty values for `category`, `priority_score`, `severity_level`, `sentiment_score`, and `recommendation`. The `category` field must be in-vocabulary (Property 7), and `severity_level` must be consistent with `priority_score` (Property 10).

**Validates: Requirements 17.1, 17.2**

---

### Property 18: AI Pipeline Fault Tolerance

*For any* valid complaint payload submitted to POST `/complaints`, when one or more AI components raise an unhandled exception during processing, the backend must still return HTTP 201 with the complaint record. AI fields affected by the failing component must be `null` or default values — the backend must never return HTTP 500 due to an AI component failure alone.

**Validates: Requirements 17.3**

---

## Error Handling

### Frontend Error Handling

| Scenario | Behavior |
|---|---|
| POST `/complaints` fails (network or 5xx) | Display inline error message in `SubmitComplaint`; form re-enabled |
| POST `/complaints` returns 422 | Display field-level validation errors from response body |
| GET `/complaints/{id}` returns 404 | Show "Complaint not found" message in `ComplaintResult` / `ComplaintDetails` |
| GET `/dashboard/stats` or `/analytics` fails | Show error banner in `Dashboard` instead of stat cards and charts |
| PUT `/complaints/{id}/status` fails | Display error toast/message in `ComplaintDetails`; status select reverts to previous value |
| Map data fetch fails | Show error overlay on the map container |
| Network offline | All fetch calls should surface a user-readable "Could not connect to server" message |

**Implementation pattern:**
- All API calls wrapped in `try/catch` with loading, success, and error states managed via `useState`.
- Errors displayed inline near the triggering UI element, not in modal dialogs.
- Loading states disable submit/action buttons to prevent duplicate requests.

### Backend Error Handling

| Scenario | HTTP Response |
|---|---|
| Missing/invalid request fields | 422 Unprocessable Entity with Pydantic error detail |
| Complaint ID not found | 404 Not Found with `{"detail": "Complaint not found"}` |
| Invalid status value in PUT | 422 with detail |
| AI component exception | Log exception; persist complaint with null AI fields; return 201 |
| Database error (connection, constraint) | 500 Internal Server Error with generic message; error logged server-side |

**Implementation notes:**
- FastAPI's built-in Pydantic validation handles 422 responses automatically.
- Custom `HTTPException` raised for 404 cases.
- The AI pipeline is wrapped in a `try/except` block in `main.py`; each AI module call is individually guarded so a failure in one (e.g., embedding model) does not prevent others from running.
- All exceptions logged with `logging` module at `ERROR` level with full traceback.

### AI/ML Error Handling

| Scenario | Behavior |
|---|---|
| Sentence Transformer model fails to load | Log error; `detect_duplicate` returns `(False, None)`; `detect_category` returns `"General"` |
| Empty description passed to similarity | Returns `(False, None)` |
| Sentiment model unavailable | Returns `sentiment_score = 0.0` (neutral) |
| Priority engine receives unknown category | Uses default category weight |
| Recommendation template not found | Returns generic fallback string |

---

## Testing Strategy

### Dual Testing Approach

Testing uses both example-based unit tests and property-based tests:

- **Unit/Example tests** verify specific, concrete behaviors: API contract examples, UI rendering checks, error state handling, integration wiring.
- **Property-based tests** verify universal invariants across large randomized input spaces: AI function outputs, API round-trips, data consistency, filtering correctness.

Both are complementary. Unit tests catch concrete regressions; property tests find edge cases and boundary violations that humans don't think to write examples for.

### Property-Based Testing Framework

**Library:** `hypothesis` (Python) for backend and AI/ML modules; `fast-check` (JavaScript) for frontend filtering logic.

**Configuration:**
- Minimum **100 iterations** per property test.
- Each property test is tagged with a comment referencing its design property number.
- Tag format: `# Feature: civicmind-ai, Property {N}: {property_text}`

**Example tag (Python):**
```python
@given(...)
@settings(max_examples=100)
# Feature: civicmind-ai, Property 7: Category detection output is always in-vocabulary
def test_category_always_in_vocabulary(title, description):
    ...
```

**Example tag (JavaScript):**
```javascript
// Feature: civicmind-ai, Property 14: Client-side text search returns only matching complaints
fc.assert(fc.property(...))
```

### Unit Tests

#### Frontend (Vitest + React Testing Library)

| Component/Page | Test Focus |
|---|---|
| `Navbar` | Active link highlighting, mobile menu toggle, all nav links present |
| `ComplaintForm` | All fields render, validation messages appear for empty fields, successful submit calls onSubmit |
| `AnalysisResult` | Renders all 5 AI fields, duplicate banner conditional on `is_duplicate` |
| `Dashboard` | Error state renders when fetch fails, stats and charts render on success |
| `ComplaintDetails` | Status dropdown present, PUT called on status change, error shown on PUT failure |
| `ComplaintMap` | Markers render, category filter hides non-matching markers, popup shows on click |

#### Backend (pytest)

| Module | Test Focus |
|---|---|
| `main.py` routes | GET /health returns 200, GET /complaints returns list, 404 for unknown ID |
| `crud.py` | Create, read, update operations with in-memory SQLite fixture |
| `ai_engine.py` | Category detection returns valid category, fallback to "General" |
| `similarity.py` | Identical texts → duplicate; very different texts → not duplicate |
| `sentiment_engine.py` | Output in [-1, 1] range for various inputs |
| `priority_engine.py` | Score in [0, 100], severity label matches score range |
| `recommendation_engine.py` | Returns non-empty string for all category/severity combinations |

### Property-Based Tests

| Property | Module Under Test | Library | Iterations |
|---|---|---|---|
| P1: Valid form sends correct POST payload | `ComplaintForm.jsx` | fast-check | 100 |
| P2: Form validation rejects incomplete submissions | `ComplaintForm.jsx` | fast-check | 100 |
| P3: Analysis result renders all AI fields | `AnalysisResult.jsx` | fast-check | 100 |
| P4: Complaint creation round-trip | `main.py` + `crud.py` | hypothesis | 100 |
| P5: Invalid payload rejected with 422 | `main.py` | hypothesis | 100 |
| P6: Status update round-trip | `main.py` + `crud.py` | hypothesis | 100 |
| P7: Category detection is always in-vocabulary | `ai_engine.py` | hypothesis | 200 |
| P8: Duplicate detection threshold invariant | `similarity.py` | hypothesis | 200 |
| P9: Sentiment score in valid range | `sentiment_engine.py` | hypothesis | 200 |
| P10: Priority score range and severity consistency | `priority_engine.py` | hypothesis | 200 |
| P11: Recommendation is always non-empty | `recommendation_engine.py` | hypothesis | 200 |
| P12: Dashboard stats consistent with DB | `main.py` | hypothesis | 100 |
| P13: Dashboard analytics accurate | `main.py` | hypothesis | 100 |
| P14: Client-side search returns only matching | `Complaints.jsx` filtering | fast-check | 100 |
| P15: Map endpoint returns complete location data | `main.py` | hypothesis | 100 |
| P16: Marker color mapping is total and correct | `ComplaintMap.jsx` color util | fast-check | 100 |
| P17: AI pipeline enriches all complaints | `main.py` (integration) | hypothesis | 100 |
| P18: AI fault tolerance returns 201 | `main.py` (mocked AI) | hypothesis | 100 |

### Integration Tests

- End-to-end POST → AI pipeline → GET round-trip using a real SQLite test database (1–3 examples).
- Dashboard stats endpoint with a known fixture dataset verifying exact count values.
- Map endpoint with a known fixture verifying location fields are present for all records.

### Smoke Tests

- `GET /health` returns 200 when the server starts.
- SQLite tables exist after `database.py` initialization.
- Sentence Transformers model loads without error on `ai_engine.py` import.
- All 19 frontend source files exist at their specified paths (Requirement 18).
- All 10 backend source files exist at their specified paths (Requirement 18).
