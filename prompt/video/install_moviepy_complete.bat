@echo off
echo MoviePy Complete Installation for AI-Agent
echo ==========================================

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Step 1: Removing existing MoviePy installations...
python -m pip uninstall moviepy -y
python -m pip uninstall imageio-ffmpeg -y
python -m pip uninstall imageio -y
python -m pip uninstall decorator -y
python -m pip uninstall proglog -y
python -m pip uninstall tqdm -y

echo.
echo Step 2: Installing dependencies in correct order...
python -m pip install "numpy>=1.17.3"
python -m pip install "pillow>=8.3.2"
python -m pip install "decorator>=4.0.2,<5.0"
python -m pip install "tqdm>=4.11.2,<5.0"
python -m pip install "requests>=2.8.1,<3.0"
python -m pip install "proglog<=1.0.0"
python -m pip install "imageio>=2.5,<3.0"
python -m pip install "imageio-ffmpeg>=0.2.0"

echo.
echo Step 3: Installing MoviePy...
python -m pip install moviepy==1.0.3

echo.
echo Step 4: Testing MoviePy installation...
python -c "from moviepy.editor import VideoFileClip, ImageClip, TextClip; print('SUCCESS: MoviePy working!')"

if errorlevel 1 (
    echo.
    echo MoviePy test failed. Trying alternative installation...
    python -m pip install moviepy --no-deps
    python -c "from moviepy.editor import VideoFileClip; print('SUCCESS: Basic MoviePy working!')"
)

echo.
echo Step 5: Configuring imageio for FFmpeg...
python -c "import imageio; imageio.plugins.ffmpeg.download(); print('FFmpeg configured')"

echo.
echo ==========================================
echo MoviePy installation complete!
echo Test with: python -c "from moviepy.editor import VideoFileClip"
echo ==========================================
pause