# Python 3.11 Upgrade Guide

## Why Upgrade?

**cognee-community-hybrid-adapter-falkor** requires Python 3.11+. Without it:
- ❌ Cognee KG search won't work
- ❌ Cognee Vector search won't work
- ⚠️ Only 50% of enrichment functionality available

## Safe Upgrade Using pyenv

We use **pyenv** because it:
- ✅ Doesn't touch your system Python (safe)
- ✅ Allows multiple Python versions
- ✅ Easy to switch between projects
- ✅ No sudo needed for Python management

## Quick Upgrade (Automated)

```bash
# Run the upgrade script
cd /home/david/Projects/HYPERCOG
./upgrade_to_python311.sh

# After completion, reload shell
exec $SHELL

# Activate new venv
source venv/bin/activate

# Install all dependencies (including Cognee adapter)
pip install -r requirements.txt

# Verify
python --version  # Should show Python 3.11.8
```

## Manual Upgrade (Step by Step)

If you prefer to do it manually:

### 1. Install Build Dependencies

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
  liblzma-dev python3-openssl git
```

### 2. Install pyenv

```bash
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
exec $SHELL
```

### 3. Install Python 3.11

```bash
pyenv install 3.11.8
```

### 4. Set Python 3.11 for This Project

```bash
cd /home/david/Projects/HYPERCOG
pyenv local 3.11.8

# Verify
python --version  # Should show 3.11.8
```

### 5. Recreate Virtual Environment

```bash
# Remove old venv
rm -rf venv

# Create new venv with Python 3.11
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 6. Enable Cognee Adapter

```bash
# Uncomment the Cognee adapter line in requirements.txt
nano requirements.txt

# Change this line:
# cognee-community-hybrid-adapter-falkor>=0.1.0  # Requires Python 3.11+

# To this:
cognee-community-hybrid-adapter-falkor>=0.1.0
```

### 7. Install All Dependencies

```bash
pip install -r requirements.txt
```

This will take several minutes (200+ packages).

## Verification

```bash
# Check Python version
python --version
# Output: Python 3.11.8

# Check imports work
python -c "import cognee; import cognee_community_hybrid_adapter_falkor; print('✅ Cognee works')"

# Check MCP imports
python -c "import mcp, structlog, tiktoken; print('✅ Core deps work')"
```

## What Gets Fixed

After upgrading:
- ✅ CogneeKGAgent works
- ✅ CogneeVectorAgent works
- ✅ Full 4/4 sub-agents functional
- ✅ 100% enrichment capability
- ✅ FalkorDB integration works

## Troubleshooting

### pyenv command not found
```bash
# Reload shell
exec $SHELL

# Or manually export
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

### Python 3.11 build fails
```bash
# Make sure build dependencies are installed
sudo apt install -y build-essential libssl-dev zlib1g-dev

# Try again
pyenv install 3.11.8
```

### pip install takes too long
This is normal - cognee has 200+ dependencies. It can take 5-10 minutes.

### Import errors after upgrade
```bash
# Make sure you're in the new venv
which python  # Should point to venv/bin/python

# Reinstall if needed
pip install --force-reinstall -r requirements.txt
```

## Rollback (If Needed)

```bash
# Switch back to Python 3.10
pyenv local 3.10.12

# Recreate venv with old Python
rm -rf venv
python -m venv venv
source venv/bin/activate

# Restore old requirements (without Cognee adapter)
git checkout requirements.txt

# Reinstall
pip install -r requirements.txt
```

## System Python Untouched

Your system Python remains Python 3.10.12:
```bash
/usr/bin/python3 --version
# Python 3.10.12

# Only this project uses 3.11
cd /home/david/Projects/HYPERCOG
python --version
# Python 3.11.8
```

This keeps your Zorin OS safe and stable!
