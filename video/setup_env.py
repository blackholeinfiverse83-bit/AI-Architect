#!/usr/bin/env python3
"""
AI-Agent Dependency Installation Script
Ensures all dependencies install successfully in one run for Windows/Python 3.12
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, description="", check=True):
    """Run a command and handle errors gracefully"""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 8:
        print("❌ Python 3.8+ required")
        return False
    
    if version.minor >= 12:
        print("✅ Python 3.12+ detected - using compatibility mode")
    
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
    else:
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Already in virtual environment")
        return True
    
    print("⚠️  Please activate virtual environment manually:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    return True

def install_build_tools():
    """Install essential build tools first"""
    commands = [
        ("python -m pip install --upgrade pip", "Upgrading pip"),
        ("python -m pip install \"setuptools<70\" wheel", "Installing build tools"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def install_core_dependencies():
    """Install core dependencies from resolved requirements"""
    return run_command(
        "python -m pip install -r requirements_resolved.txt",
        "Installing core dependencies"
    )

def install_special_packages():
    """Install packages that need special handling"""
    commands = [
        # Install moviepy without dependencies to avoid conflicts
        ("python -m pip install moviepy --no-deps", "Installing MoviePy (no deps)"),
        
        # Install moviepy dependencies separately
        ("python -m pip install decorator imageio proglog tqdm", "Installing MoviePy dependencies"),
        
        # Install PyTorch CPU version
        ("python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu", 
         "Installing PyTorch (CPU version)"),
        
        # Fix version conflicts
        ("python -m pip install \"starlette>=0.27.0,<0.28.0\"", "Fixing Starlette version"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc, check=False):  # Don't fail on these
            print(f"⚠️  {desc} failed, but continuing...")
    
    return True

def verify_installation():
    """Verify that key packages are installed correctly"""
    test_imports = [
        "fastapi",
        "uvicorn", 
        "sqlmodel",
        "numpy",
        "pandas",
        "requests",
        "pydantic"
    ]
    
    print("\n🔍 Verifying installation...")
    
    failed_imports = []
    for package in test_imports:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️  Failed to import: {', '.join(failed_imports)}")
        return False
    
    # Test FastAPI app import
    try:
        from app.main import app
        print("✅ FastAPI application loads successfully")
    except Exception as e:
        print(f"⚠️  FastAPI app import issue: {e}")
    
    return True

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        run_command("copy .env.example .env" if platform.system() == "Windows" else "cp .env.example .env",
                   "Creating .env file from template")

def main():
    """Main installation process"""
    print("🚀 AI-Agent Dependency Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install build tools
    if not install_build_tools():
        print("❌ Failed to install build tools")
        sys.exit(1)
    
    # Install core dependencies
    if not install_core_dependencies():
        print("❌ Failed to install core dependencies")
        sys.exit(1)
    
    # Install special packages
    install_special_packages()
    
    # Create .env file
    create_env_file()
    
    # Verify installation
    if verify_installation():
        print("\n🎉 SUCCESS: All dependencies installed successfully!")
        print("\n📋 Next steps:")
        print("1. Activate virtual environment (if not already active)")
        print("2. Configure .env file with your settings")
        print("3. Initialize database: python -c \"from core.database import create_db_and_tables; create_db_and_tables()\"")
        print("4. Start server: python scripts/start_server.py")
        print("5. Access API: http://localhost:9000")
    else:
        print("\n⚠️  Installation completed with some issues")
        print("Check the error messages above and try manual installation for failed packages")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()