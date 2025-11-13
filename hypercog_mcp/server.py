#!/usr/bin/env python3
# CRITICAL: Load environment variables FIRST, before any other imports
from pathlib import Path
from dotenv import load_dotenv
import sys
import os

# Load .env immediately to ensure all environment variables are available
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)

# CRITICAL: MCP stdio servers MUST NOT write to stdout except JSON-RPC messages
# Redirect all output to stderr to prevent protocol corruption
class StderrOnly:
    """Redirect all writes to stderr"""
    def write(self, text):
        sys.stderr.write(text)
        return len(text)
    def flush(self):
        sys.stderr.flush()

# Replace stdout with stderr before ANY imports that might print
sys.stdout = StderrOnly()

# Set environment to suppress any library output to stdout
os.environ['PYTHONUNBUFFERED'] = '1'

# Now safe to import modules that depend on environment variables
import asyncio
import json
import signal
from typing import Any, Dict, Optional
import structlog

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field, ValidationError

from .config import setup_cognee
from .orchestrator import HyperCogOrchestrator
from .llm_client import LLMClient
from .utils.logging import setup_logging

logger = setup_logging(log_level="INFO")

app = Server("hypercog-mcp")

storage_root = Path(__file__).parent / "storage"
storage_root.mkdir(parents=True, exist_ok=True)

orchestrator: Optional[HyperCogOrchestrator] = None
llm_client: Optional[LLMClient] = None
shutdown_event = asyncio.Event()

class EnrichInput(BaseModel):
    """Validated input for hypercog_enrich tool"""
    task: str = Field(..., min_length=1, max_length=10000, description="Task description")
    session_context: str = Field(..., min_length=1, description="Session context")
    attached_files: list[Dict[str, str]] = Field(default_factory=list)
    workspace_path: Optional[str] = None
    user_intent: Optional[str] = None

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
    """
    Handle tool calls with input validation
    
    CRITICAL: Never log to stdout in STDIO MCP servers
    All logs go to stderr via structlog
    """
    log = logger.bind(tool=name)
    
    if name != "hypercog_enrich":
        error_msg = f"Unknown tool: {name}"
        log.error("unknown_tool", tool=name)
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": error_msg,
                    "status": "failed"
                }, indent=2)
            )
        ]
    
    try:
        validated = EnrichInput(**arguments)
        log.info("tool_invoked", task_length=len(validated.task))
        
    except ValidationError as e:
        log.error("input_validation_failed", errors=e.errors())
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": "Input validation failed",
                    "details": e.errors(),
                    "status": "failed"
                }, indent=2)
            )
        ]
    
    context = {
        "session_context": validated.session_context,
        "attached_files": validated.attached_files,
        "workspace_path": validated.workspace_path,
        "user_intent": validated.user_intent
    }
    
    try:
        result = await orchestrator.enrich(validated.task, context)
        log.info("tool_completed", status=result.get("status"))
        
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]
    
    except asyncio.TimeoutError:
        log.error("tool_timeout")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": "Enrichment timeout - operation took too long",
                    "status": "failed"
                }, indent=2)
            )
        ]
    
    except Exception as e:
        log.exception("tool_failed", error=str(e))
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "status": "failed"
                }, indent=2)
            )
        ]

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logger.info("shutdown_signal_received", signal=signum)
    shutdown_event.set()

async def main():
    """Main entry point with graceful shutdown"""
    global orchestrator, llm_client
    
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    import os
    logger.info("hypercog_mcp_starting", 
                env_file_exists=env_path.exists(),
                env_file_path=str(env_path))
    
    try:
        # Verify required environment variables
        required_vars = ["OPENAI_API_KEY"]
        optional_vars = ["PERPLEXITY_API_KEY", "GOOGLE_API_KEY"]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        
        if missing:
            logger.error("missing_required_env_vars", missing=missing)
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        if missing_optional:
            logger.warning("missing_optional_env_vars", 
                          missing=missing_optional,
                          note="Some features may be disabled")
        
        logger.info("environment_validated",
                   required_vars_present=len(required_vars),
                   optional_vars_present=len(optional_vars) - len(missing_optional))
        
        try:
            setup_cognee()
            logger.info("cognee_initialized")
        except Exception as e:
            logger.warning("cognee_setup_failed", error=str(e))
            logger.info("continuing_without_cognee")
        
        llm_client = LLMClient()
        orchestrator = HyperCogOrchestrator(storage_root, llm_client)
        
        logger.info("hypercog_mcp_ready")
        
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    
    except Exception as e:
        logger.exception("server_startup_failed", error=str(e))
        sys.exit(1)
    
    finally:
        logger.info("hypercog_mcp_shutdown_complete")

if __name__ == "__main__":
    asyncio.run(main())
