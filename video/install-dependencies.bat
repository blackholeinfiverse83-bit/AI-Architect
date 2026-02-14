@echo off
echo AI-Agent Complete Dependency Installer
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated.

REM Run the comprehensive installer
echo Running comprehensive dependency installer...
python install_all_dependencies.py

REM Always show results
echo.
echo ========================================
echo Installation process completed.
echo ========================================
echo.
echo Next steps:
echo 1. Check output above for any errors
echo 2. Copy .env.example to .env and configure
echo 3. Initialize database: python -c "from core.database import create_db_and_tables; create_db_and_tables()"
echo 4. Start server: python scripts\start_server.py
echo 5. Access API: http://localhost:9000
echo.
echo If there were errors, check requirements_backup.txt
echo for successfully installed packages.
echo.
echo Press any key to exit...
pause >nul