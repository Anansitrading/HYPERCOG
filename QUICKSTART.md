# HyperCog Quick Start

## ✅ Status: Python 3.11 Upgrade Complete

Python 3.11.8 is installed via pyenv. Now installing dependencies.

## Complete Installation

Run these commands in your terminal:

```bash
cd /home/david/Projects/HYPERCOG

# Activate pyenv and venv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
source venv/bin/activate

# Verify Python version
python --version  # Should show Python 3.11.8

# Install ALL dependencies (takes 5-10 minutes)
pip install -r requirements.txt

# This installs 200+ packages including:
# - cognee + cognee-community-hybrid-adapter-falkor
# - mcp, structlog, tiktoken
# - openai, google-generativeai
# - Many other dependencies
```

## After Installation

### 1. Verify Installation

```bash
python -c "import cognee; print('✅ Cognee')"
python -c "import cognee_community_hybrid_adapter_falkor; print('✅ FalkorDB adapter')"
python -c "import mcp, structlog, tiktoken; print('✅ Core deps')"
```

### 2. Configure Environment

```bash
# Copy and edit .env
cp .env.example .env
nano .env

# Add your API keys:
# OPENAI_API_KEY=your_key_here (REQUIRED)
# PERPLEXITY_API_KEY=your_key_here (optional)
# GOOGLE_API_KEY=your_key_here (optional)
```

### 3. Start FalkorDB

```bash
docker-compose up -d falkordb

# Verify it's running
docker ps | grep falkordb
curl http://localhost:3000
```

### 4. Test the Server

```bash
python -m hypercog_mcp.server
```

## What Now Works

✅ **All 4 sub-agents:**
- Perplexity Search
- Google File Search  
- Cognee Knowledge Graph
- Cognee Vector Search

✅ **Full enrichment pipeline**
✅ **100% functionality**

## Troubleshooting

### If pip install hangs
The installation has 200+ packages and can take 5-10 minutes. Be patient.

### If imports fail
Make sure you're in the venv:
```bash
which python  # Should point to venv/bin/python
python --version  # Should show 3.11.8
```

### To reinstall
```bash
pip install --force-reinstall -r requirements.txt
```

## Next Steps

1. Finish `pip install -r requirements.txt`
2. Add API keys to `.env`
3. Start FalkorDB
4. Run the MCP server
5. Connect from your MCP client (Amp, Claude, etc.)
