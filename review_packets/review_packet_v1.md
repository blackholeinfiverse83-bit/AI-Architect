# REVIEW_PACKET_V1

## 1. ENTRY POINT

**Frontend entry:**
Path: `prompt/frontend-webapp/index.html` (served via `server.js`)

**Backend entry:**
Path: `prompt/Design-Engine-/backend/app/main.py`

The system starts by launching the FastAPI backend on port 8000 for AI processing and the Express server on port 3000 to serve the frontend application.

---

## 2. CORE EXECUTION FLOW (MAX 4 FILES)

**File 1:**
Path: `prompt/frontend-webapp/app.js`
Manages frontend state, API communication for design generation, and **Recent Designs history retrieval**.

**File 2:**
Path: `prompt/Design-Engine-/backend/app/main.py`
FastAPI gateway directing requests to generation and history routers.

**File 3:**
Path: `prompt/Design-Engine-/backend/app/api/history.py`
Fixed to properly query MongoDB for user-specific design iterations and specs.

**File 4:**
Path: `prompt/Design-Engine-/backend/app/api/generate.py`
Persists new designs to MongoDB and triggers history refresh.

---

## 3. LIVE FLOW (REAL EXECUTION)

**User action (Generation):**
User enters a prompt in the dashboard and clicks "Generate Design".
*Flow:* Frontend (app.js) → POST `/api/v1/generate` → Backend → MongoDB Save → UI Update.

**User action (History):**
User opens the dashboard or clicks "Refresh" on Recent Designs.
*Flow:* Frontend (app.js) → GET `/api/v1/history` → Backend (history.py) → MongoDB Query → UI Grid Render.

---

## 4. WHAT WAS BUILT IN THIS TASK

• **Added:** Recent Designs UI grid with auto-refresh on generation.
• **Modified:** `prompt/Design-Engine-/backend/app/api/history.py` (Fixed broken SQLAlchemy mock logic to use real MongoDB Motor queries).
• **Modified:** `prompt/frontend-webapp/app.js` (Implemented `loadHistory`, `renderHistoryGrid`, and removed all legacy video generation code).
• **Modified:** `prompt/frontend-webapp/index.html` (Added Recent Designs section, removed Video Lab tab).
• **Removed:** Entire Video Generation feature and associated API health checks/UI elements.
• **Not touched:** `prompt/Design-Engine-/backend/app/nlp/*` (NLP processing remains unchanged).

---

## 5. FAILURE CASES

**Case 1:** Backend Service Offline
**Case 2:** LLM Generation Timeout (Model takes >60s)
**Case 3:** Authentication Token Expired

**Behavior:**
The frontend displays a specialized error notification using `showError()` and provides a retry button or redirect to login.

---

## 6. PROOF

**Console logs (System Startup):**
```text
BHIV Design Engine - Startup Script
==========================================

1. Stopping existing processes...
2. Launching Backend (FastAPI)...
3. Launching Frontend (Express)...

Done! 
Backend: http://localhost:8000
Frontend: http://localhost:3000
```
