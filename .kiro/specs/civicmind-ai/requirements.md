# Requirements Document

## Introduction

CivicMind AI is a civic complaint management system that allows citizens to submit complaints, receive AI-driven analysis, and enables administrators to manage, prioritize, and visualize complaint data. The system combines a React-based frontend with a FastAPI backend, SQLite database, and Python AI/ML components to automate category detection, duplicate detection, severity scoring, sentiment analysis, and location-based complaint mapping.

The project is split across seven team responsibilities: Landing Page & Navigation, Complaint Submission Module, Admin Dashboard & Charts, Backend & Database, AI/NLP Engine, Priority & Recommendation Engine, and Maps & Complaint Management.

---

## Glossary

- **System**: The CivicMind AI application as a whole.
- **Frontend**: The React + Vite + Tailwind CSS web client.
- **Backend**: The FastAPI Python server.
- **Database**: The SQLite database managed via SQLAlchemy.
- **AI_Engine**: The Python module responsible for automatic category detection and duplicate detection (`ai_engine.py`, `similarity.py`).
- **Priority_Engine**: The Python module responsible for severity detection, priority score calculation, and sentiment analysis (`priority_engine.py`, `sentiment_engine.py`).
- **Recommendation_Engine**: The Python module that generates actionable recommendations for complaints (`recommendation_engine.py`).
- **Complaint**: A civic complaint record containing at minimum a name, title, description, category, and location.
- **Citizen**: An end user who submits complaints via the Frontend.
- **Administrator**: An authorized user who manages complaints via the Dashboard and Complaint Management pages.
- **Category**: A predefined classification label assigned to a complaint (e.g., Roads, Water, Electricity, Sanitation).
- **Priority_Score**: A numeric score (0–100) representing the urgency and severity of a complaint.
- **Severity_Level**: One of four discrete labels: Low, Medium, High, or Critical.
- **Duplicate**: A complaint whose semantic similarity to an existing complaint exceeds the defined similarity threshold.
- **Similarity_Threshold**: The cosine similarity value above which two complaints are considered duplicates.
- **Sentiment_Score**: A numeric value representing the emotional tone of a complaint description.
- **Recommendation**: A suggested resolution action generated for a complaint based on its category, priority, and sentiment.
- **Stat_Card**: A UI widget displaying a single aggregate metric on the Dashboard.
- **Map**: The interactive Leaflet/OpenStreetMap component displaying complaint markers.

---

## Requirements

### Requirement 1: Landing Page

**User Story:** As a Citizen, I want to view an informative landing page, so that I can understand what CivicMind AI does and how to use it.

#### Acceptance Criteria

1. THE Frontend SHALL render a Hero section that displays the product name, a tagline, and a call-to-action button that navigates to the complaint submission page.
2. THE Frontend SHALL render a Problem/Solution section that describes the civic problem and the system's solution.
3. THE Frontend SHALL render a Features section that lists the key capabilities of the system.
4. THE Frontend SHALL render a How It Works section that describes the complaint submission and resolution process in sequential steps.
5. THE Frontend SHALL render a Footer section that displays copyright information and navigation links.
6. WHILE the viewport width is less than 768px, THE Frontend SHALL display a mobile-responsive layout for all landing page sections.

---

### Requirement 2: Navigation

**User Story:** As a Citizen or Administrator, I want consistent navigation, so that I can move between pages without losing context.

#### Acceptance Criteria

1. THE Frontend SHALL render a Navbar on every page that contains links to: Landing Page, Submit Complaint, Dashboard, Complaints, and Map.
2. WHEN a Citizen clicks a Navbar link, THE Frontend SHALL navigate to the corresponding page without a full page reload.
3. WHILE the viewport width is less than 768px, THE Navbar SHALL display a collapsible mobile menu.
4. THE Navbar SHALL visually highlight the currently active route.

---

### Requirement 3: Complaint Submission Form

**User Story:** As a Citizen, I want to submit a civic complaint through a form, so that my issue is recorded and processed by the system.

#### Acceptance Criteria

1. THE Frontend SHALL render a complaint submission form with the following required fields: Name, Complaint Title, Description, Category (dropdown), Location Name, and Map Location (interactive pin).
2. WHEN a Citizen submits the form with all required fields populated, THE Frontend SHALL send a POST request to `/complaints` with the complaint data.
3. IF a required field is empty when the form is submitted, THEN THE Frontend SHALL display a field-level validation error message and prevent form submission.
4. WHILE the POST request to `/complaints` is in-flight, THE Frontend SHALL display a loading indicator and disable the submit button.
5. WHEN the POST `/complaints` request returns a success response, THE Frontend SHALL navigate the Citizen to the Analysis Result page for that complaint.
6. IF the POST `/complaints` request returns an error response, THEN THE Frontend SHALL display a descriptive error message to the Citizen.

