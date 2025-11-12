# HyperCog MCP - Advanced Context Enrichment Orchestration

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

HyperCog is an advanced MCP (Model Context Protocol) server that orchestrates context enrichment using multiple AI agents, knowledge graphs, and vector search to produce world-class outcomes.

## 🎯 Key Features

- **Intelligent Context Evaluation**: Assesses context sufficiency before task execution
- **Deep Thinking Agent**: Uses Hermeneutic Circle methodology for recursive understanding
- **Multi-Source Enrichment**: Integrates Perplexity, Google File Search, and Cognee (KG + Vector)
- **Mandatory Optimization**: ALL execution paths converge through context optimization
- **Smart Task Decomposition**: SCRUM agent breaks down large contexts into manageable subtasks
- **Hybrid Graph+Vector Storage**: Powered by Cognee and FalkorDB

## 📊 Architecture

```
HyperCog --enrich
    ↓
Extract Context → Evaluate
    ↓
[Sufficient?] → YES → [Manageable?] → YES → OPTIMIZE → Execute
              ↓                       ↓
              NO                      NO → SCRUM → OPTIMIZE each → Execute
              ↓
        Deep Thinking (Hermeneutic Circle)
              ↓
        Identify Gaps → Craft Queries
              ↓
        Sub-Agents (Perplexity, File Search, Cognee KG, Cognee Vector)
              ↓
        Consolidate Results
              ↓
        [Manageable?] → YES → OPTIMIZE → Execute
              ↓
              NO → SCRUM → OPTIMIZE each → Execute
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API key
- Google API key (for Gemini File Search)
- Perplexity API key

### 2. Installation

```bash
# Clone the repository
cd /home/david/Projects/HYPERCOG

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_API_KEY`: Your Google/Gemini API key
- `PERPLEXITY_API_KEY`: Your Perplexity API key
- `GRAPH_DB_URL`: FalkorDB host (default: localhost)
- `GRAPH_DB_PORT`: FalkorDB port (default: 6379)

### 4. Start FalkorDB

```bash
# Start FalkorDB with Docker Compose
docker-compose up -d

# Verify it's running
curl http://localhost:3000
```

### 5. Start HyperCog MCP Server

```bash
# Run the MCP server
python -m hypercog_mcp.server

# Or use the CLI
hypercog --help
```

## 🔧 Configuration

### MCP Client Configuration (Amp, Claude, etc.)

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "hypercog": {
      "command": "python",
      "args": ["-m", "hypercog_mcp.server"],
      "cwd": "/home/david/Projects/HYPERCOG",
      "env": {
        "OPENAI_API_KEY": "your-key",
        "GOOGLE_API_KEY": "your-key",
        "PERPLEXITY_API_KEY": "your-key"
      }
    }
  }
}
```

## 📖 Usage

### Using the MCP Tool

The HyperCog MCP server exposes one main tool: `hypercog_enrich`

```python
{
  "name": "hypercog_enrich",
  "arguments": {
    "task": "Implement a JWT authentication system",
    "session_context": "Current project uses Express.js...",
    "attached_files": [
      {"path": "/path/to/file.js"}
    ],
    "workspace_path": "/path/to/project",
    "user_intent": "Build secure auth with refresh tokens"
  }
}
```

### Agent System Prompts

All agent prompts are editable markdown files in `hypercog_mcp/agents/prompts/`:

- `evaluator_agent.md`: Context sufficiency evaluation
- `deep_thinking_agent.md`: Hermeneutic circle methodology
- `optimizer_agent.md`: Context optimization (MANDATORY)
- `consolidator_agent.md`: Multi-source result consolidation
- `scrum_agent.md`: Task decomposition

Edit these files to customize agent behavior without code changes.

## 🏗️ Project Structure

```
hypercog_mcp/
├── agents/
│   ├── prompts/           # Editable agent prompts
│   ├── base_agent.py
│   ├── context_extractor.py
│   ├── evaluator.py
│   ├── deep_thinking.py
│   ├── consolidator.py
│   ├── optimizer.py
│   └── scrum_agent.py
├── sub_agents/
│   ├── perplexity/
│   ├── file_search/
│   ├── cognee_kg/
│   └── cognee_vector/
├── storage/
│   ├── prompt_store/      # Raw extracted context
│   ├── rough/             # Consolidated research
│   └── optimized/         # Optimized context
├── config/
│   ├── cognee_config.py
│   ├── gemini_config.py
│   └── env_config.py
├── orchestrator.py        # Main orchestration engine
├── llm_client.py
└── server.py              # MCP server
```

## 🎨 Key Concepts

### Hermeneutic Circle

The Deep Thinking Agent uses a hermeneutic methodology:
1. **Iteration 1**: Examine parts (identify gaps)
2. **Iteration 2**: Consider whole (context relationships)
3. **Iteration 3**: Synthesize (final refined understanding)

### Zone Placement Strategy

The Optimizer Agent uses 4-zone placement:
- **Zone 1** (Start): Task definition
- **Zone 2** (Middle-Early): Core technical context
- **Zone 3** (Middle-Late): Supporting information
- **Zone 4** (End - Most Current Tokens): ⚠️ **CRITICAL GOTCHAS**

Zone 4 is crucial - the LLM sees this last, giving it highest attention weight.

### Mandatory Optimization

**ALL execution paths flow through the Optimizer Agent** - this is non-negotiable in the corrected flow. Whether context is:
- Sufficient + manageable
- Sufficient + needs breakdown
- Enriched + manageable
- Enriched + needs breakdown

...it MUST be optimized before execution.

## 🔍 Storage & Artifacts

### prompt_store/
Raw extracted context from each session
```
{session_id}_context.json
```

### rough/
Unprocessed sub-agent results
```
{timestamp}_perplexity.json
{timestamp}_file_search.json
{timestamp}_cognee_kg.json
{timestamp}_cognee_vector.json
```

### optimized/
Final optimized contexts ready for execution
```
{session_id}_{timestamp}_optimized.json
```

## 🧪 Development

### Running Tests

```bash
# TODO: Add tests
pytest tests/
```

### Editing Agent Prompts

```bash
# Edit any agent prompt
nano hypercog_mcp/agents/prompts/evaluator_agent.md

# Changes take effect immediately on next server restart
```

## 🐛 Troubleshooting

### FalkorDB Connection Issues

```bash
# Check FalkorDB is running
docker ps | grep falkordb

# Check logs
docker logs hypercog-falkordb

# Restart FalkorDB
docker-compose restart falkordb
```

### API Key Issues

```bash
# Verify environment variables
env | grep API_KEY

# Or in Python
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Cognee Setup Issues

If Cognee fails to initialize, the server will continue without KG/Vector search capabilities. Check:
- FalkorDB is accessible
- Correct ports in .env
- Cognee adapter is installed: `pip install cognee-community-hybrid-adapter-falkor`

## 📝 TODO

- [ ] Add comprehensive tests
- [ ] CLI commands for status, prompt editing
- [ ] Cognee document ingestion utilities
- [ ] Performance metrics and monitoring
- [ ] Docker image for easy deployment
- [ ] Integration examples with popular MCP clients

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Cognee](https://docs.cognee.ai/) for knowledge graph capabilities
- [FalkorDB](https://falkordb.com/) for hybrid graph+vector storage
- [Perplexity](https://perplexity.ai/) for web search
- [Model Context Protocol](https://modelcontextprotocol.io/) specification

---

Built with 🔥 by the HyperCog team
