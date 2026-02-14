@echo off
echo ==========================================
echo BHIV Design Engine - Frontend Deployment
echo ==========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Check if node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Testing local server...
start cmd /k "npm start"
timeout /t 3 >nul

echo.
echo ==========================================
echo Local server should be running!
echo Open http://localhost:3000 in your browser
echo.
echo To deploy to Render:
echo 1. Create a GitHub repository
echo 2. Push this code to GitHub
echo 3. Go to https://dashboard.render.com/
echo 4. Click "New +" ^> "Web Service"
echo 5. Connect your GitHub repo
echo 6. Use these settings:
echo    - Build Command: npm install
echo    - Start Command: npm start
echo    - Plan: Free
echo ==========================================
echo.

choice /C YN /M "Do you want to initialize Git and push to GitHub now"
if errorlevel 2 goto :skip_git
if errorlevel 1 goto :setup_git

:setup_git
echo.
echo Step 3: Initializing Git repository...
git init
if not exist .gitignore (
    echo Creating .gitignore...
    (
        echo node_modules/
        echo .env
        echo .DS_Store
    ) > .gitignore
)

git add .
git commit -m "Initial frontend deployment"

echo.
echo Git repository initialized!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub
echo 2. Run these commands:
echo    git branch -M main
echo    git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
echo    git push -u origin main
echo.

goto :end

:skip_git
echo.
echo Skipping Git setup.
echo Remember to manually push to GitHub before deploying to Render.

:end
echo.
echo Press any key to exit...
pause >nul
