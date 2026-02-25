# Environment Variables Guide

## 📋 Overview

This guide explains which environment variables you need to add for **local development** and **Render deployment**.

---

## 🏠 Local Development

### For Video Backend (Port 9000)

**Minimum Required (works with defaults):**
- None! The video backend will work with default SQLite database and local storage.

**Recommended (for better functionality):**
Create `video/.env` file with:

```env
# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./data.db

# JWT Secret (optional - will generate if missing)
JWT_SECRET_KEY=your-secret-key-min-32-chars

# Storage (optional - defaults to local)
BHIV_STORAGE_BACKEND=local
BHIV_BUCKET_PATH=bucket

# Environment
ENVIRONMENT=development
```

**✅ You can run locally WITHOUT any environment variables!**

---

## ☁️ Render Deployment

### For Video Backend (`ai-uploader-agent`)

You **MUST** add these environment variables in Render Dashboard:

#### 🔴 Required Variables

| Key | Value | Where to Get |
|-----|-------|--------------|
| `JWT_SECRET_KEY` | `your-secret-key-min-32-chars` | Generate a secure random string (min 32 characters) |
| `DATABASE_URL` | `postgresql://...` | From your Supabase project settings |
| `BHIV_STORAGE_BACKEND` | `supabase` | Set to `supabase` for production |
| `SUPABASE_URL` | `https://[PROJECT].supabase.co` | From Supabase project settings |
| `SUPABASE_KEY` | `eyJhbGc...` | Supabase anon key from project settings |
| `SUPABASE_BUCKET_NAME` | `ai-agent-files` | Your Supabase storage bucket name |

#### 🟡 Optional (but recommended)

| Key | Value | Notes |
|-----|-------|-------|
| `SENTRY_DSN` | `https://...` | Error tracking (optional) |
| `POSTHOG_API_KEY` | `phc_...` | Analytics (optional) |
| `POSTHOG_HOST` | `https://us.posthog.com` | PostHog host |
| `ENABLE_PERFORMANCE_MONITORING` | `true` | Enable monitoring |
| `ENABLE_USER_ANALYTICS` | `true` | Enable analytics |
| `ENABLE_ERROR_REPORTING` | `true` | Enable error reporting |

---

## 📝 How to Add Environment Variables in Render

### Step 1: Go to Your Service
1. Open [Render Dashboard](https://dashboard.render.com)
2. Click on `ai-uploader-agent` service

### Step 2: Add Environment Variables
1. Click **"Environment"** tab (left sidebar)
2. Click **"Add Environment Variable"**
3. Enter each variable:
   - **Key**: `JWT_SECRET_KEY`
   - **Value**: Your secret key
   - Click **"Save"**
4. Repeat for all required variables

### Step 3: Redeploy
After adding variables, Render will automatically redeploy, or you can click **"Manual Deploy"**.

---

## 🔑 Generating JWT Secret Key

You can generate a secure JWT secret key using:

**Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Online:**
- Use any secure random string generator
- Minimum 32 characters
- Example: `SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==`

---

## ✅ Quick Checklist

### Local Development
- [ ] No environment variables needed (works with defaults)
- [ ] Optional: Create `video/.env` for custom config

### Render Deployment
- [ ] `JWT_SECRET_KEY` - Required
- [ ] `DATABASE_URL` - Required (Supabase PostgreSQL)
- [ ] `BHIV_STORAGE_BACKEND=supabase` - Required
- [ ] `SUPABASE_URL` - Required
- [ ] `SUPABASE_KEY` - Required
- [ ] `SUPABASE_BUCKET_NAME` - Required
- [ ] Optional monitoring variables

---

## 🚨 Important Notes

1. **Never commit `.env` files to Git** - They contain secrets!
2. **Use `sync: false` in render.yaml** - This means you must manually add the value in Render Dashboard
3. **For production, use Supabase storage** - Set `BHIV_STORAGE_BACKEND=supabase`
4. **Local development uses SQLite** - No database setup needed locally

---

## 🔍 Where to Find Supabase Credentials

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Settings** → **API**
4. Find:
   - **Project URL** → Use for `SUPABASE_URL`
   - **anon public key** → Use for `SUPABASE_KEY`
5. Go to **Storage** → Create bucket → Use name for `SUPABASE_BUCKET_NAME`
6. Go to **Settings** → **Database** → **Connection string** → Use for `DATABASE_URL`

---

## 📚 Summary

- **Local**: No environment variables needed! ✅
- **Render**: Add 6 required variables in Render Dashboard ⚠️
