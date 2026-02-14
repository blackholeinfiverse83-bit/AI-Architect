# main.py
import json
import logging
import os
import uuid
from typing import Optional
import requests
import streamlit as st

logger = logging.getLogger("prompt_runner")

BASE_URL = os.environ.get("PROMPT_TO_JSON_URL", "http://127.0.0.1:8000")
DEFAULT_USERNAME = os.environ.get("PROMPT_TO_JSON_USERNAME", "admin")
DEFAULT_PASSWORD = os.environ.get("PROMPT_TO_JSON_PASSWORD", "bhiv2024")

st.set_page_config(
    page_title="BHIV Design Engine",
    layout="wide",
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# Initialize session state
for key in ["auth_token", "auth_user", "last_spec_id", "last_spec_json", 
            "last_preview_url", "last_cost", "recent_designs", "api_connected"]:
    if key not in st.session_state:
        if key in ["auth_token", "auth_user", "last_spec_id", "last_spec_json", "last_preview_url"]:
            st.session_state[key] = None
        elif key == "last_cost":
            st.session_state[key] = 0
        elif key == "recent_designs":
            st.session_state[key] = []
        else:
            st.session_state[key] = False

def _auth_headers():
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def api_post(path: str, payload: Optional[dict] = None, timeout: int = 30):
    url = f"{BASE_URL}{path}"
    return requests.post(url, json=payload or {}, headers=_auth_headers(), timeout=timeout)

def api_get(path: str, params: Optional[dict] = None, timeout: int = 30):
    url = f"{BASE_URL}{path}"
    return requests.get(url, params=params or {}, headers=_auth_headers(), timeout=timeout)

def check_api_health():
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        st.session_state["api_connected"] = resp.status_code == 200
        return True
    except:
        st.session_state["api_connected"] = False
        return False

def login(username: str, password: str):
    url = f"{BASE_URL}/api/v1/auth/login"
    resp = requests.post(url, data={"username": username, "password": password}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise ValueError("Auth token missing")
    st.session_state["auth_token"] = token
    st.session_state["auth_user"] = username
    return token

def show_response(resp: requests.Response):
    try:
        data = resp.json()
    except:
        data = resp.text
    if resp.status_code >= 400:
        st.error(f"Error {resp.status_code}")
        if isinstance(data, dict):
            st.json(data)
        else:
            st.text(str(data))
    else:
        st.success(f"Success ({resp.status_code})")
        if isinstance(data, dict):
            st.json(data)
        else:
            st.text(str(data))
    return data if isinstance(data, dict) else {}

def display_design_result(data: dict):
    """Display the design generation result in a nice format"""
    st.markdown("---")
    st.subheader("📋 Design Result")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Spec ID:**")
        st.code(data.get("spec_id", "N/A"))
        
        st.markdown("**Preview URL:**")
        preview_url = data.get("preview_url")
        if preview_url:
            st.info(preview_url)
        else:
            st.warning("No preview available")
    
    with col2:
        cost = data.get("estimated_cost", 0)
        st.metric("Estimated Cost", f"₹{cost:,.0f}" if cost else "N/A")
        
        spec_id = data.get("spec_id", "")
        st.metric("Spec ID", spec_id[:12] + "..." if len(spec_id) > 12 else spec_id)
    
    # Show JSON in expander
    with st.expander("View Full Spec JSON"):
        st.json(data.get("spec_json", {}))

# Sidebar
with st.sidebar:
    st.markdown("### 🔐 Authentication")
    username = st.text_input("Username", value=DEFAULT_USERNAME, key="sidebar_user")
    password = st.text_input("Password", value=DEFAULT_PASSWORD, type="password", key="sidebar_pass")
    
    if st.session_state.get("auth_token"):
        st.success(f"✓ Logged in as: {st.session_state.get('auth_user')}")
        if st.button("Logout"):
            st.session_state["auth_token"] = None
            st.session_state["auth_user"] = None
            st.rerun()
    else:
        if st.button("Login", type="primary"):
            try:
                login(username, password)
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

if not st.session_state.get("auth_token"):
    st.warning("Please login to continue")
    st.stop()

check_api_health()

st.title("🏗️ BHIV Design Engine")

# Tabs
tabs = st.tabs([
    "Dashboard", "Generate", "Switch", "Iterate", 
    "Evaluate", "Compliance", "History", "Geometry", "Reports", "RL"
])

# Dashboard Tab
with tabs[0]:
    st.subheader("Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        recent_count = len(st.session_state.get("recent_designs") or [])
        st.metric("Total Designs", recent_count)
    with col2:
        status = "Online" if st.session_state.get("api_connected") else "Offline"
        st.metric("API Status", status)
    with col3:
        spec_id = st.session_state.get("last_spec_id") or ""
        display_id = spec_id[:12] + "..." if spec_id and len(spec_id) > 12 else (spec_id or "None")
        st.metric("Last Spec", display_id)
    with col4:
        cost = st.session_state.get("last_cost") or 0
        st.metric("Est. Cost", f"₹{cost:,.0f}" if cost else "N/A")
    
    st.divider()
    
    # Quick Generate Section
    st.subheader("⚡ Quick Generate")
    
    q_prompt = st.text_area("Describe your design:", placeholder="Design a modern 3-bedroom apartment in Mumbai...", height=80, key="quick_prompt")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        q_city = st.selectbox("City", ["Mumbai", "Pune", "Ahmedabad", "Nashik", "Bangalore"], key="quick_city")
    with col2:
        q_style = st.selectbox("Style", ["Modern", "Traditional", "Contemporary", "Rustic", "Industrial"], key="quick_style")
    with col3:
        q_budget = st.number_input("Budget (INR)", min_value=0, value=0, step=100000, help="0 for auto", key="quick_budget")
    
    if st.button("Generate", type="primary"):
        if q_prompt:
            with st.spinner("Generating design..."):
                try:
                    payload = {
                        "user_id": st.session_state.get("auth_user") or "user",
                        "prompt": q_prompt,
                        "city": q_city,
                        "style": q_style.lower(),
                        "context": {"budget": q_budget} if q_budget > 0 else {},
                    }
                    resp = api_post("/api/v1/generate", payload, timeout=60)
                    data = resp.json() if resp.status_code < 400 else {}
                    
                    if resp.status_code < 400 and data:
                        # Update session state
                        st.session_state["last_spec_id"] = data.get("spec_id", "")
                        st.session_state["last_spec_json"] = data.get("spec_json")
                        st.session_state["last_preview_url"] = data.get("preview_url")
                        st.session_state["last_cost"] = data.get("estimated_cost", 0)
                        
                        # Add to recent
                        st.session_state["recent_designs"].append({
                            "spec_id": data.get("spec_id", ""),
                            "prompt": q_prompt[:50] + "..." if len(q_prompt) > 50 else q_prompt,
                            "city": q_city
                        })
                        
                        st.success(f"Created: {data.get('spec_id')}")
                        display_design_result(data)
                    else:
                        st.error(f"Failed: {resp.status_code}")
                        if data:
                            st.json(data)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Please enter a design description")

# Generate Tab
with tabs[1]:
    st.subheader("✨ Generate New Design")
    
    prompt = st.text_area("Design Description", height=120, placeholder="A modern kitchen with marble island and copper fixtures...", key="gen_prompt")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        city = st.selectbox("City", ["Mumbai", "Pune", "Ahmedabad", "Nashik", "Bangalore"], key="gen_city")
    with col2:
        style = st.selectbox("Style", ["Modern", "Traditional", "Contemporary", "Rustic", "Industrial"], key="gen_style")
    with col3:
        budget = st.number_input("Budget (INR, 0 for auto)", min_value=0, value=0, step=100000, key="gen_budget")
    
    if st.button("Generate Design", type="primary"):
        if prompt and len(prompt) >= 10:
            with st.spinner("Generating..."):
                try:
                    payload = {
                        "user_id": st.session_state.get("auth_user") or "user",
                        "prompt": prompt,
                        "city": city,
                        "style": style.lower(),
                        "context": {"budget": budget} if budget > 0 else {},
                    }
                    resp = api_post("/api/v1/generate", payload, timeout=60)
                    data = resp.json() if resp.status_code < 400 else {}
                    
                    if resp.status_code < 400 and data:
                        st.session_state["last_spec_id"] = data.get("spec_id", "")
                        st.session_state["last_spec_json"] = data.get("spec_json")
                        st.session_state["last_preview_url"] = data.get("preview_url")
                        st.session_state["last_cost"] = data.get("estimated_cost", 0)
                        display_design_result(data)
                    else:
                        st.error(f"Failed: {resp.status_code}")
                        if data:
                            st.json(data)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Please enter at least 10 characters")
    
    # Show last result if exists
    if st.session_state.get("last_spec_json"):
        st.markdown("---")
        st.subheader("Last Generated Design")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Spec ID:** `{st.session_state.get('last_spec_id')}`")
            preview = st.session_state.get("last_preview_url")
            if preview:
                st.info(f"Preview: {preview}")
        with col2:
            cost = st.session_state.get("last_cost", 0)
            st.metric("Cost", f"₹{cost:,.0f}" if cost else "N/A")

# Switch Tab
with tabs[2]:
    st.subheader("🔄 Switch Materials")
    
    col1, col2 = st.columns(2)
    with col1:
        spec_id = st.text_input("Spec ID", value=st.session_state.get("last_spec_id") or "", key="switch_spec_id")
    with col2:
        query = st.text_input("Change Request", placeholder="e.g., change wall to marble", key="switch_query")
    
    if st.button("Apply Switch", type="primary"):
        if spec_id and query:
            with st.spinner("Applying..."):
                try:
                    resp = api_post("/api/v1/switch", {"spec_id": spec_id, "query": query}, timeout=30)
                    show_response(resp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Spec ID and query required")

# Iterate Tab
with tabs[3]:
    st.subheader("📈 Iterate Design")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        spec_id = st.text_input("Spec ID", value=st.session_state.get("last_spec_id") or "", key="iter_spec_id")
    with col2:
        strategy = st.selectbox("Strategy", ["auto_optimize", "improve_materials", "improve_layout", "improve_colors"], key="iter_strategy")
    
    if st.button("Iterate", type="primary"):
        if spec_id:
            with st.spinner("Iterating..."):
                try:
                    payload = {
                        "user_id": st.session_state.get("auth_user") or "user",
                        "spec_id": spec_id,
                        "strategy": strategy,
                    }
                    resp = api_post("/api/v1/iterate", payload, timeout=60)
                    show_response(resp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Spec ID required")

# Evaluate Tab
with tabs[4]:
    st.subheader("⭐ Evaluate Design")
    
    spec_id = st.text_input("Spec ID", value=st.session_state.get("last_spec_id") or "", key="eval_spec_id")
    rating = st.slider("Rating", 1, 5, 3, key="eval_rating")
    st.markdown("Rating: " + "⭐" * rating)
    
    notes = st.text_area("Notes", height=80, key="eval_notes")
    feedback = st.text_area("Feedback", height=80, key="eval_feedback")
    
    if st.button("Submit Evaluation", type="primary"):
        if spec_id:
            with st.spinner("Submitting..."):
                try:
                    payload = {
                        "user_id": st.session_state.get("auth_user") or "user",
                        "spec_id": spec_id,
                        "rating": rating,
                        "notes": notes,
                        "feedback_text": feedback,
                    }
                    resp = api_post("/api/v1/evaluate", payload, timeout=30)
                    show_response(resp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Spec ID required")

# Compliance Tab
with tabs[5]:
    st.subheader("✅ Compliance Check")
    
    col1, col2 = st.columns(2)
    with col1:
        city = st.selectbox("City", ["Mumbai", "Pune", "Ahmedabad", "Nashik"], key="comp_city")
        project_id = st.text_input("Project ID", value="project_001", key="comp_project_id")
    with col2:
        land_use = st.selectbox("Land Use Zone", ["R1", "R2", "R3", "Commercial", "Mixed Use"], key="comp_land_use")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        plot_area = st.number_input("Plot Area (sq.m)", 0.0, 10000.0, 100.0, 10.0, key="comp_plot_area")
        height = st.number_input("Height (m)", 0.0, 200.0, 10.0, 0.5, key="comp_height")
    with col4:
        road_width = st.number_input("Road Width (m)", 0.0, 50.0, 12.0, 0.5, key="comp_road_width")
        setback = st.number_input("Setback (m)", 0.0, 20.0, 3.0, 0.5, key="comp_setback")
    with col5:
        fsi = st.number_input("FSI", 0.0, 10.0, 1.8, 0.1, key="comp_fsi")
        bldg_type = st.selectbox("Building Type", ["Residential", "Commercial", "Mixed Use", "Industrial"], key="comp_bldg_type")
    
    if st.button("Run Compliance", type="primary"):
        with st.spinner("Checking..."):
            try:
                case = {
                    "case_id": f"case_{uuid.uuid4().hex[:8]}",
                    "project_id": project_id,
                    "city": city,
                    "parameters": {
                        "land_use_zone": land_use,
                        "plot_area_sq_m": plot_area,
                        "abutting_road_width_m": road_width,
                        "height_m": height,
                        "setback_m": setback,
                        "fsi": fsi,
                        "building_type": bldg_type,
                    },
                }
                resp = api_post("/api/v1/compliance/run_case", case, timeout=60)
                show_response(resp)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# History Tab
with tabs[6]:
    st.subheader("📜 Design History")
    
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("History Limit", 1, 100, 20, key="hist_limit")
    with col2:
        if st.button("Load History", type="primary"):
            try:
                resp = api_get("/api/v1/history", params={"limit": limit}, timeout=30)
                show_response(resp)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    
    spec_id_hist = st.text_input("Spec ID for Spec History", value=st.session_state.get("last_spec_id") or "", key="hist_spec_id")
    if st.button("Load Spec History"):
        if spec_id_hist:
            try:
                resp = api_get(f"/api/v1/history/{spec_id_hist}", params={"limit": 50}, timeout=30)
                show_response(resp)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Spec ID required")

# Geometry Tab
with tabs[7]:
    st.subheader("📐 Geometry")
    
    if st.button("List Geometry Files"):
        try:
            resp = api_get("/api/v1/geometry/list", timeout=30)
            show_response(resp)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    
    spec_json = st.session_state.get("last_spec_json")
    if not spec_json:
        st.warning("Generate a design first to create geometry")
    else:
        request_id = st.text_input("Request ID", f"req_{uuid.uuid4().hex[:6]}", key="geom_request_id")
        format_opt = st.selectbox("Format", ["glb", "obj", "fbx"], key="geom_format")
        
        if st.button("Generate Geometry", type="primary"):
            with st.spinner("Generating 3D model..."):
                try:
                    payload = {"spec_json": spec_json, "request_id": request_id, "format": format_opt}
                    resp = api_post("/api/v1/geometry/generate", payload, timeout=60)
                    show_response(resp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Reports Tab
with tabs[8]:
    st.subheader("📊 Reports")
    
    report_spec_id = st.text_input("Spec ID", value=st.session_state.get("last_spec_id") or "", key="report_spec_id")
    
    if st.button("Generate Report", type="primary"):
        if report_spec_id:
            with st.spinner("Generating report..."):
                try:
                    resp = api_get(f"/api/v1/reports/{report_spec_id}", timeout=30)
                    show_response(resp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Spec ID required")

# RL Tab
with tabs[9]:
    st.subheader("🤖 RL Training")
    
    st.markdown("**Submit Feedback**")
    
    col1, col2 = st.columns(2)
    with col1:
        spec_id_rl = st.text_input("Spec ID", value=st.session_state.get("last_spec_id") or "", key="rl_spec_id")
    with col2:
        preference = st.selectbox("Preference", [1, -1, 0], format_func=lambda v: "A" if v == 1 else "B" if v == -1 else "Equal", key="rl_preference")
    
    design_a = st.text_input("Design A ID", value=spec_id_rl, key="rl_design_a")
    design_b = st.text_input("Design B ID", value="", key="rl_design_b")
    
    if st.button("Submit Feedback", type="primary"):
        with st.spinner("Submitting..."):
            try:
                payload = {"design_a_id": design_a, "design_b_id": design_b, "preference": preference}
                resp = api_post("/api/v1/rl/feedback", payload, timeout=30)
                show_response(resp)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**RLHF Training**")
        samples = st.number_input("Samples", 10, 1000, 100, key="rlhf_samples")
        if st.button("Train RLHF", type="primary"):
            with st.spinner("Training..."):
                try:
                    resp = api_post("/api/v1/rl/train/rlhf", {"num_samples": samples}, timeout=120)
                    show_response(resp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("**PPO Training**")
        iterations = st.number_input("Iterations", 10, 500, 50, key="ppo_iterations")
        if st.button("Train PPO", type="primary"):
            with st.spinner("Training..."):
                try:
                    resp = api_post("/api/v1/rl/train/opt", {"num_iterations": iterations}, timeout=180)
                    show_response(resp)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
