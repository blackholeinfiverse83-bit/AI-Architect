# ✅ Complete Deployment Checklist for Video Backend

## 📋 Everything You Need to Do

---

## 1️⃣ Environment Variables for `ai-uploader-agent` Service

Go to Render Dashboard → `ai-uploader-agent` → Environment tab → Add these:

### Required Variables (7)

| Key | Value | Copy From |
|-----|-------|-----------|
| `PYTHON_VERSION` | `3.11.10` | - |
| `JWT_SECRET_KEY` | `SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==` | video/render.yaml |
| `DATABASE_URL` | `postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres` | **Copy from design-engine-api** |
| `BHIV_STORAGE_BACKEND` | `supabase` | ⚠️ Must be `supabase` (not `local`) |
| `SUPABASE_URL` | `https://dusqpdhojbgfxwflukhc.supabase.co` | **Copy from design-engine-api** |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1c3FwZGhvamJnZnh3Zmx1a2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMDcwNTIsImV4cCI6MjA3Mzc4MzA1Mn0.Is0lvgpi1Ijc3jZ8-DQmnrRPqiFfnrQblXzmVKQqY4c` | **Copy from design-engine-api** |
| `SUPABASE_BUCKET_NAME` | `ai-agent-files` | ⚠️ Must match your Supabase bucket |

### Optional but Recommended (8)

| Key | Value |
|-----|-------|
| `ENVIRONMENT` | `production` |
| `JWS_SECRET` | `SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==` |
| `SENTRY_DSN` | `https://0d595f5827bf2a4ae5da7d1ed1a09338@o4509949438328832.ingest.us.sentry.io/4510035576946688` |
| `POSTHOG_API_KEY` | `phc_lmGvuDZ7JiyjDmkL1T6Wy3TvDHgFdjt1zlH02fVziwU` |
| `POSTHOG_HOST` | `https://us.posthog.com` |
| `ENABLE_PERFORMANCE_MONITORING` | `true` |
| `ENABLE_USER_ANALYTICS` | `true` |
| `ENABLE_ERROR_REPORTING` | `true` |

---

## 2️⃣ Supabase Storage Bucket Setup

### Create Storage Bucket in Supabase

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Storage** (left sidebar)
4. Click **"New bucket"**
5. Name: `ai-agent-files`
6. Make it **Public** (for video streaming)
7. Click **"Create bucket"**

### Set Bucket Policies

The bucket needs to allow:
- **Read access** for public (for video streaming)
- **Write access** for authenticated users (for video uploads)

---

## 3️⃣ Update Frontend Video API URL

After video backend is deployed, update `frontend-webapp/app.js`:

1. Get your video backend URL from Render (e.g., `https://ai-uploader-agent-XXXX.onrender.com`)
2. Update line 9 in `frontend-webapp/app.js`:

```javascript
const VIDEO_API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:9000'
    : 'https://ai-uploader-agent-XXXX.onrender.com'; // Your actual Render URL
```

3. Commit and push - Render will auto-redeploy frontend

---

## 4️⃣ Verify Service Configuration

### Check `ai-uploader-agent` Service Settings

In Render Dashboard → `ai-uploader-agent` → Settings:

- ✅ **Root Directory**: `video`
- ✅ **Build Command**: `pip install -r requirements.txt`
- ✅ **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ **Health Check Path**: `/health`

---

## 5️⃣ Test After Deployment

### Test Video Backend Health

```bash
curl https://ai-uploader-agent-XXXX.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "AI Content Uploader Agent"
}
```

### Test Video Generation

```bash
curl -X POST https://ai-uploader-agent-XXXX.onrender.com/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Hello world\nThis is a test",
    "title": "Test Video"
  }'
```

### Test Frontend Connection

1. Open your deployed frontend
2. Go to "Video Lab" tab
3. Check if "Video API" shows "Online" (green dot)
4. Try generating a video

---

## 6️⃣ Common Issues & Fixes

### Issue: Video backend not starting

**Check:**
- All required environment variables are set
- `BHIV_STORAGE_BACKEND=supabase` (not `local`)
- `SUPABASE_BUCKET_NAME` matches your bucket name
- Check Render logs for errors

### Issue: CORS errors on deployed site

**Fix:**
- CORS is already configured in code
- Make sure video backend is running
- Check frontend `VIDEO_API_BASE_URL` is correct

### Issue: Videos not generating

**Check:**
- Supabase bucket exists and is public
- `SUPABASE_KEY` is correct (anon key)
- `SUPABASE_URL` is correct
- Check Render logs for MoviePy errors

### Issue: Database connection fails

**Check:**
- `DATABASE_URL` is correct (copy from `design-engine-api`)
- Database tables exist (auto-created on first run)
- Check Render logs for connection errors

---

## ✅ Final Checklist

### Environment Variables
- [ ] `PYTHON_VERSION` = `3.11.10`
- [ ] `JWT_SECRET_KEY` = (added)
- [ ] `DATABASE_URL` = (copied from design-engine-api)
- [ ] `BHIV_STORAGE_BACKEND` = `supabase`
- [ ] `SUPABASE_URL` = (copied from design-engine-api)
- [ ] `SUPABASE_KEY` = (copied from design-engine-api)
- [ ] `SUPABASE_BUCKET_NAME` = `ai-agent-files`
- [ ] Optional variables added (recommended)

### Supabase Setup
- [ ] Storage bucket `ai-agent-files` created
- [ ] Bucket is set to **Public**
- [ ] Bucket policies allow read/write

### Frontend Update
- [ ] Video backend URL obtained from Render
- [ ] `VIDEO_API_BASE_URL` updated in `app.js`
- [ ] Changes committed and pushed
- [ ] Frontend redeployed

### Testing
- [ ] Video backend health check passes
- [ ] Video generation works
- [ ] Frontend connects to video backend
- [ ] Videos appear in gallery
- [ ] Videos are playable
- [ ] Download button works

---

## 📊 Summary

**Total Steps:**
1. ✅ Add 7 required environment variables
2. ✅ Create Supabase storage bucket
3. ✅ Update frontend video API URL
4. ✅ Test everything

**Time Required:** ~15-20 minutes

**After completion:** Your video generation will work on the deployed site! 🎉
