# Render Deployment - Quick Reference Card

## 🔧 Backend Service Configuration

**Service Name:** `design-engine-api`

**Settings:**
- Root Directory: `prompt-to-json-main/backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`
- Python Version: `3.11.0`

**Essential Environment Variables:**
```
PYTHON_VERSION=3.11.0
PORT=10000
DATABASE_URL=<your-database-url>
JWT_SECRET_KEY=<random-secret-key>
DEMO_USERNAME=admin
DEMO_PASSWORD=<your-password>
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-key>
SUPABASE_SERVICE_KEY=<your-service-key>
DEBUG=false
ENVIRONMENT=production
```

---

## 🎨 Frontend Service Configuration

**Service Name:** `samrachna-frontend`

**Settings:**
- Root Directory: `frontend-webapp`
- Build Command: `npm install`
- Start Command: `npm start`
- Node Version: `>=14.0.0`

**Environment Variables:**
```
NODE_ENV=production
PORT=3000
```

**⚠️ After Backend Deploys:**
Update `frontend-webapp/app.js` line 7:
```javascript
const API_BASE_URL = 'https://your-backend-url.onrender.com';
```

---

## 📋 Deployment Steps

1. **Deploy Backend First**
   - Create web service
   - Use settings above
   - Add environment variables
   - Wait for deployment

2. **Get Backend URL**
   - Copy URL from Render dashboard
   - Example: `https://design-engine-api-xxxx.onrender.com`

3. **Update Frontend Code**
   - Edit `frontend-webapp/app.js`
   - Update `API_BASE_URL` to backend URL
   - Commit and push

4. **Deploy Frontend**
   - Create web service
   - Use settings above
   - Add environment variables
   - Deploy

---

## ✅ Quick Test

**Backend Health:**
```
https://your-backend.onrender.com/health
```

**Video API Health:**
```
https://your-backend.onrender.com/api/v1/video/health
```

**Frontend:**
```
https://your-frontend.onrender.com
```

---

For detailed instructions, see `MANUAL_RENDER_DEPLOYMENT.md`
