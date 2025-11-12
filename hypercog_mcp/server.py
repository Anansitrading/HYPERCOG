#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import load_environment, setup_cognee
from .orchestrator import HyperCogOrchestrator
from .llm_client import LLMClient

app = Server("hypercog-mcp")

storage_root = Path(__file__).parent / "storage"
storage_root.mkdir(parents=True, exist_ok=True)

orchestrator: HyperCogOrchestrator = None
llm_client: LLMClient = None

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="hypercog_enrich",
            description="""HyperCog context enrichment orchestration.
            
Follows the corrected agent flow:
1. Extract session context
2. Evaluate sufficiency
3. If sufficient + manageable → Optimize → Execute
4. If sufficient + too large → SCRUM breakdown → Optimize each → Execute
5. If insufficient → Deep Thinking → Enrichment (Perplexity, Cognee, Files) → Consolidate → Check size → Optimize → Execute

ALL paths converge at mandatory optimization before execution.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task to enrich context for"
                    },
                    "session_context": {
                        "type": "string",
                        "description": "Current session context"
                    },
                    "attached_files": {
                        "type": "array",
                        "description": "List of attached files",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            }
                        },
                        "default": []
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace directory path",
                        "default": None
                    },
                    "user_intent": {
                        "type": "string",
                        "description": "Explicit user intent",
                        "default": None
                    }
                },
                "required": ["task", "session_context"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    if name != "hypercog_enrich":
        raise ValueError(f"Unknown tool: {name}")
    
    task = arguments.get("task", "")
    
    context = {
        "session_context": arguments.get("session_context", ""),
        "attached_files": arguments.get("attached_files", []),
        "workspace_path": arguments.get("workspace_path"),
        "user_intent": arguments.get("user_intent")
    }
    
    try:
        result = await orchestrator.enrich(task, context)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]
    
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "status": "failed"
                }, indent=2)
            )
        ]

async def main():
    """Main entry point"""
    global orchestrator, llm_client
    
    print("🚀 Starting HyperCog MCP Server...", file=sys.stderr)
    
    load_environment()
    
    try:
        setup_cognee()
    except Exception as e:
        print(f"⚠ Cognee setup warning: {e}", file=sys.stderr)
        print("Continuing without Cognee integration", file=sys.stderr)
    
    llm_client = LLMClient()
    orchestrator = HyperCogOrchestrator(storage_root, llm_client)
    
    print("✓ HyperCog MCP Server ready", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
