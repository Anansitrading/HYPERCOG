# Configure HyperCog MCP in Amp

## Step 1: Copy Config to Amp Settings

**For Amp/VS Code:** Open Command Palette (Ctrl+Shift+P) → "Preferences: Open User Settings (JSON)"

Add this to your `settings.json`:

```json
{
  "amp.mcpServers": {
    "hypercog": {
      "command": "python",
      "args": ["-m", "hypercog_mcp.server"],
      "cwd": "/home/david/Projects/HYPERCOG",
      "env": {
        "OPENAI_API_KEY": "YOUR_KEY_HERE",
        "PERPLEXITY_API_KEY": "YOUR_KEY_HERE",
        "GOOGLE_API_KEY": "YOUR_KEY_HERE",
        "GRAPH_DB_URL": "localhost",
        "GRAPH_DB_PORT": "6379",
        "VECTOR_DB_URL": "localhost",
        "VECTOR_DB_PORT": "6379",
        "LLM_MODEL": "gpt-4",
        "PATH": "/home/david/.pyenv/shims:/home/david/.pyenv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
      }
    }
  }
}
```

**IMPORTANT:** Replace `YOUR_KEY_HERE` with your actual API keys from `.env`

## Step 2: Start FalkorDB

```bash
cd /home/david/Projects/HYPERCOG
docker-compose up -d falkordb
```

## Step 3: Reload Amp

- Reload VS Code window (Ctrl+Shift+P → "Developer: Reload Window")
- Or restart Amp

## Step 4: Test the MCP Server

In Amp chat, try:
```
Use the hypercog_enrich tool to enrich context for: "Implement JWT authentication"
```

## Alternative: Use amp-mcp-config.json

If Amp supports external config files:

```bash
amp --mcp-config /home/david/Projects/HYPERCOG/amp-mcp-config.json
```

## Verification

After configuration, check:
1. Amp's MCP server list should show "hypercog"
2. The tool "hypercog_enrich" should be available
3. Server logs go to stderr (visible in Amp's output panel)

## Troubleshooting

### Server won't start
```bash
# Test manually first
cd /home/david/Projects/HYPERCOG
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
source venv/bin/activate
python -m hypercog_mcp.server
```

Should show:
```
2025-11-13T14:49:08Z [info] hypercog_mcp_starting
2025-11-13T14:49:08Z [info] cognee_initialized
2025-11-13T14:49:08Z [info] hypercog_mcp_ready
```

### PATH issues
Make sure the `PATH` in config includes pyenv shims so Python 3.11 is found.

### API key errors
Verify keys in the `env` section match your actual keys from `.env`

## What You'll Get

Once connected to Amp, you can use:

**Tool:** `hypercog_enrich`

**Capabilities:**
- ✅ Context evaluation (world-class sufficiency check)
- ✅ Deep thinking with hermeneutic circle (3 iterations)
- ✅ Multi-source enrichment (Perplexity + File Search + Cognee KG + Cognee Vector)
- ✅ Mandatory context optimization with zone placement
- ✅ SCRUM breakdown for oversized contexts
- ✅ All 4 sub-agents working with Python 3.11
