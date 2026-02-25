# 🔧 Render Environment Variables - Update List

Since you already have the project deployed, here are the **NEW or UPDATED** environment variables you need to add/update in your Render backend service:

---

## ✅ Required Environment Variables to ADD/UPDATE

### 1. AI Services (For Dashboard Design Generation)

**Add these if not already present:**

```
GROQ_API_KEY=your-groq-api-key-here
USE_AI_MODEL=true
```

**Optional (if you want fallbacks):**
```
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Why:** 
- `GROQ_API_KEY` - Enables fast AI design generation (primary LLM)
- `USE_AI_MODEL=true` - Enables AI models instead of templates
- OpenAI/Anthropic are fallbacks if Groq fails

---

### 2. 3D Generation Services (For Geometry Preview)

**Add these for 3D GLB generation:**

```
MESHY_API_KEY=msy_nH5iA0...
TRIPO_API_KEY=your-tripo-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
```

**Why:**
- `MESHY_API_KEY` - **PRIORITY** for realistic 3D model generation
- `TRIPO_API_KEY` - Fallback if Meshy fails
- `HUGGINGFACE_API_KEY` - Free fallback option

**Priority Order:**
1. Meshy AI (if `MESHY_API_KEY` is set)
2. Tripo AI (if Meshy fails and `TRIPO_API_KEY` is set)
3. HuggingFace (if both fail and `HUGGINGFACE_API_KEY` is set)
4. Local generator (if all fail)

---

## 📋 Complete Environment Variables List

Here's the **complete list** of all environment variables you should have in Render:

### Core Settings:
```
PYTHON_VERSION=3.11.0
PORT=10000
ENVIRONMENT=production
DEBUG=false
```

### Database & Storage:
```
DATABASE_URL=postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://dntmhjlbxirtgslzwbui.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwMDc1OTksImV4cCI6MjA3MzU4MzU5OX0.e4ruUJBlI3WaS1RHtP-1844ZZz658MCkVqFMI9FP4GA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODAwNzU5OSwiZXhwIjoyMDczNTgzNTk5fQ.FqU_-DN-bQgQkIVAR_oHtTpPG9YjXRkuh2gPl92oqF4
```

### Authentication:
```
JWT_SECRET_KEY=bhiv-jwt-secret-2024-super-secure-key-for-production
JWT_ALGORITHM=HS256
DEMO_USERNAME=admin
DEMO_PASSWORD=bhiv2024
```

### AI Services (NEW/UPDATE):
```
GROQ_API_KEY=your-groq-api-key-here
USE_AI_MODEL=true
OPENAI_API_KEY=your-openai-api-key-here (optional)
ANTHROPIC_API_KEY=your-anthropic-api-key-here (optional)
```

### 3D Generation Services (NEW/UPDATE):
```
MESHY_API_KEY=msy_nH5iA0...
TRIPO_API_KEY=your-tripo-api-key-here (optional)
HUGGINGFACE_API_KEY=your-huggingface-api-key-here (optional)
```

### External Services:
```
SOHAM_URL=https://ai-rule-api-w7z5.onrender.com
RANJEET_RL_URL=https://land-utilization-rl.onrender.com
LAND_UTILIZATION_ENABLED=true
LAND_UTILIZATION_MOCK_MODE=false
RANJEET_SERVICE_AVAILABLE=true
```

### Monitoring:
```
SENTRY_DSN=your-sentry-dsn-if-using (optional)
ENABLE_METRICS=true
DEMO_MODE=false
```

---

## 🎯 Quick Action Items

### Must Add (Required for current features):
1. ✅ `GROQ_API_KEY` - For AI design generation
2. ✅ `USE_AI_MODEL=true` - Enable AI models
3. ✅ `MESHY_API_KEY` - For 3D GLB generation (priority)

### Should Add (Recommended):
4. ✅ `TRIPO_API_KEY` - Fallback for 3D generation
5. ✅ `HUGGINGFACE_API_KEY` - Free fallback for 3D

### Optional (Nice to have):
6. ⚪ `OPENAI_API_KEY` - Fallback for design generation
7. ⚪ `ANTHROPIC_API_KEY` - Fallback for design generation

---

## 📝 How to Update in Render

1. Go to your Render Dashboard: https://dashboard.render.com
2. Click on your **Backend Service** (e.g., `design-engine-api`)
3. Go to **"Environment"** tab
4. Click **"Add Environment Variable"** for each new variable
5. Enter the **Key** and **Value**
6. Mark sensitive keys (API keys) as **"Secret"**
7. Click **"Save Changes"**
8. Service will automatically redeploy

---

## ⚠️ Important Notes

- **MESHY_API_KEY** is the most important for 3D generation - it's prioritized
- **GROQ_API_KEY** is required for AI design generation in Dashboard
- **USE_AI_MODEL=true** must be set to enable AI features
- All API keys should be marked as **"Secret"** in Render
- After adding variables, wait for automatic redeploy (2-3 minutes)

---

## ✅ Verification

After updating environment variables, test:

1. **Backend Health:**
   ```
   https://your-backend-url.onrender.com/health
   ```

2. **Generate Design (Dashboard):**
   - Should use Groq AI if `GROQ_API_KEY` is set
   - Should use Meshy AI for 3D if `MESHY_API_KEY` is set

3. **Check Logs:**
   - Look for: "Using Groq AI for design generation"
   - Look for: "Using Meshy AI for 3D generation"

---

**That's it!** Just add/update these environment variables in Render and your deployment will have all the latest features. 🚀
