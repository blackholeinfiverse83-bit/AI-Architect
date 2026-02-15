@echo off
chcp 65001 >nul
echo Starting Samrachna Unified Backend...
echo.

REM Kill any existing Python processes on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a 2>nul

timeout /t 2 /nobreak >nul

echo Starting Unified Backend (Port 8000)...
echo Includes: Design Engine + Video Generation
cd /d "C:\Users\PIXEL\Desktop\Sid\prompt\prompt-to-json-main"
start "Unified Backend" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"

echo.
echo ==========================================
echo Unified Backend is starting!
echo ==========================================
echo.
echo Backend: http://localhost:8000
echo - Design Engine API: /api/v1/*
echo - Video Generation API: /api/v1/video/*
echo.
echo Wait 10 seconds for service to start...
echo Then test with: curl http://localhost:8000/health
echo ==========================================
pause
