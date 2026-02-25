# 🚀 Complete Render Deployment Guide
## Samrachna - AI Design & Architecture

This guide will help you deploy both **Backend** and **Frontend** to Render.

---

## 📋 Prerequisites

- [ ] GitHub account
- [ ] Render account (sign up at [render.com](https://render.com))
- [ ] Code committed and pushed to GitHub
- [ ] Supabase database credentials ready

---

## 🔧 Service 1: Backend API

### Step 1: Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing this project

### Step 2: Configure Backend Service

**Basic Settings:**
- **Name:** `design-engine-api` (or any name you prefer)
- **Region:** `Oregon (US West)` (or closest to you)
- **Branch:** `main` (or your deployment branch)
- **Root Directory:** `prompt-to-json-main/backend` ⚠️ **IMPORTANT: Set this correctly!**
- **Runtime:** `Python 3`
- **Build Command:** `pip install --no-cache-dir -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan:** `Free` (or upgrade to `Starter $7/mo` for always-on)

**Health Check:**
- **Health Check Path:** `/health`

### Step 3: Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

#### Required Core Variables:
```
PYTHON_VERSION=3.11.0
PORT=10000
ENVIRONMENT=production
DEBUG=false
```

#### Database & Storage:
```
DATABASE_URL=postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://dntmhjlbxirtgslzwbui.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwMDc1OTksImV4cCI6MjA3MzU4MzU5OX0.e4ruUJBlI3WaS1RHtP-1844ZZz658MCkVqFMI9FP4GA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODAwNzU5OSwiZXhwIjoyMDczNTgzNTk5fQ.FqU_-DN-bQgQkIVAR_oHtTpPG9YjXRkuh2gPl92oqF4
```

#### Authentication:
```
JWT_SECRET_KEY=bhiv-jwt-secret-2024-super-secure-key-for-production
JWT_ALGORITHM=HS256
DEMO_USERNAME=admin
DEMO_PASSWORD=bhiv2024
```

#### AI Services (Groq, OpenAI, Anthropic):
```
GROQ_API_KEY=your-groq-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
USE_AI_MODEL=true
```

#### 3D Generation Services:
```
MESHY_API_KEY=msy_nH5iA0...
TRIPO_API_KEY=your-tripo-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
```

#### External Services:
```
SOHAM_URL=https://ai-rule-api-w7z5.onrender.com
RANJEET_RL_URL=https://land-utilization-rl.onrender.com
LAND_UTILIZATION_ENABLED=true
LAND_UTILIZATION_MOCK_MODE=false
RANJEET_SERVICE_AVAILABLE=true
```

#### Monitoring & Logging:
```
SENTRY_DSN=your-sentry-dsn-if-using
ENABLE_METRICS=true
DEMO_MODE=false
```

**Note:** Mark sensitive variables (passwords, API keys) as **"Secret"** in Render.

### Step 4: Deploy Backend

1. Review all settings
2. Click **"Create Web Service"**
3. Wait 5-10 minutes for deployment
4. Note your backend URL: `https://design-engine-api-xxxx.onrender.com`

---

## 🎨 Service 2: Frontend Web App

### Step 1: Create New Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect the **same GitHub repository**

### Step 2: Configure Frontend Service

**Basic Settings:**
- **Name:** `samrachna-frontend` (or any name you prefer)
- **Region:** `Oregon (US West)` (same as backend)
- **Branch:** `main` (or your deployment branch)
- **Root Directory:** `frontend-webapp`
- **Runtime:** `Node`
- **Build Command:** `npm install`
- **Start Command:** `npm start`
- **Plan:** `Free` (or upgrade if needed)

### Step 3: Environment Variables

Add these environment variables:

```
NODE_ENV=production
PORT=3000
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

**⚠️ Important:** Replace `your-backend-url.onrender.com` with your actual backend URL from Step 4 above.

### Step 4: Update Frontend API URL

After backend is deployed, you need to update the frontend code:

1. Edit `frontend-webapp/app.js`
2. Find the `API_BASE_URL` constant (around line 5-7)
3. Update it to your backend URL:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```
4. Commit and push the change to trigger a redeploy

### Step 5: Deploy Frontend

1. Review all settings
2. Click **"Create Web Service"**
3. Wait 3-5 minutes for deployment
4. Note your frontend URL: `https://samrachna-frontend-xxxx.onrender.com`

---

## 🔗 Connecting Frontend to Backend

### Option 1: Update Code (Recommended)

1. Get your backend URL from Render dashboard
2. Edit `frontend-webapp/app.js`:
   ```javascript
   const API_BASE_URL = 'https://design-engine-api-xxxx.onrender.com';
   ```
3. Commit and push to trigger redeploy

### Option 2: Use Environment Variable

Update `frontend-webapp/app.js` to use environment variable:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 
    (window.location.hostname === 'localhost' 
        ? 'http://127.0.0.1:8000' 
        : 'https://design-engine-api-xxxx.onrender.com');
```

---

## 📝 Quick Deployment Checklist

### Backend Deployment:
- [ ] Created web service
- [ ] Set root directory: `prompt-to-json-main/backend`
- [ ] Set build command: `pip install --no-cache-dir -r requirements.txt`
- [ ] Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Added all environment variables (see list above)
- [ ] Set health check path: `/health`
- [ ] Service is running and healthy
- [ ] Backend URL noted: `https://design-engine-api-xxxx.onrender.com`

### Frontend Deployment:
- [ ] Created web service
- [ ] Set root directory: `frontend-webapp`
- [ ] Set build command: `npm install`
- [ ] Set start command: `npm start`
- [ ] Added environment variables
- [ ] Updated `API_BASE_URL` in `app.js` to backend URL
- [ ] Committed and pushed changes
- [ ] Service is running
- [ ] Frontend URL noted: `https://samrachna-frontend-xxxx.onrender.com`

---

## 🧪 Testing Deployment

### 1. Test Backend:
```bash
# Health check
curl https://your-backend-url.onrender.com/health

# Should return: {"status":"ok","service":"Design Engine API","version":"0.1.0"}
```

### 2. Test Frontend:
- Visit: `https://your-frontend-url.onrender.com`
- Should show the login page
- Login with: `admin` / `bhiv2024`

### 3. Test Video API:
```bash
curl https://your-backend-url.onrender.com/api/v1/video/health

# Should return: {"status":"ok","service":"Video Generation API"}
```

---

## ⚠️ Important Notes

### Free Tier Limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to **Starter ($7/mo)** for always-on services

### Memory Requirements:
- Backend may need **Standard plan ($25/mo)** for video generation
- Free tier has 512MB RAM limit (may cause OOM errors)
- Video generation is memory-intensive

### CORS Configuration:
- Backend CORS is configured to allow all origins (`*`)
- Should work automatically with frontend
- For production, update CORS in `app/main.py` to specific domains

### Database:
- Using Supabase PostgreSQL (already configured)
- Database URL is in environment variables

### Storage:
- Video files stored in Supabase Storage
- GLB files stored in Supabase Storage
- Set `BHIV_STORAGE_BACKEND=supabase` if needed

---

## 🆘 Troubleshooting

### Backend won't start:
- Check build logs for missing dependencies
- Verify `requirements.txt` is in `prompt-to-json-main/backend/`
- Check Python version matches (3.11.0)
- Verify all environment variables are set

### Frontend can't connect to backend:
- Verify `API_BASE_URL` is correct in `app.js`
- Check backend is running and healthy
- Check CORS settings in backend
- Verify backend URL is accessible

### Out of Memory errors:
- Upgrade to Standard plan ($25/mo)
- Or reduce video generation resolution (already optimized)

### Services keep spinning down:
- Upgrade to Starter plan ($7/mo) for always-on
- Or use a service like UptimeRobot to ping every 5 minutes

---

## 📞 Support

If you encounter issues:
1. Check Render service logs
2. Verify all environment variables are set correctly
3. Test endpoints directly using the backend URL
4. Check that both services are in "Live" status
5. Review the deployment checklist above

---

## 🎉 Success!

Once both services are deployed:
- **Backend:** `https://your-backend-url.onrender.com`
- **Frontend:** `https://your-frontend-url.onrender.com`
- **Login:** `admin` / `bhiv2024`

**Your application is now live! 🚀**
