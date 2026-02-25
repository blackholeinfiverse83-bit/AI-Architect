@echo off
echo ============================================
echo Starting Streamlit Prompt Runner
echo ============================================

cd /d "%~dp0"

if not exist venv (
    echo [1/2] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [2/2] Installing requirements...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting Streamlit...
python -m streamlit run main.py --server.port 8501

pause
