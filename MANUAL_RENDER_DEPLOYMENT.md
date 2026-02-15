# Manual Render Deployment Guide
## Samrachna - AI Design & Architecture

This guide will help you deploy the unified backend and frontend to Render **without using render.yaml**.

---

## 📋 Services to Deploy

You need to deploy **2 services**:

1. **Backend API** (Unified - includes Design Engine + Video Generation)
2. **Frontend Web App**

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
- **Region:** `Oregon` (or closest to you)
- **Branch:** `main` (or your deployment branch)
- **Root Directory:** `prompt-to-json-main/backend`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan:** `Free` (or upgrade if needed)

**Health Check:**
- **Health Check Path:** `/health`

### Step 3: Environment Variables

Add these environment variables in the Render dashboard:

#### Required Variables:
```
PYTHON_VERSION=3.11.0
PORT=10000
```

#### Database & Storage:
```
DATABASE_URL=<your-postgresql-connection-string>
# OR use Supabase:
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-key>
```

#### Authentication:
```
JWT_SECRET_KEY=<generate-a-random-secret-key>
DEMO_USERNAME=admin
DEMO_PASSWORD=<your-secure-password>
```

#### Optional AI Services:
```
OPENAI_API_KEY=<your-openai-key-if-using-ai>
ANTHROPIC_API_KEY=<your-anthropic-key-if-using-ai>
USE_AI_MODEL=false
```

#### External Services:
```
SOHAM_URL=https://ai-rule-api-w7z5.onrender.com
RANJEET_RL_URL=https://land-utilization-rl.onrender.com
LAND_UTILIZATION_ENABLED=true
LAND_UTILIZATION_MOCK_MODE=false
RANJEET_SERVICE_AVAILABLE=true
```

#### Configuration:
```
DEBUG=false
ENVIRONMENT=production
```

**Note:** Mark sensitive variables (like passwords, API keys) as **"Secret"** in Render.

---

## 🎨 Service 2: Frontend Web App

### Step 1: Create New Web Service
1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect the **same GitHub repository**

### Step 2: Configure Frontend Service

**Basic Settings:**
- **Name:** `samrachna-frontend` (or any name you prefer)
- **Region:** `Oregon` (or same as backend)
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
```

**Important:** After backend is deployed, update the frontend's `app.js` file to use the backend URL:
- Change `API_BASE_URL` to your backend's Render URL (e.g., `https://design-engine-api-xxxx.onrender.com`)

---

## 🔗 Connecting Frontend to Backend

After both services are deployed:

1. **Get your backend URL** from Render dashboard (e.g., `https://design-engine-api-xxxx.onrender.com`)

2. **Update frontend code:**
   - Edit `frontend-webapp/app.js`
   - Find the `API_BASE_URL` constant
   - Update it to your backend URL:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```

3. **Commit and push** the change to trigger a redeploy

---

## 📝 Quick Checklist

### Backend Deployment:
- [ ] Created web service
- [ ] Set root directory: `prompt-to-json-main/backend`
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Added all environment variables
- [ ] Set health check path: `/health`
- [ ] Service is running and healthy

### Frontend Deployment:
- [ ] Created web service
- [ ] Set root directory: `frontend-webapp`
- [ ] Set build command: `npm install`
- [ ] Set start command: `npm start`
- [ ] Added environment variables
- [ ] Updated `API_BASE_URL` in `app.js` to backend URL
- [ ] Service is running

---

## 🧪 Testing Deployment

1. **Test Backend:**
   - Visit: `https://your-backend-url.onrender.com/health`
   - Should return: `{"status": "ok"}`

2. **Test Frontend:**
   - Visit: `https://your-frontend-url.onrender.com`
   - Should show the login page

3. **Test Video API:**
   - Visit: `https://your-backend-url.onrender.com/api/v1/video/health`
   - Should return: `{"status": "ok", "service": "Video Generation API"}`

---

## ⚠️ Important Notes

1. **Free Tier Limitations:**
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down may take 30-60 seconds
   - Consider upgrading to paid plan for always-on services

2. **Database:**
   - You can use Render's PostgreSQL (free tier available)
   - Or use Supabase (recommended for this project)

3. **Storage:**
   - Video files are stored locally in `bucket/videos/`
   - For production, consider using Supabase Storage or AWS S3
   - Set `BHIV_STORAGE_BACKEND=supabase` in environment variables

4. **CORS:**
   - Backend CORS is configured to allow all origins
   - Should work automatically with frontend

---

## 🆘 Troubleshooting

**Backend won't start:**
- Check build logs for missing dependencies
- Verify `requirements.txt` is in `prompt-to-json-main/backend/`
- Check Python version matches (3.11.0)

**Frontend can't connect to backend:**
- Verify `API_BASE_URL` is correct in `app.js`
- Check backend is running and healthy
- Check CORS settings in backend

**Videos not generating:**
- Check MoviePy dependencies are installed
- Verify `bucket/videos/` directory is writable
- Check backend logs for errors

---

## 📞 Support

If you encounter issues:
1. Check Render service logs
2. Verify all environment variables are set
3. Test endpoints directly using the backend URL
4. Check that both services are in "Live" status

---

**Good luck with your deployment! 🚀**
