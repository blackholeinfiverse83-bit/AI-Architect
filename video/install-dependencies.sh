#!/bin/bash
echo "Installing AI-Agent dependencies for Python 3.12..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install build tools
echo "Upgrading pip and installing build tools..."
python -m pip install --upgrade pip
python -m pip install "setuptools<70" wheel

# Install dependencies from requirements-install.txt
echo "Installing dependencies..."
python -m pip install -r requirements-install.txt

# Install moviepy separately to avoid dependency conflicts
echo "Installing moviepy..."
python -m pip install moviepy --no-deps

# Install PyTorch with CPU support
echo "Installing PyTorch (CPU version)..."
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Fix starlette version conflict
echo "Fixing version conflicts..."
python -m pip install "starlette>=0.27.0,<0.28.0"

# Verify installation
echo "Verifying installation..."
python -c "import fastapi, uvicorn, sqlmodel, numpy, pandas; print('SUCCESS: All core dependencies installed!')"

echo ""
echo "Installation complete!"
echo "To start the server, run: python scripts/start_server.py"