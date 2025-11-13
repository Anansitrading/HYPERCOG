#!/bin/bash
# Install HyperCog dependencies with Python 3.11
# Run this after upgrade_to_python311.sh

set -e

echo "📦 Installing HyperCog Dependencies"
echo "===================================="
echo ""

# Activate pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Activate venv
cd /home/david/Projects/HYPERCOG
source venv/bin/activate

echo "Python version: $(python --version)"
echo ""

# Upgrade pip first
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel -q

# Install dependencies
echo "📦 Installing dependencies (this takes 5-10 minutes)..."
echo "   - Core: mcp, structlog, tiktoken"
echo "   - LLM: openai, google-generativeai"  
echo "   - Cognee: cognee + falkordb adapter (200+ packages)"
echo ""

pip install -r requirements.txt

echo ""
echo "============================================"
echo "✅ Installation Complete!"
echo "============================================"
echo ""

# Verify key imports
echo "🔍 Verifying installations..."
python -c "import mcp; print('✅ MCP')"
python -c "import structlog; print('✅ structlog')"
python -c "import tiktoken; print('✅ tiktoken')"
python -c "import openai; print('✅ OpenAI')"
python -c "import cognee; print('✅ Cognee')"
python -c "import cognee_community_hybrid_adapter_falkor; print('✅ Cognee FalkorDB adapter')"

echo ""
echo "🎉 All dependencies installed successfully!"
echo ""
echo "Next: Start FalkorDB"
echo "  docker-compose up -d falkordb"
