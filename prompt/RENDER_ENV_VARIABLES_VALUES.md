# 🔑 Render Environment Variables - Actual Values

Here are the **actual API key values** you need to add to your Render backend service:

---

## ✅ Required Environment Variables

### 1. AI Services (For Dashboard Design Generation)

```
GROQ_API_KEY=<your-groq-api-key>
USE_AI_MODEL=true
```

**Optional Fallbacks:**
```
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

---

### 2. 3D Generation Services (For Geometry Preview)

```
MESHY_API_KEY=<your-meshy-api-key>
TRIPO_API_KEY=<your-tripo-api-key>
HUGGINGFACE_API_KEY=<your-huggingface-token>
```

---

## 📋 Complete List with Values

Copy and paste these into Render's Environment Variables section:

### Core Settings:
```
PYTHON_VERSION=3.11.0
PORT=10000
ENVIRONMENT=production
DEBUG=false
```

### Database & Storage:
```
DATABASE_URL=<your-database-url>
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-key>
```

### Authentication:
```
JWT_SECRET_KEY=<your-jwt-secret-at-least-32-chars>
JWT_ALGORITHM=HS256
DEMO_USERNAME=admin
DEMO_PASSWORD=<your-demo-password>
```

### AI Services (NEW - Add These):
```
GROQ_API_KEY=<your-groq-api-key>
USE_AI_MODEL=true
```

### 3D Generation Services (NEW - Add These):
```
MESHY_API_KEY=<your-meshy-api-key>
TRIPO_API_KEY=<your-tripo-api-key>
HUGGINGFACE_API_KEY=<your-huggingface-token>
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
SENTRY_DSN=https://4465443c7756d19300022e0d12f400e2@o4510289261887488.ingest.us.sentry.io/4510322463670272
ENABLE_METRICS=true
DEMO_MODE=false
```

---

## 🎯 Quick Copy-Paste for Render

**Just add these 5 new variables:**

1. `GROQ_API_KEY` = `<your-groq-api-key>`
2. `USE_AI_MODEL` = `true`
3. `MESHY_API_KEY` = `<your-meshy-api-key>`
4. `TRIPO_API_KEY` = `<your-tripo-api-key>`
5. `HUGGINGFACE_API_KEY` = `<your-huggingface-token>`

**Mark all API keys as "Secret" in Render!**

---

## 📝 How to Add in Render

1. Go to: https://dashboard.render.com
2. Click on your **Backend Service**
3. Go to **"Environment"** tab
4. For each variable:
   - Click **"Add Environment Variable"**
   - Enter **Key** (e.g., `GROQ_API_KEY`)
   - Enter **Value** (e.g., your API key from provider)
   - Check **"Secret"** checkbox for API keys
   - Click **"Save Changes"**
5. Service will automatically redeploy

---

## ✅ Verification

After adding variables, check logs for:
- ✅ `"Using Groq AI for design generation"`
- ✅ `"Using Meshy AI for 3D generation"`
- ✅ `"AI generated design"`

---

**That's it!** Add these 5 variables and your deployment will have all the latest features. 🚀
