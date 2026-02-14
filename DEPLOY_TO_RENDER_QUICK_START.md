# 🚀 Quick Start: Deploy All Services to Render

This guide will help you deploy all three services (Main Backend, Video Backend, and Frontend) to Render in one go.

---

## 📋 Prerequisites

- ✅ GitHub account
- ✅ Render account ([sign up here](https://render.com))
- ✅ Code pushed to GitHub repository
- ✅ Supabase database credentials ready

---

## 🎯 Method 1: Using Blueprint (Recommended - Easiest)

### Step 1: Push Code to GitHub

Make sure your `render.yaml` file is in the root of your repository:

```bash
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Deploy via Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Review the services it will create:
   - `design-engine-api` (Main Backend)
   - `ai-uploader-agent` (Video Backend)
   - `bhiv-design-engine-frontend` (Frontend)
6. Click **"Apply"**

### Step 3: Configure Environment Variables

For each service, you'll need to add environment variables:

#### Main Backend (`design-engine-api`)
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `SUPABASE_SERVICE_KEY` - Supabase service key
- `JWT_SECRET_KEY` - Secure JWT secret (min 32 chars)
- `DEMO_PASSWORD` - Demo user password
- `OPENAI_API_KEY` - OpenAI API key (if using)

#### Video Backend (`ai-uploader-agent`)
- `JWT_SECRET_KEY` - Same as main backend or different
- `DATABASE_URL` - PostgreSQL connection string (can be same as main backend)
- `BHIV_STORAGE_BACKEND` - Set to `supabase` for production
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `SUPABASE_BUCKET_NAME` - Supabase storage bucket name (e.g., `ai-agent-files`)
- `SENTRY_DSN` - (Optional) Sentry error tracking
- `POSTHOG_API_KEY` - (Optional) PostHog analytics

#### Frontend (`bhiv-design-engine-frontend`)
- No environment variables needed (or minimal)

### Step 4: Update Frontend URLs

After deployment, update `frontend-webapp/app.js`:

```javascript
// Update these URLs with your Render service URLs
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000'
    : 'https://design-engine-api-XXXX.onrender.com'; // Your main backend URL

const VIDEO_API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:9000'
    : 'https://ai-uploader-agent-XXXX.onrender.com'; // Your video backend URL
```

Then push the changes:
```bash
git add frontend-webapp/app.js
git commit -m "Update API URLs for Render deployment"
git push origin main
```

Render will automatically redeploy the frontend.

---

## 🔧 Method 2: Manual Deployment (Step by Step)

### Step 1: Deploy Main Backend

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect repository
4. Configure:
   - **Name**: `design-engine-api`
   - **Root Directory**: `prompt-to-json-main`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
5. Add environment variables (see Method 1, Step 3)
6. Click **"Create Web Service"**

### Step 2: Deploy Video Backend

1. Click **"New +"** → **"Web Service"**
2. Connect same repository
3. Configure:
   - **Name**: `ai-uploader-agent`
   - **Root Directory**: `video` ⚠️ **IMPORTANT!**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Add environment variables (see Method 1, Step 3)
5. Click **"Create Web Service"**

### Step 3: Deploy Frontend

1. Click **"New +"** → **"Web Service"**
2. Connect same repository
3. Configure:
   - **Name**: `bhiv-design-engine-frontend`
   - **Root Directory**: `frontend-webapp`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Health Check Path**: `/`
4. Add environment variables:
   - `NODE_ENV`: `production`
   - `PORT`: `3000`
5. Click **"Create Web Service"**

### Step 4: Update Frontend URLs

Same as Method 1, Step 4.

---

## ✅ Verification

After deployment, verify each service:

### Main Backend
```bash
curl https://design-engine-api-XXXX.onrender.com/health
```

### Video Backend
```bash
curl https://ai-uploader-agent-XXXX.onrender.com/health
```

### Frontend
Visit: `https://bhiv-design-engine-frontend-XXXX.onrender.com`

---

## 🔄 Updating Services

### Automatic Updates
Render automatically redeploys when you push to the connected branch.

### Manual Redeploy
1. Go to Render Dashboard
2. Select service
3. Click **"Manual Deploy"**
4. Select branch/commit
5. Click **"Deploy"**

---

## 🐛 Common Issues

### Issue: Video Backend Build Fails

**Solution:**
- Verify `rootDir` is set to `video`
- Check `requirements.txt` exists in `video/` folder
- Review build logs for missing dependencies

### Issue: Services Can't Connect

**Solution:**
- Verify all URLs are updated in frontend
- Check CORS settings in backends
- Ensure services are deployed and running

### Issue: Database Connection Fails

**Solution:**
- Verify `DATABASE_URL` is correct
- Check Supabase connection settings
- Ensure database is accessible from Render

### Issue: Video Generation Fails

**Solution:**
- Set `BHIV_STORAGE_BACKEND=supabase` (not `local`)
- Verify Supabase storage bucket exists
- Check Supabase credentials

---

## 📊 Service URLs

After deployment, you'll get URLs like:
- Main Backend: `https://design-engine-api-XXXX.onrender.com`
- Video Backend: `https://ai-uploader-agent-XXXX.onrender.com`
- Frontend: `https://bhiv-design-engine-frontend-XXXX.onrender.com`

Replace `XXXX` with your actual service ID.

---

## 💰 Cost

### Free Tier
- ✅ All three services can run on free tier
- ⚠️ Services spin down after 15 min inactivity
- ⚠️ Cold start takes ~30 seconds
- ✅ Good for development/testing

### Starter Plan ($7/month per service)
- ✅ Always-on (no spin-down)
- ✅ Faster response times
- ✅ Better for production
- 💰 Total: $21/month for all three services

---

## 📚 Additional Resources

- [Video Backend Deployment Guide](video/RENDER_DEPLOYMENT_GUIDE.md)
- [Main Backend Deployment Guide](prompt-to-json-main/RENDER_DEPLOYMENT_GUIDE.md)
- [Render Documentation](https://render.com/docs)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] All three services deployed
- [ ] Environment variables configured
- [ ] Health checks passing
- [ ] Frontend URLs updated
- [ ] Services tested and working
- [ ] Monitoring configured (optional)

---

## 🎉 Success!

Your complete application should now be deployed:
- ✅ Main Backend API
- ✅ Video Generation Backend
- ✅ Frontend Web App

All services are live and connected! 🚀
