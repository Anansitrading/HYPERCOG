from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
import asyncio

class BaseAgent(ABC):
    """Base class for all HyperCog agents"""
    
    def __init__(self, name: str, prompt_file: Optional[Path] = None):
        self.name = name
        self.prompt_file = prompt_file
        self.system_prompt = self._load_system_prompt() if prompt_file else None
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from markdown file"""
        if self.prompt_file and self.prompt_file.exists():
            return self.prompt_file.read_text()
        return ""
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic"""
        pass
    
    def log(self, message: str, level: str = "INFO"):
        """Simple logging"""
        print(f"[{level}] {self.name}: {message}")
