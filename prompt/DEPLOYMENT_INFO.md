# Samrachna - Deployment Information

## 📱 Application Details

**Application Name:** Samrachna  
**Subtitle:** AI Design & Architecture  
**Version:** 1.0.0

---

## 🔗 Deployment URLs

### Backend API (Render)
**URL:** `https://design-engine-api-y8e7.onrender.com`  
**Health Check:** `https://design-engine-api-y8e7.onrender.com/health`  
**API Docs:** `https://design-engine-api-y8e7.onrender.com/docs`  
**Video API Health:** `https://design-engine-api-y8e7.onrender.com/api/v1/video/health`

### Frontend Web App (Render)
**URL:** `https://samrachna-frontend.onrender.com`  
**Status:** Deployed and connected to backend

---

## 🔐 Login Credentials

### Demo/Admin Account
**Username:** `admin`  
**Password:** `bhiv2024`

**Note:** This is the default demo account. For production, change the password in environment variables.

---

## 🛠️ Service Configuration

### Backend Service
- **Platform:** Render
- **Service Name:** `design-engine-api`
- **Root Directory:** `prompt-to-json-main/backend`
- **Build Command:** `pip install --no-cache-dir -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`
- **Python Version:** `3.11.0`

### Frontend Service
- **Platform:** Render
- **Service Name:** `samrachna-frontend`
- **Root Directory:** `frontend-webapp`
- **Build Command:** `npm install`
- **Start Command:** `npm start`
- **Node Version:** `>=14.0.0`

---

## 📝 Important Notes

1. **Backend URL:** The frontend is configured to use `https://design-engine-api-y8e7.onrender.com`
2. **Auto-deployment:** Both services auto-deploy on git push to `main` branch
3. **Free Tier:** Services may spin down after 15 minutes of inactivity
4. **First Request:** May take 30-60 seconds if service was spun down

---

## 🔄 Update Links

If you need to update the backend URL in the frontend:
1. Edit `frontend-webapp/app.js`
2. Update line 7: `const API_BASE_URL = 'https://your-new-backend-url.onrender.com';`
3. Commit and push to trigger redeploy

---

## 📞 Support

For deployment issues:
- Check Render dashboard logs
- Verify environment variables are set
- Test health endpoints
- Check build logs for dependency installation

---

**Last Updated:** 2026-02-15  
**Repository:** `blackholeinfiverse83-bit/AI-Architect`  
**Branch:** `main`
