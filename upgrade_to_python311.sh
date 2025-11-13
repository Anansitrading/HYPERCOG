#!/bin/bash
# HyperCog Python 3.11 Upgrade Script
# Safe installation using pyenv (doesn't touch system Python)

set -e  # Exit on error

echo "🔧 HyperCog Python 3.11 Upgrade"
echo "================================"
echo ""

# Step 1: Install build dependencies
echo "📦 Step 1/5: Installing build dependencies..."
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
  liblzma-dev python3-openssl git

echo "✅ Build dependencies installed"
echo ""

# Step 2: Install pyenv
echo "📦 Step 2/5: Installing pyenv..."
if [ -d "$HOME/.pyenv" ]; then
    echo "⚠️  pyenv already installed, skipping..."
else
    curl https://pyenv.run | bash
    
    # Add to bashrc if not already there
    if ! grep -q "pyenv init" ~/.bashrc; then
        echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
        echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    fi
    
    # Load pyenv for this script
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
fi

echo "✅ pyenv installed"
echo ""

# Step 3: Install Python 3.11
echo "📦 Step 3/5: Installing Python 3.11.8..."
pyenv install -s 3.11.8  # -s skips if already installed

echo "✅ Python 3.11.8 installed"
echo ""

# Step 4: Set Python 3.11 for this project
echo "📦 Step 4/5: Setting Python 3.11 for HyperCog project..."
cd /home/david/Projects/HYPERCOG
pyenv local 3.11.8

echo "✅ Python 3.11.8 set as local version"
echo ""

# Step 5: Recreate virtual environment
echo "📦 Step 5/5: Recreating virtual environment with Python 3.11..."

# Backup old requirements if they exist
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements.txt.backup
    echo "📋 Backed up requirements.txt"
fi

# Remove old venv
if [ -d "venv" ]; then
    echo "🗑️  Removing old Python 3.10 venv..."
    rm -rf venv
fi

# Create new venv with Python 3.11
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Uncomment Cognee adapter in requirements.txt
sed -i 's/# cognee-community-hybrid-adapter-falkor/cognee-community-hybrid-adapter-falkor/' requirements.txt

echo "✅ Virtual environment created with Python 3.11"
echo ""

echo "============================================"
echo "🎉 Upgrade Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Reload your shell: exec \$SHELL"
echo "  2. Activate venv: source venv/bin/activate"
echo "  3. Install dependencies: pip install -r requirements.txt"
echo "  4. Verify Python version: python --version"
echo ""
echo "Your system Python 3.10 is untouched and safe."
echo "This project now uses Python 3.11.8 via pyenv."
