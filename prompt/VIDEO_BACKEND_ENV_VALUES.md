# Video Backend Environment Variables - Complete List with Values

## 📋 Add These to `ai-uploader-agent` Service in Render

Copy and paste these exact values into Render Dashboard → `ai-uploader-agent` → Environment tab.

---

## 🔴 Required Variables (6)

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.10` |
| `JWT_SECRET_KEY` | `SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==` |
| `DATABASE_URL` | `postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres` |
| `BHIV_STORAGE_BACKEND` | `supabase` |
| `SUPABASE_URL` | `https://dusqpdhojbgfxwflukhc.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1c3FwZGhvamJnZnh3Zmx1a2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMDcwNTIsImV4cCI6MjA3Mzc4MzA1Mn0.Is0lvgpi1Ijc3jZ8-DQmnrRPqiFfnrQblXzmVKQqY4c` |
| `SUPABASE_BUCKET_NAME` | `ai-agent-files` |

---

## 🟡 Optional but Recommended Variables

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

## 📝 Quick Copy-Paste Format

### Required (Copy these exactly):

```
PYTHON_VERSION=3.11.10
JWT_SECRET_KEY=SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==
DATABASE_URL=postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
BHIV_STORAGE_BACKEND=supabase
SUPABASE_URL=https://dusqpdhojbgfxwflukhc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1c3FwZGhvamJnZnh3Zmx1a2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMDcwNTIsImV4cCI6MjA3Mzc4MzA1Mn0.Is0lvgpi1Ijc3jZ8-DQmnrRPqiFfnrQblXzmVKQqY4c
SUPABASE_BUCKET_NAME=ai-agent-files
```

### Optional (Recommended):

```
ENVIRONMENT=production
JWS_SECRET=SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==
SENTRY_DSN=https://0d595f5827bf2a4ae5da7d1ed1a09338@o4509949438328832.ingest.us.sentry.io/4510035576946688
POSTHOG_API_KEY=phc_lmGvuDZ7JiyjDmkL1T6Wy3TvDHgFdjt1zlH02fVziwU
POSTHOG_HOST=https://us.posthog.com
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USER_ANALYTICS=true
ENABLE_ERROR_REPORTING=true
```

---

## ⚠️ Important Notes

1. **BHIV_STORAGE_BACKEND**: Changed from `local` to `supabase` for production
2. **SUPABASE_BUCKET_NAME**: Make sure this bucket exists in your Supabase project
3. **All values are from your existing configuration files**
4. **Copy values exactly as shown** (including special characters)

---

## ✅ Step-by-Step in Render

1. Go to Render Dashboard
2. Click on **`ai-uploader-agent`** service
3. Click **"Environment"** tab
4. Click **"Add Environment Variable"** for each one
5. Copy Key and Value from the table above
6. Click **"Save"**
7. Render will auto-redeploy

---

## 🎯 Minimum Required (6 variables)

If you only want the essentials:

1. `PYTHON_VERSION` = `3.11.10`
2. `JWT_SECRET_KEY` = `SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==`
3. `DATABASE_URL` = `postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres`
4. `BHIV_STORAGE_BACKEND` = `supabase`
5. `SUPABASE_URL` = `https://dusqpdhojbgfxwflukhc.supabase.co`
6. `SUPABASE_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1c3FwZGhvamJnZnh3Zmx1a2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMDcwNTIsImV4cCI6MjA3Mzc4MzA1Mn0.Is0lvgpi1Ijc3jZ8-DQmnrRPqiFfnrQblXzmVKQqY4c`
7. `SUPABASE_BUCKET_NAME` = `ai-agent-files`

---

## 📊 Summary

- **Total Required**: 7 variables (including PYTHON_VERSION)
- **Total Optional**: 8 variables
- **All values found in**: `video/render.yaml` and `video/setup_correct_supabase.py`
