# Video Backend Environment Variables for Render

## 📋 Required Environment Variables for `ai-uploader-agent`

You need to add these environment variables in the Render Dashboard for the **`ai-uploader-agent`** service (NOT `design-engine-api`).

---

## 🔴 Required Variables (Must Add)

| Key | Value | Where to Get |
|-----|-------|--------------|
| `JWT_SECRET_KEY` | `your-secret-key-min-32-chars` | Generate secure random string (min 32 chars) |
| `DATABASE_URL` | `postgresql://...` | Same as `design-engine-api` (from Supabase) |
| `BHIV_STORAGE_BACKEND` | `supabase` | Set to `supabase` for production |
| `SUPABASE_URL` | `https://[PROJECT].supabase.co` | Same as `design-engine-api` |
| `SUPABASE_KEY` | `eyJhbGc...` | Same as `design-engine-api` (Supabase anon key) |
| `SUPABASE_BUCKET_NAME` | `ai-agent-files` | Your Supabase storage bucket name |

---

## 🟡 Optional Variables (Recommended)

| Key | Value | Notes |
|-----|-------|-------|
| `ENVIRONMENT` | `production` | Environment name |
| `SENTRY_DSN` | `https://...` | Error tracking (optional) |
| `POSTHOG_API_KEY` | `phc_...` | Analytics (optional) |
| `POSTHOG_HOST` | `https://us.posthog.com` | PostHog host |
| `ENABLE_PERFORMANCE_MONITORING` | `true` | Enable monitoring |
| `ENABLE_USER_ANALYTICS` | `true` | Enable analytics |
| `ENABLE_ERROR_REPORTING` | `true` | Enable error reporting |
| `PYTHON_VERSION` | `3.11.10` | Python version |

---

## 📝 How to Add in Render Dashboard

### Step 1: Go to Video Backend Service
1. Open [Render Dashboard](https://dashboard.render.com)
2. Click on **`ai-uploader-agent`** service (NOT `design-engine-api`)
3. Click **"Environment"** tab in the left sidebar

### Step 2: Add Each Variable
1. Click **"Add Environment Variable"** button
2. For each variable:
   - **Key**: Enter the variable name (e.g., `JWT_SECRET_KEY`)
   - **Value**: Enter the value
   - Click **"Save"**

### Step 3: Copy from Main Backend (if same)
You can copy these values from `design-engine-api`:
- `DATABASE_URL` - Same PostgreSQL connection
- `SUPABASE_URL` - Same Supabase project
- `SUPABASE_KEY` - Same Supabase anon key
- `JWT_SECRET_KEY` - Can be same or different (recommend different for security)

---

## 🔑 Quick Copy Checklist

From your `design-engine-api` service, you can reuse:

✅ **Copy these values:**
- `DATABASE_URL` → Use same value
- `SUPABASE_URL` → Use same value  
- `SUPABASE_KEY` → Use same value
- `JWT_SECRET_KEY` → Can use same or generate new one

✅ **Add new values:**
- `BHIV_STORAGE_BACKEND` → Set to `supabase`
- `SUPABASE_BUCKET_NAME` → Your bucket name (e.g., `ai-agent-files`)

---

## 🚨 Important Notes

1. **Different Service**: Make sure you're adding variables to `ai-uploader-agent`, NOT `design-engine-api`
2. **Storage Backend**: Must be `supabase` for production (not `local`)
3. **Bucket Name**: Must match your Supabase storage bucket name
4. **JWT Secret**: Can be same as main backend or different (both work)

---

## ✅ After Adding Variables

1. Render will automatically redeploy the service
2. Check the logs to ensure it starts successfully
3. Test the health endpoint: `https://ai-uploader-agent-XXXX.onrender.com/health`
4. Update frontend `VIDEO_API_BASE_URL` if needed

---

## 📊 Summary

**Minimum Required:**
- `JWT_SECRET_KEY`
- `DATABASE_URL` (copy from main backend)
- `BHIV_STORAGE_BACKEND=supabase`
- `SUPABASE_URL` (copy from main backend)
- `SUPABASE_KEY` (copy from main backend)
- `SUPABASE_BUCKET_NAME` (your bucket name)

**Total: 6 required variables**
