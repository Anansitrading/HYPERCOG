# Manual Installation Instructions

## Quick Commands (Copy & Paste)

```bash
# 1. Navigate to project
cd /home/david/Projects/HYPERCOG

# 2. Activate pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# 3. Verify Python version
python --version
# Should show: Python 3.11.8

# 4. Activate virtual environment
source venv/bin/activate

# 5. Verify you're in the right venv
which python
# Should show: /home/david/Projects/HYPERCOG/venv/bin/python

# 6. Upgrade pip
pip install --upgrade pip setuptools wheel

# 7. Install dependencies (takes 5-10 minutes)
pip install -r requirements.txt

# Watch it run - be patient!
```

## After Installation Completes

```bash
# Verify core packages
python -c "import cognee; print('✅ Cognee')"
python -c "import cognee_community_hybrid_adapter_falkor; print('✅ FalkorDB adapter')"
python -c "import mcp; print('✅ MCP')"
python -c "import structlog; print('✅ Structlog')"
python -c "import tiktoken; print('✅ Tiktoken')"
python -c "import openai; print('✅ OpenAI')"

# Check package count
pip list | wc -l
# Should show 200+ packages
```

## Configure & Run

```bash
# 1. Add API keys
cp .env.example .env
nano .env
# Add your OPENAI_API_KEY (required)

# 2. Start FalkorDB
docker-compose up -d falkordb

# 3. Test the server
python -m hypercog_mcp.server
```

## If Something Goes Wrong

```bash
# Clear pip cache and retry
pip cache purge
pip install -r requirements.txt

# Or force reinstall everything
pip install --force-reinstall -r requirements.txt
```

## You're Done When...

✅ `python --version` shows 3.11.8  
✅ `python -c "import cognee"` doesn't error  
✅ `pip list | wc -l` shows 200+ packages  
✅ All verification imports work  

Then you have **100% functionality** with all 4 sub-agents working!
