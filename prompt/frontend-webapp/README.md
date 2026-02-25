# BHIV Design Engine - Frontend Web App

A modern, responsive web frontend for the BHIV Design Engine API.

## Features

- **Modern UI**: Clean, professional interface with dark theme
- **Authentication**: JWT-based login system
- **Dashboard**: Quick overview and fast design generation
- **Generate**: Create new designs with prompts, city, style, and budget
- **Switch**: Change materials in existing designs
- **Iterate**: Improve designs with different strategies
- **Evaluate**: Rate and provide feedback on designs
- **Compliance**: Check building compliance against regulations
- **History**: View design history and iterations
- **Geometry**: Generate 3D models from designs
- **Reports**: Generate detailed reports
- **RL Training**: Reinforcement learning feedback and training

## Getting Started

### Prerequisites

- Backend API running on `http://127.0.0.1:8000`
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Running the Frontend Locally

#### Option 1: Open Directly
Simply open the `index.html` file in your browser:
```bash
cd frontend-webapp
# Windows
start index.html
# macOS
open index.html
# Linux
xdg-open index.html
```

#### Option 2: Use a Local Server (Recommended)
For better compatibility with API calls:

```bash
cd frontend-webapp
# Python 3
python -m http.server 3000

# Or Node.js
npx serve .

# Or PHP
php -S localhost:3000
```

Then open `http://localhost:3000` in your browser.

### Default Credentials

- **Username**: admin
- **Password**: bhiv2024

---

## Deploying to Render

### Step 1: Push to GitHub

First, make sure your code is in a GitHub repository:

```bash
cd frontend-webapp
git init
git add .
git commit -m "Initial frontend deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bhiv-frontend.git
git push -u origin main
```

### Step 2: Update API URL

Before deploying, update the API URL in `app.js`:

```javascript
// Line 5-8 in app.js
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:8000' 
    : 'https://your-backend-url.onrender.com'; // <-- UPDATE THIS
```

Replace `'https://your-backend-url.onrender.com'` with your actual backend URL.

### Step 3: Deploy on Render

#### Method A: Using Render Dashboard (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Static Site"** (or **"Web Service"**)
3. Connect your GitHub repository
4. Configure:
   - **Name**: `bhiv-design-engine-frontend`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Plan**: Free
5. Click **"Create Web Service"**

#### Method B: Using render.yaml (Blueprint)

1. Make sure `render.yaml` is in your repository root
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render will automatically read `render.yaml` and create the service

### Step 4: Environment Variables (Optional)

In Render Dashboard, go to your service → **Environment** tab:

Add if needed:
- `NODE_ENV`: `production`

### Step 5: Custom Domain (Optional)

1. In Render Dashboard, go to your service → **Settings**
2. Scroll to **Custom Domains**
3. Click **"Add Custom Domain"**
4. Follow the DNS instructions

### Deployed URL

After deployment, your frontend will be available at:
```
https://bhiv-design-engine-frontend.onrender.com
```

---

## Project Structure

```
frontend-webapp/
├── index.html          # Main HTML file
├── styles.css          # Styling and themes
├── app.js              # JavaScript logic and API calls
├── server.js           # Express server for production
├── package.json        # Node.js dependencies
├── render.yaml         # Render deployment config
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## API Configuration

The frontend connects to the backend API. The URL is configured in `app.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:8000'  // Local development
    : 'https://your-backend-url.onrender.com';  // Production
```

## Features Guide

### 1. Dashboard
- View metrics: Total designs, API status, last spec ID, estimated cost
- Quick generate section for fast design creation

### 2. Generate Design
- Enter a design description
- Select city (Mumbai, Pune, Ahmedabad, Nashik, Bangalore)
- Choose style (Modern, Traditional, Contemporary, Rustic, Industrial)
- Set budget (0 for auto-estimation)
- View generated design with Spec ID, cost, and preview URL

### 3. Switch Materials
- Enter Spec ID
- Specify material change request
- Apply changes to existing design

### 4. Iterate Design
- Enter Spec ID
- Select strategy: Auto Optimize, Improve Materials, Improve Layout, Improve Colors
- Iterate on existing design

### 5. Evaluate Design
- Enter Spec ID
- Rate design (1-5 stars)
- Add notes and feedback

### 6. Compliance Check
- Enter building parameters
- Check against municipal regulations
- View compliance results

### 7. History
- View user design history
- View spec-specific history

### 8. Geometry
- List available geometry files
- Generate 3D models (GLB, OBJ, FBX)

### 9. Reports
- Generate detailed reports for designs

### 10. RL Training
- Submit feedback for reinforcement learning
- Train RLHF model
- Train PPO model

---

## Troubleshooting

### CORS Issues
If you see CORS errors in the browser console, ensure the backend has CORS enabled. The backend should have:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins like ["https://your-frontend.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Not Connected
- Verify the backend is running and accessible
- Check the API_BASE_URL in app.js matches your backend URL
- Ensure no firewall is blocking the connection
- Check browser console for error messages

### Build Fails on Render
- Make sure `package.json` is correct
- Check Render logs for specific errors
- Ensure all files are committed to Git

### 404 Errors
- The frontend uses client-side routing
- `server.js` handles all routes by serving `index.html`
- This is already configured

### Login Issues
- Default credentials: admin / bhiv2024
- Check browser console for error messages
- Verify the backend `/api/v1/auth/login` endpoint is accessible
- Check CORS settings on backend

---

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

Proprietary - BHIV AI Platform
