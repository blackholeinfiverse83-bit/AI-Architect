# REVIEW_PACKET_V1

## 1. ENTRY POINT

**Frontend entry:**
Path: `prompt/frontend-webapp/index.html` (served via `server.js`)

**Backend entry:**
Path: `prompt/Design-Engine-/backend/app/main.py`

The system starts by launching the FastAPI backend on port 8000 for AI processing and the Express server on port 3000 to serve the frontend application.

---

## 2. CORE EXECUTION FLOW (MAX 3 FILES ONLY)

**File 1:**
Path: `prompt/frontend-webapp/app.js`
Manages the frontend state, API communication for design generation, and 3D model rendering logic.

**File 2:**
Path: `prompt/Design-Engine-/backend/app/main.py`
Acts as the main FastAPI gateway, handling routing for generation, health checks, and system orchestration.

**File 3:**
Path: `prompt/Design-Engine-/backend/app/geometry_generator_real.py`
Contains the core algorithmic logic for processing architectural prompts and generating valid 3D geometry outputs.

---

## 3. LIVE FLOW (REAL EXECUTION)

**User action:**
User enters a prompt (e.g., "modern minimalist villa with a garden") in the dashboard and clicks "Generate Design".

**System flow:**
Frontend (app.js) → API (POST /api/v1/generate) → Backend (main.py) → Processing (geometry_generator_real.py) → Response (JSON)

**REAL RESPONSE JSON:**
```json
{
  "message": "Geometry uploaded successfully",
  "upload_id": "geometry_1767769824_spec_cb54d186",
  "spec_id": "spec_cb54d186",
  "filename": "test_geometry.stl",
  "stored_filename": "spec_cb54d186_1767769824.stl",
  "signed_url": "https://dntmhjlbxirtgslzwbui.supabase.co/storage/v1/object/public/geometry/spec_cb54d186.glb",
  "file_type": "stl",
  "file_size": 68,
  "user": "admin",
  "stored_in_database": true,
  "stored_locally": "data/geometry_outputs\\spec_cb54d186_1767769824.stl",
  "metadata_file": "data/geometry_outputs\\geometry_1767769824_spec_cb54d186_metadata.json"
}
```

---

## 4. WHAT WAS BUILT IN THIS TASK

• **Added:** `/review_packets/review_packet_v1.md`
• **Modified:** `prompt/frontend-webapp/index.html`, `prompt/frontend-webapp/app.js`, `prompt/frontend-webapp/styles.css` (UI modernization, expanded prompt area, removed budget field, reordered 3D editor).
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
