@echo off
echo ==========================================
echo Video Service Dependencies Installation
echo ==========================================
echo.

cd /d "%~dp0"

echo Installing required packages for video generation...
echo.

REM Install moviepy and dependencies
pip install moviepy==1.0.3 Pillow numpy

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Restart the video service
echo 2. Test video generation
echo.
pause
