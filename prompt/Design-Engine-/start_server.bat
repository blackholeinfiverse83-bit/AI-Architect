@echo off
echo Activating virtual environment and starting server...

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "backend\.venv\Scripts\activate.bat" (
    call backend\.venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] No virtual environment found in Design-Engine-. Dependencies might be missing.
)

REM Change to backend directory
cd backend

REM Ensure dependencies are installed just in case
if not exist "venv_installed.marker" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Done > venv_installed.marker
)

REM Start the server using the fully integrated main
echo Starting FastAPI server...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