---

### Requirement 4: Complaint Analysis Result Page

**User Story:** As a Citizen, I want to see the AI analysis of my submitted complaint, so that I know it has been processed and understand its priority.

#### Acceptance Criteria

1. WHEN the Analysis Result page is loaded with a valid complaint ID, THE Frontend SHALL display the detected Category, Severity_Level, Priority_Score, Sentiment_Score, and Recommendation for that complaint.
2. WHEN the AI_Engine detects a Duplicate, THE Frontend SHALL display a notice to the Citizen indicating that a similar complaint already exists.
3. THE Frontend SHALL display a success confirmation message on the Analysis Result page after successful submission.

---

### Requirement 5: Backend API — Complaint Endpoints

**User Story:** As the System, I want a RESTful API for complaint management, so that the Frontend and AI components can create, read, and update complaint records.

#### Acceptance Criteria

1. WHEN a POST request is made to `/complaints` with a valid complaint payload, THE Backend SHALL persist the complaint to the Database and return the created complaint record with HTTP 201.
2. IF a POST request to `/complaints` contains an invalid or incomplete payload, THEN THE Backend SHALL return HTTP 422 with a descriptive validation error.
3. WHEN a GET request is made to `/complaints`, THE Backend SHALL return a list of all complaint records from the Database with HTTP 200.
4. WHEN a GET request is made to `/complaints/{id}` with a valid complaint ID, THE Backend SHALL return the matching complaint record with HTTP 200.
5. IF a GET request is made to `/complaints/{id}` with an ID that does not exist in the Database, THEN THE Backend SHALL return HTTP 404.
6. WHEN a PUT request is made to `/complaints/{id}/status` with a valid status value, THE Backend SHALL update the complaint's status in the Database and return the updated record with HTTP 200.
7. IF a PUT request to `/complaints/{id}/status` contains an invalid status value, THEN THE Backend SHALL return HTTP 422 with a descriptive validation error.
8. WHEN a GET request is made to `/health`, THE Backend SHALL return HTTP 200 with a status indicator confirming the service is operational.

---

### Requirement 6: Database & Data Models

**User Story:** As the System, I want a persistent relational data store, so that complaint records and their AI analysis results are reliably stored and retrieved.

#### Acceptance Criteria

1. THE Database SHALL persist each Complaint with at minimum: id, name, title, description, category, location name, latitude, longitude, status, priority score, severity level, sentiment score, recommendation, is_duplicate flag, and created_at timestamp.
2. THE Backend SHALL use SQLAlchemy as the ORM to define and interact with all Database models.
3. WHEN the Backend starts, THE Backend SHALL create all required Database tables if they do not already exist.
4. THE Backend SHALL use Pydantic schemas to validate all request and response payloads for complaint-related endpoints.

---

### Requirement 7: AI/NLP — Category Detection

**User Story:** As the System, I want to automatically detect the category of a submitted complaint, so that complaints are consistently classified without manual input.

#### Acceptance Criteria

1. WHEN a new Complaint is received by the Backend, THE AI_Engine SHALL assign one Category from the predefined set of categories to the Complaint.
2. THE AI_Engine SHALL determine the Category based on semantic analysis of the Complaint's title and description fields.
3. IF the AI_Engine cannot determine a Category with sufficient confidence, THEN THE AI_Engine SHALL assign a default category of "General".
4. THE AI_Engine SHALL return the detected Category to the Backend for persistence with the Complaint record.

---

### Requirement 8: AI/NLP — Duplicate Detection

**User Story:** As the System, I want to detect duplicate complaints, so that administrators are not overwhelmed with redundant entries.

#### Acceptance Criteria

1. WHEN a new Complaint is received by the Backend, THE AI_Engine SHALL compute the cosine similarity between the new Complaint's description embedding and the embeddings of all existing Complaint descriptions using Sentence Transformers.
2. WHEN the cosine similarity between the new Complaint and any existing Complaint exceeds the Similarity_Threshold, THE AI_Engine SHALL mark the new Complaint as a Duplicate and record the ID of the most similar existing Complaint.
3. WHEN a Complaint is marked as a Duplicate, THE Backend SHALL persist the is_duplicate flag as true and the related complaint ID with the Complaint record.
4. THE AI_Engine SHALL use a Sentence Transformers model to generate complaint description embeddings.

---

### Requirement 9: Priority Engine — Severity Detection & Scoring

