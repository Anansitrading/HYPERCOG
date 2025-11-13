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

### ✅ WORKING
- Project structure & code architecture
- All production improvements (logging, error handling, timeouts, validation)
- Context extraction & evaluation agents
- Deep thinking agent with hermeneutic circle
- Optimization agent with tiktoken
- SCRUM breakdown agent
- Perplexity search sub-agent (with API key)
- File search sub-agent (with API key)

### ⚠️ NOT YET WORKING
- **Cognee Knowledge Graph integration** - requires Python 3.11+
- **Cognee Vector Search** - requires Python 3.11+
- **FalkorDB setup** - needs manual Docker launch
- Full orchestration flow (missing Cognee components)

### 🔧 WHAT'S BROKEN

**Critical Issue**: The `cognee-community-hybrid-adapter-falkor` package requires Python 3.11+, but you have Python 3.10. This means:

❌ **CogneeKGAgent** - Won't work (imports will fail)  
❌ **CogneeVectorAgent** - Won't work (imports will fail)  
✅ **PerplexitySearchAgent** - Will work with API key  
✅ **FileSearchAgent** - Will work with API key  

**What This Means**: The enrichment phase can only use 2 out of 4 sub-agents (50% functionality).

## Required API Keys

- **OPENAI_API_KEY**: ✅ Required, works on Python 3.10
- **PERPLEXITY_API_KEY**: ✅ Optional, works on Python 3.10
- **GOOGLE_API_KEY**: ✅ Optional, works on Python 3.10

## Quick Test

```bash
# After adding OPENAI_API_KEY to .env
source venv/bin/activate
python -m hypercog_mcp.server
```

The server will start and listen for MCP connections via stdio.
