#!/usr/bin/env python3
"""
Emergency dependency fixer for AI-Agent project
Run this if the main installation fails
"""

import subprocess
import sys
import os

def run_pip_command(cmd, description):
    """Run pip command with error handling"""
    print(f"\n🔧 {description}")
    try:
        result = subprocess.run(f"python -m pip {cmd}", shell=True, 
                              capture_output=True, text=True, check=True)
        print(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        print(f"Error: {e.stderr}")
        return False

def fix_common_issues():
    """Fix common dependency installation issues"""
    
    print("🛠️  Fixing common dependency issues...")
    
    # Common fixes for Python 3.12
    fixes = [
        ("install --upgrade pip setuptools wheel", "Upgrading core tools"),
        ("install \"setuptools<70\"", "Fixing setuptools version"),
        ("install \"starlette>=0.27.0,<0.28.0\"", "Fixing Starlette version"),
        ("install \"cryptography>=41.0.0,<42.0.0\"", "Fixing cryptography version"),
        ("install \"bcrypt==4.0.1\"", "Fixing bcrypt version"),
        ("install \"numpy==1.25.2\"", "Installing compatible NumPy"),
        ("install \"pandas==2.1.4\"", "Installing compatible Pandas"),
        ("uninstall moviepy -y", "Removing problematic MoviePy"),
        ("install moviepy --no-deps", "Reinstalling MoviePy without deps"),
        ("install decorator imageio proglog tqdm", "Installing MoviePy dependencies"),
    ]
    
    success_count = 0
    for cmd, desc in fixes:
        if run_pip_command(cmd, desc):
            success_count += 1
    
    print(f"\n📊 Fixed {success_count}/{len(fixes)} issues")
    
    # Try to install PyTorch CPU version
    print("\n🧠 Installing PyTorch CPU version...")
    pytorch_cmd = "install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    run_pip_command(pytorch_cmd, "PyTorch CPU installation")

def install_remaining_packages():
    """Install remaining packages one by one"""
    
    remaining_packages = [
        "streamlit==1.28.2",
        "plotly==5.17.0",
        "altair==5.2.0",
        "celery==5.3.4",
        "redis==5.0.1",
        "locust==2.17.0",
        "aiohttp==3.9.1",
        "boto3==1.34.0",
        "supabase==2.3.4",
        "psutil==5.9.6",
        "prometheus-fastapi-instrumentator==6.1.0",
        "vaderSentiment==3.3.2",
        "pillow==10.1.0",
        "opencv-python==4.8.1.78",
        "scikit-learn==1.3.2",
    ]
    
    print(f"\n📦 Installing {len(remaining_packages)} remaining packages...")
    
    for package in remaining_packages:
        run_pip_command(f"install {package}", f"Installing {package}")

def main():
    """Main dependency fixing process"""
    print("🚨 AI-Agent Dependency Emergency Fixer")
    print("=" * 40)
    
    # Fix common issues first
    fix_common_issues()
    
    # Install remaining packages
    install_remaining_packages()
    
    # Final verification
    print("\n🔍 Final verification...")
    try:
        import fastapi
        import uvicorn
        import sqlmodel
        print("✅ Core packages working")
    except ImportError as e:
        print(f"❌ Core package issue: {e}")
    
    print("\n✨ Dependency fixing complete!")
    print("Try running the main application now.")

if __name__ == "__main__":
    main()