**User Story:** As the System, I want to automatically calculate the priority of each complaint, so that administrators can focus on the most urgent issues first.

#### Acceptance Criteria

1. WHEN a new Complaint is received by the Backend, THE Priority_Engine SHALL compute a Priority_Score between 0 and 100 for the Complaint based on its category, description content, and Sentiment_Score.
2. THE Priority_Engine SHALL assign a Severity_Level to each Complaint according to the following mapping: Priority_Score 0–24 = Low, 25–49 = Medium, 50–74 = High, 75–100 = Critical.
3. THE Priority_Engine SHALL return the Priority_Score and Severity_Level to the Backend for persistence with the Complaint record.

---

### Requirement 10: Sentiment Analysis

**User Story:** As the System, I want to analyze the sentiment of complaint descriptions, so that the urgency of citizen distress is factored into priority scoring.

#### Acceptance Criteria

1. WHEN a new Complaint is received by the Backend, THE Priority_Engine SHALL compute a Sentiment_Score for the Complaint's description field.
2. THE Priority_Engine SHALL use the Sentiment_Score as an input to the Priority_Score calculation defined in Requirement 9.
3. THE Priority_Engine SHALL return the Sentiment_Score to the Backend for persistence with the Complaint record.

---

### Requirement 11: Recommendation Engine

**User Story:** As an Administrator, I want to receive an AI-generated recommendation for each complaint, so that I have a starting point for resolving the issue.

#### Acceptance Criteria

1. WHEN a new Complaint is processed, THE Recommendation_Engine SHALL generate a Recommendation text based on the Complaint's Category, Severity_Level, and Sentiment_Score.
2. THE Recommendation_Engine SHALL return the Recommendation to the Backend for persistence with the Complaint record.
3. THE Frontend SHALL display the Recommendation on the Analysis Result page and on the Complaint Details page.

---

### Requirement 12: Admin Dashboard — Statistics

**User Story:** As an Administrator, I want to see aggregate complaint statistics at a glance, so that I can quickly assess the current state of civic complaints.

#### Acceptance Criteria

1. WHEN the Dashboard page is loaded, THE Frontend SHALL send a GET request to `/dashboard/stats` and display the returned statistics.
2. THE Frontend SHALL display four Stat_Cards showing: Total Complaints, High Priority Complaints, Duplicate Complaints, and Resolved Complaints.
3. WHEN the GET `/dashboard/stats` request returns an error, THE Frontend SHALL display an error message in place of the Stat_Cards.
4. THE Backend SHALL expose a GET `/dashboard/stats` endpoint that returns counts for total complaints, high-priority complaints (Severity_Level of High or Critical), duplicate complaints, and resolved complaints.

---

### Requirement 13: Admin Dashboard — Charts & Analytics

**User Story:** As an Administrator, I want to see visual charts of complaint data, so that I can identify trends and distributions across categories and priorities.

#### Acceptance Criteria

1. WHEN the Dashboard page is loaded, THE Frontend SHALL send a GET request to `/dashboard/analytics` and render the returned data as charts.
2. THE Frontend SHALL render a Category Distribution chart showing the number of complaints per Category using Chart.js.
3. THE Frontend SHALL render a Priority Distribution chart showing the number of complaints per Severity_Level using Chart.js.
4. THE Frontend SHALL render a Trend chart showing the number of complaints submitted over time using Chart.js.
5. THE Frontend SHALL render a Smart Insights panel that displays AI-generated summary insights derived from the analytics data.
6. THE Backend SHALL expose a GET `/dashboard/analytics` endpoint that returns per-category counts, per-severity-level counts, and complaint counts aggregated by date.

---

### Requirement 14: Complaint Management — List, Search, Filter & Sort

**User Story:** As an Administrator, I want to browse, search, filter, and sort all complaints, so that I can efficiently find and manage specific complaints.

#### Acceptance Criteria

1. WHEN the Complaints page is loaded, THE Frontend SHALL fetch and display a paginated list of all complaints from GET `/complaints`.
2. THE Frontend SHALL provide a text search input that filters displayed complaints by title or description on the client side.
3. THE Frontend SHALL provide a Category filter dropdown that filters displayed complaints to the selected Category.
4. THE Frontend SHALL provide a Severity_Level filter that filters displayed complaints to the selected Severity_Level.
5. THE Frontend SHALL provide column sort controls that sort the displayed complaints by: Date Submitted, Priority_Score, and Severity_Level.
6. WHEN an Administrator clicks a complaint row, THE Frontend SHALL navigate to the Complaint Details page for that complaint.

---

### Requirement 15: Complaint Details & Status Update

