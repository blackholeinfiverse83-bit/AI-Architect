# 🚀 Video Backend Deployment Guide for Render

Complete guide to deploy the Video Generation Backend to Render.

---

## 📋 Prerequisites

- ✅ GitHub account with repository access
- ✅ Render account (sign up at [render.com](https://render.com))
- ✅ Supabase database (PostgreSQL) or SQLite for development
- ✅ Video backend code pushed to GitHub

---

## 🎯 Step 1: Prepare Your Repository

### 1.1 Ensure Video Backend is in Repository

Make sure your `video/` folder is in your GitHub repository. The structure should be:

```
your-repo/
├── video/
│   ├── app/
│   ├── core/
│   ├── requirements.txt
│   ├── render.yaml
│   └── ...
├── prompt-to-json-main/
├── frontend-webapp/
└── ...
```

### 1.2 Verify render.yaml

The `video/render.yaml` file should exist and be configured. Here's what it should contain:

```yaml
services:
  - type: web
    name: ai-uploader-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.10
      - key: JWT_SECRET_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: BHIV_STORAGE_BACKEND
        value: supabase
      - key: ENVIRONMENT
        value: production
```

---

## 🌐 Step 2: Create Render Web Service

### 2.1 Access Render Dashboard

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### 2.2 Connect Repository

1. Click **"Connect a repository"**
2. Find and select your repository
3. Click **"Connect"**

**If using Blueprint (render.yaml):**
- Select **"Blueprint"** instead of **"Web Service"**
- Render will automatically detect `video/render.yaml`

---

## ⚙️ Step 3: Configure Service Settings

### 3.1 Basic Settings

**Name:**
```
ai-uploader-agent
```
(or your preferred name)

**Region:**
```
Oregon (US West)
```
(Choose closest to your users)

**Branch:**
```
main
```
(or your default branch)

**Root Directory:**
```
video
```
⚠️ **IMPORTANT:** Set this to `video` so Render knows where your video backend code is!

**Runtime:**
```
Python 3
```

### 3.2 Build Settings

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Plan:**
- **Free** (for testing) - Note: Free tier spins down after 15 min inactivity
- **Starter ($7/mo)** - Recommended for production (always-on)

### 3.3 Health Check

**Health Check Path:**
```
/health
```

**Health Check Interval:**
```
30 seconds
```

---

## 🔐 Step 4: Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

### Required Variables

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.10` | Python version |
| `JWT_SECRET_KEY` | `your-secret-key-min-32-chars` | Generate secure key |
| `DATABASE_URL` | `postgresql://...` | From Supabase or PostgreSQL |
| `ENVIRONMENT` | `production` | Environment name |

### Storage Configuration

| Key | Value | Notes |
|-----|-------|-------|
| `BHIV_STORAGE_BACKEND` | `supabase` | Options: `local`, `s3`, `supabase` |
| `BHIV_BUCKET_PATH` | `bucket` | For local storage only |
| `SUPABASE_URL` | `https://[PROJECT].supabase.co` | If using Supabase |
| `SUPABASE_KEY` | `eyJhbGc...` | Supabase anon key |
| `SUPABASE_BUCKET_NAME` | `ai-agent-files` | Supabase bucket name |

### Optional Monitoring

| Key | Value | Notes |
|-----|-------|-------|
| `SENTRY_DSN` | `https://...` | Error tracking (optional) |
| `POSTHOG_API_KEY` | `phc_...` | Analytics (optional) |
| `POSTHOG_HOST` | `https://us.posthog.com` | PostHog host |
| `ENABLE_PERFORMANCE_MONITORING` | `true` | Enable monitoring |
| `ENABLE_USER_ANALYTICS` | `true` | Enable analytics |
| `ENABLE_ERROR_REPORTING` | `true` | Enable error reporting |

### Video Generation Specific

| Key | Value | Notes |
|-----|-------|-------|
| `PERPLEXITY_API_KEY` | `pplx-...` | For AI features (optional) |
| `BHIV_LM_URL` | `https://api.perplexity.ai` | AI service URL |

---

## 🚀 Step 5: Deploy

1. Review all settings
2. Click **"Create Web Service"**
3. Wait 5-10 minutes for first deployment
4. Watch the logs for any errors

---

## ✅ Step 6: Verify Deployment

### 6.1 Check Health

Visit your service URL:
```
https://ai-uploader-agent.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "AI Content Uploader Agent"
}
```

### 6.2 Test API Documentation

Visit:
```
https://ai-uploader-agent.onrender.com/docs
```

You should see the Swagger/OpenAPI documentation.

### 6.3 Test Video Generation

```bash
curl -X POST https://ai-uploader-agent.onrender.com/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Hello world\nThis is a test video",
    "title": "Test Video"
  }'
```

---

## 🔗 Step 7: Update Frontend Configuration

Update your frontend to point to the new video backend URL.

### In `frontend-webapp/app.js`:

```javascript
// Update VIDEO_API_BASE_URL
const VIDEO_API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:9000' 
    : 'https://ai-uploader-agent.onrender.com'; // <-- UPDATE THIS
```

---

## 📝 Step 8: Update Main Backend (Optional)

If your main backend needs to communicate with the video backend, update its configuration:

```python
VIDEO_API_URL = os.getenv("VIDEO_API_URL", "https://ai-uploader-agent.onrender.com")
```

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Solution:**
- Check `requirements.txt` is in `video/` folder
- Verify Python version matches (3.11.10)
- Check build logs for missing dependencies

### Issue: Service Won't Start

**Solution:**
- Verify `startCommand` is correct
- Check that `app/main.py` exists
- Review startup logs for errors
- Ensure `DATABASE_URL` is set correctly

### Issue: Database Connection Fails

**Solution:**
- Verify `DATABASE_URL` is correct
- Check Supabase/PostgreSQL is accessible
- Ensure database tables are created
- Run migrations if needed

### Issue: Video Generation Fails

**Solution:**
- Check `BHIV_STORAGE_BACKEND` is set correctly
- Verify storage credentials (Supabase/S3)
- Check file permissions
- Review error logs

### Issue: Free Tier Spins Down

**Solution:**
- Free tier services spin down after 15 min inactivity
- First request after spin-down takes ~30 seconds
- Upgrade to Starter plan ($7/mo) for always-on

---

## 📊 Monitoring

### View Logs

1. Go to Render Dashboard
2. Select your service
3. Click **"Logs"** tab
4. View real-time logs

### Health Checks

Monitor these endpoints:
- `/health` - Basic health check
- `/health/detailed` - Detailed system status
- `/metrics` - Performance metrics

---

## 🔄 Updating Deployment

### Automatic Updates

Render automatically redeploys when you push to the connected branch.

### Manual Redeploy

1. Go to Render Dashboard
2. Select your service
3. Click **"Manual Deploy"**
4. Select branch/commit
5. Click **"Deploy"**

---

## 💰 Cost Considerations

### Free Tier
- ✅ Free forever
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Cold start takes ~30 seconds
- ✅ Good for development/testing

### Starter Plan ($7/month)
- ✅ Always-on (no spin-down)
- ✅ Faster response times
- ✅ Better for production
- ✅ 512 MB RAM, 0.5 CPU

### Professional Plans
- For high traffic/production
- More resources
- Better performance

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Video Backend README](../README.md)
- [API Documentation](https://ai-uploader-agent.onrender.com/docs)

---

## ✅ Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] Root directory set to `video`
- [ ] Build command configured
- [ ] Start command configured
- [ ] Environment variables added
- [ ] Health check configured
- [ ] Service deployed successfully
- [ ] Health endpoint working
- [ ] API docs accessible
- [ ] Video generation tested
- [ ] Frontend updated with new URL
- [ ] Monitoring configured

---

## 🎉 Success!

Your video backend should now be deployed at:
```
https://ai-uploader-agent.onrender.com
```

Update your frontend to use this URL, and you're all set! 🚀
