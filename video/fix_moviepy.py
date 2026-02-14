#!/usr/bin/env python3
"""
MoviePy Installation Fixer for AI-Agent
Specifically fixes moviepy.editor import issues
"""

import subprocess
import sys
import os
import platform

def run_cmd(cmd, description=""):
    """Run command with error handling"""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True, timeout=300)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr[:200]}...")
        return False
    except subprocess.TimeoutExpired:
        print("⏰ Timeout")
        return False

def uninstall_moviepy():
    """Completely remove moviepy and related packages"""
    print("\n🗑️ Removing existing MoviePy installations...")
    
    packages_to_remove = [
        "moviepy",
        "imageio-ffmpeg", 
        "imageio",
        "decorator",
        "proglog",
        "tqdm"
    ]
    
    for package in packages_to_remove:
        run_cmd(f"python -m pip uninstall {package} -y", f"Removing {package}")

def install_system_dependencies():
    """Install system dependencies for MoviePy"""
    print("\n🛠️ Installing system dependencies...")
    
    if platform.system() == "Windows":
        print("Windows detected - MoviePy should work with imageio-ffmpeg")
        # Install imageio-ffmpeg for Windows
        run_cmd("python -m pip install imageio-ffmpeg==0.4.9", "Installing imageio-ffmpeg")
    else:
        print("Non-Windows system - you may need to install ffmpeg manually")

def install_moviepy_dependencies():
    """Install MoviePy dependencies in correct order"""
    print("\n📦 Installing MoviePy dependencies...")
    
    # Install dependencies in specific order
    dependencies = [
        ("numpy>=1.17.3", "NumPy (required by imageio)"),
        ("pillow>=8.3.2", "Pillow (image processing)"),
        ("decorator>=4.0.2,<5.0", "Decorator"),
        ("tqdm>=4.11.2,<5.0", "Progress bars"),
        ("requests>=2.8.1,<3.0", "HTTP requests"),
        ("proglog<=1.0.0", "Progress logging"),
        ("imageio>=2.5,<3.0", "Image I/O"),
        ("imageio-ffmpeg>=0.2.0", "FFmpeg for imageio")
    ]
    
    for dep, desc in dependencies:
        if not run_cmd(f"python -m pip install \"{dep}\"", f"Installing {desc}"):
            print(f"⚠️ {desc} failed, trying without version constraints...")
            base_name = dep.split(">=")[0].split("<=")[0].split("==")[0]
            run_cmd(f"python -m pip install {base_name}", f"Installing {base_name} (any version)")

def install_moviepy():
    """Install MoviePy with specific configuration"""
    print("\n🎬 Installing MoviePy...")
    
    # Try different installation methods
    methods = [
        ("python -m pip install moviepy==1.0.3", "Installing MoviePy 1.0.3"),
        ("python -m pip install moviepy --no-deps", "Installing MoviePy without dependencies"),
        ("python -m pip install moviepy --force-reinstall", "Force reinstalling MoviePy"),
        ("python -m pip install moviepy --no-cache-dir", "Installing MoviePy without cache")
    ]
    
    for cmd, desc in methods:
        if run_cmd(cmd, desc):
            return True
    
    print("❌ All MoviePy installation methods failed")
    return False

def test_moviepy_import():
    """Test if moviepy.editor can be imported"""
    print("\n🔍 Testing MoviePy import...")
    
    test_scripts = [
        ("import moviepy", "Basic moviepy import"),
        ("from moviepy.editor import VideoFileClip", "VideoFileClip import"),
        ("from moviepy.editor import ImageClip", "ImageClip import"),
        ("from moviepy.editor import TextClip", "TextClip import"),
        ("from moviepy.editor import CompositeVideoClip", "CompositeVideoClip import")
    ]
    
    success_count = 0
    
    for script, desc in test_scripts:
        try:
            exec(script)
            print(f"✅ {desc}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {desc}: {e}")
        except Exception as e:
            print(f"⚠️ {desc}: {e}")
    
    print(f"\n📊 MoviePy test results: {success_count}/{len(test_scripts)} successful")
    return success_count >= 3

def fix_imageio_config():
    """Fix imageio configuration for MoviePy"""
    print("\n⚙️ Configuring imageio for MoviePy...")
    
    config_script = '''
import imageio
try:
    # Download ffmpeg if not available
    imageio.plugins.ffmpeg.download()
    print("✅ FFmpeg downloaded successfully")
except Exception as e:
    print(f"⚠️ FFmpeg download issue: {e}")

try:
    # Test ffmpeg
    reader = imageio.get_reader('<video0>')
    print("✅ FFmpeg working")
except Exception as e:
    print(f"⚠️ FFmpeg test failed: {e}")
'''
    
    try:
        exec(config_script)
    except Exception as e:
        print(f"⚠️ Imageio configuration failed: {e}")

def create_moviepy_test():
    """Create a test script to verify MoviePy functionality"""
    test_script = '''
#!/usr/bin/env python3
"""Test MoviePy functionality"""

def test_moviepy():
    try:
        from moviepy.editor import VideoFileClip, ImageClip, TextClip, CompositeVideoClip
        import numpy as np
        
        print("✅ All MoviePy imports successful")
        
        # Test creating a simple clip
        clip = ImageClip(np.zeros((100, 100, 3)), duration=1)
        print("✅ ImageClip creation successful")
        
        # Test text clip (might fail if no font available)
        try:
            text_clip = TextClip("Test", fontsize=20, color='white', duration=1)
            print("✅ TextClip creation successful")
        except Exception as e:
            print(f"⚠️ TextClip failed (normal on some systems): {e}")
        
        print("🎉 MoviePy is working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ MoviePy error: {e}")
        return False

if __name__ == "__main__":
    test_moviepy()
'''
    
    with open("test_moviepy.py", "w") as f:
        f.write(test_script)
    
    print("📝 Created test_moviepy.py - run this to test MoviePy")

def main():
    """Main MoviePy fixing process"""
    print("🎬 MoviePy Installation Fixer")
    print("=" * 40)
    
    # Step 1: Clean installation
    uninstall_moviepy()
    
    # Step 2: Install system dependencies
    install_system_dependencies()
    
    # Step 3: Install dependencies
    install_moviepy_dependencies()
    
    # Step 4: Install MoviePy
    if not install_moviepy():
        print("\n❌ MoviePy installation failed")
        print("Try manual installation:")
        print("1. pip install imageio-ffmpeg")
        print("2. pip install moviepy --no-deps")
        return
    
    # Step 5: Configure imageio
    fix_imageio_config()
    
    # Step 6: Test installation
    if test_moviepy_import():
        print("\n🎉 SUCCESS: MoviePy is working!")
        print("\nYou can now use:")
        print("from moviepy.editor import VideoFileClip, ImageClip, TextClip")
    else:
        print("\n⚠️ MoviePy installed but has import issues")
        print("Check the error messages above")
    
    # Step 7: Create test script
    create_moviepy_test()
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()