**User Story:** As an Administrator, I want to view the full details of a complaint and update its status, so that I can manage the resolution workflow.

#### Acceptance Criteria

1. WHEN the Complaint Details page is loaded with a valid complaint ID, THE Frontend SHALL fetch and display the full complaint record from GET `/complaints/{id}`, including all AI analysis fields.
2. THE Frontend SHALL display the Recommendation on the Complaint Details page.
3. THE Frontend SHALL provide a status update control that allows the Administrator to change the complaint status (e.g., Open, In Progress, Resolved).
4. WHEN an Administrator submits a status change, THE Frontend SHALL send a PUT request to `/complaints/{id}/status` and display the updated status upon success.
5. IF the PUT request to `/complaints/{id}/status` fails, THEN THE Frontend SHALL display an error message without changing the displayed status.

---

### Requirement 16: Interactive Complaint Map

**User Story:** As an Administrator or Citizen, I want to view complaints on an interactive map, so that I can understand the geographic distribution of civic issues.

#### Acceptance Criteria

1. WHEN the Map page is loaded, THE Frontend SHALL fetch complaint location data from GET `/map/complaints` and render a Leaflet/OpenStreetMap map with one marker per complaint.
2. THE Backend SHALL expose a GET `/map/complaints` endpoint that returns the id, title, category, severity level, latitude, and longitude for all complaints.
3. WHEN an Administrator or Citizen clicks a complaint marker on the Map, THE Frontend SHALL display a popup containing the complaint title, Category, and Severity_Level.
4. THE Frontend SHALL color-code map markers by Severity_Level (e.g., green = Low, yellow = Medium, orange = High, red = Critical).
5. THE Frontend SHALL allow the Administrator or Citizen to filter map markers by Category using a filter control on the Map page.
6. WHEN a map location pin is placed during complaint submission on the Complaint Submission Form, THE Frontend SHALL capture the latitude and longitude of the pin and populate the corresponding form fields.

---

### Requirement 17: AI Pipeline Integration on Complaint Submission

**User Story:** As the System, I want all AI processing to run automatically when a complaint is submitted, so that every complaint is enriched with analysis before being returned to the Citizen.

#### Acceptance Criteria

1. WHEN a valid Complaint is persisted to the Database via POST `/complaints`, THE Backend SHALL invoke the AI_Engine for category detection and duplicate detection, THE Priority_Engine for severity detection and sentiment analysis, and THE Recommendation_Engine for recommendation generation — all before returning the response to the caller.
2. THE Backend SHALL persist all AI analysis results (Category, is_duplicate, Priority_Score, Severity_Level, Sentiment_Score, Recommendation) as part of the Complaint record in the Database.
3. IF any AI component raises an unhandled exception during processing, THEN THE Backend SHALL persist the Complaint with default/null values for the affected AI fields and return HTTP 201 with the partial record.

---

### Requirement 18: Project File Structure

**User Story:** As a developer, I want a well-defined file structure, so that each team member knows exactly where to create and find their files.

#### Acceptance Criteria

1. THE System repository SHALL contain a `frontend/` directory with the following source files created (empty or with placeholder content):
   - `frontend/src/pages/LandingPage.jsx`
   - `frontend/src/pages/SubmitComplaint.jsx`
   - `frontend/src/pages/ComplaintResult.jsx`
   - `frontend/src/pages/Dashboard.jsx`
   - `frontend/src/pages/ComplaintMap.jsx`
   - `frontend/src/pages/Complaints.jsx`
   - `frontend/src/pages/ComplaintDetails.jsx`
   - `frontend/src/components/Navbar.jsx`
   - `frontend/src/components/Hero.jsx`
   - `frontend/src/components/Features.jsx`
   - `frontend/src/components/HowItWorks.jsx`
   - `frontend/src/components/Footer.jsx`
   - `frontend/src/components/ComplaintForm.jsx`
   - `frontend/src/components/AnalysisResult.jsx`
   - `frontend/src/components/StatCards.jsx`
   - `frontend/src/components/CategoryChart.jsx`
   - `frontend/src/components/PriorityChart.jsx`
   - `frontend/src/components/TrendChart.jsx`
   - `frontend/src/components/SmartInsights.jsx`

2. THE System repository SHALL contain a `backend/` directory with the following source files created (empty or with placeholder content):
   - `backend/main.py`
   - `backend/database.py`
   - `backend/models.py`
   - `backend/schemas.py`
   - `backend/crud.py`
   - `backend/ai_engine.py`
   - `backend/similarity.py`
   - `backend/priority_engine.py`
   - `backend/recommendation_engine.py`
   - `backend/sentiment_engine.py`
