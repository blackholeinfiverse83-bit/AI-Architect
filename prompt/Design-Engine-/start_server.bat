@echo off
cd /d "%~dp0"
echo Starting Design Engine Backend Server...
set PYTHONPATH=%~dp0backend;%~dp0
cd /d "%~dp0backend"
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
