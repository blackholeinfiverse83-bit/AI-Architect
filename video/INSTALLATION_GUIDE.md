# AI-Agent Installation Guide - Dependency Resolution

This guide provides multiple methods to install all dependencies successfully for the AI-Agent project.

## 🚀 Quick Installation (Recommended)

### Method 1: Automated Windows Installation
```cmd
# Double-click or run in Command Prompt
install-dependencies.bat
```

### Method 2: Python Setup Script
```cmd
# In Command Prompt or VS Code Terminal
python setup_env.py
```

### Method 3: Manual Step-by-Step
```cmd
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install build tools
python -m pip install --upgrade pip
python -m pip install "setuptools<70" wheel

# 3. Install core dependencies
python -m pip install -r requirements-install.txt

# 4. Install special packages
python -m pip install moviepy --no-deps
python -m pip install decorator imageio proglog tqdm
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
python -m pip install "starlette>=0.27.0,<0.28.0"

# 5. Install remaining packages
python -m pip install -r requirements_resolved.txt
```

## 🛠️ Troubleshooting

### If Installation Fails
```cmd
# Run the emergency fixer
python fix_dependencies.py
```

### Common Issues and Solutions

#### Issue 1: `pkgutil.ImpImporter` Error (Python 3.12)
**Solution:** Install setuptools<70 first
```cmd
python -m pip install "setuptools<70" wheel
```

#### Issue 2: Starlette Version Conflict
**Solution:** Fix version explicitly
```cmd
python -m pip install "starlette>=0.27.0,<0.28.0"
```

#### Issue 3: MoviePy Installation Fails
**Solution:** Install without dependencies
```cmd
python -m pip uninstall moviepy -y
python -m pip install moviepy --no-deps
python -m pip install decorator imageio proglog tqdm
```

#### Issue 4: PyTorch Installation Issues
**Solution:** Use CPU-only version
```cmd
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Issue 5: Cryptography Build Errors
**Solution:** Use compatible version
```cmd
python -m pip install "cryptography>=41.0.0,<42.0.0"
```

## 📋 Verification

After installation, verify everything works:

```cmd
# Test core imports
python -c "import fastapi, uvicorn, sqlmodel, numpy, pandas; print('SUCCESS: Core packages working!')"

# Test application startup
python -c "from app.main import app; print('SUCCESS: Application loads correctly!')"

# Initialize database
python -c "from core.database import create_db_and_tables; create_db_and_tables()"

# Start server
python scripts/start_server.py
```

## 🎯 What Each File Does

- **`requirements_resolved.txt`**: Main requirements with fixed versions
- **`requirements-install.txt`**: Minimal core dependencies for initial install
- **`setup_env.py`**: Comprehensive Python installation script
- **`install-dependencies.bat`**: Windows batch file for one-click install
- **`fix_dependencies.py`**: Emergency fixer for failed installations

## 🔧 Manual Package Installation Order

If automated scripts fail, install in this exact order:

1. **Build Tools**
   ```cmd
   python -m pip install --upgrade pip
   python -m pip install "setuptools<70" wheel
   ```

2. **Core FastAPI Stack**
   ```cmd
   python -m pip install fastapi==0.104.1
   python -m pip install uvicorn[standard]==0.24.0
   python -m pip install "starlette>=0.27.0,<0.28.0"
   ```

3. **Database & Auth**
   ```cmd
   python -m pip install sqlmodel==0.0.14
   python -m pip install pydantic==2.5.0
   python -m pip install python-jose[cryptography]==3.3.0
   ```

4. **Data Processing**
   ```cmd
   python -m pip install "numpy==1.25.2"
   python -m pip install "pandas==2.1.4"
   ```

5. **Special Packages**
   ```cmd
   python -m pip install moviepy --no-deps
   python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

## ✅ Success Indicators

You'll know installation succeeded when:

- ✅ No error messages during pip install
- ✅ `python -c "import fastapi"` works without errors
- ✅ `python scripts/start_server.py` starts without crashes
- ✅ Server responds at http://localhost:9000/health

## 🆘 Getting Help

If you still have issues:

1. Check Python version: `python --version` (should be 3.8+)
2. Check virtual environment: `where python` (should point to venv)
3. Run emergency fixer: `python fix_dependencies.py`
4. Check the error logs in the terminal output

## 📦 Package Versions Summary

Key fixed versions for compatibility:
- Python: 3.8+ (tested on 3.12)
- FastAPI: 0.104.1
- Starlette: >=0.27.0,<0.28.0
- NumPy: 1.25.2
- Pandas: 2.1.4
- Setuptools: <70 (critical for Python 3.12)
- PyTorch: CPU version from official index