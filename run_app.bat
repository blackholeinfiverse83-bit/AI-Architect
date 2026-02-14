@echo off
cd /d "%~dp0"
echo ==========================================
echo    BHIV Design Engine - Startup Script
echo ==========================================
echo.
echo 1. Stopping existing processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo 2. Launching Backend (FastAPI)...
start "BHIV Backend" "prompt-to-json-main\backend\start_server.bat"

echo 3. Launching Frontend (React)...
start "BHIV Frontend" "prompt-web-client\start_web.bat"

echo.
echo Done! 
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
