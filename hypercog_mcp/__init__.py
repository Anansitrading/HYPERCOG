"""HyperCog MCP - Advanced context enrichment orchestration"""

__version__ = "0.1.0"

from .orchestrator import HyperCogOrchestrator
from .llm_client import LLMClient

__all__ = ['HyperCogOrchestrator', 'LLMClient']
