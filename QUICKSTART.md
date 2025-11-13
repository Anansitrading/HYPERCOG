# HyperCog Quick Start

## Setup (5 minutes)

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Create .env file
cp .env.example .env
# Edit .env and add your API keys (OPENAI_API_KEY is required)

# 3. Start FalkorDB (optional - only if using Cognee)
docker-compose up -d falkordb

# 4. Test the server
python -c "from hypercog_mcp.orchestrator import HyperCogOrchestrator; print('✅ Import works')"
```

## Current Status

✅ Project structure created  
✅ All code improvements applied  
✅ Virtual environment setup  
✅ Core dependencies installed  
⚠️ Need to add API keys to .env  
⚠️ Cognee adapter requires Python 3.11+ (optional)

## What Works Now

- Context extraction & evaluation
- Deep thinking agent with hermeneutic circle
- Optimization with proper token counting
- Structured logging to stderr
- Input validation
- Error handling & timeouts

## What Needs API Keys

- **OPENAI_API_KEY**: Required for all LLM operations
- **PERPLEXITY_API_KEY**: Optional, for web search
- **GOOGLE_API_KEY**: Optional, for file search

## Quick Test

```bash
# After adding OPENAI_API_KEY to .env
source venv/bin/activate
python -m hypercog_mcp.server
```

The server will start and listen for MCP connections via stdio.
