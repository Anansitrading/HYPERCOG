import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent

class ContextExtractor(BaseAgent):
    """Extracts session context and saves to prompt_store/"""
    
    def __init__(self, storage_root: Path):
        super().__init__("ContextExtractor")
        self.storage_root = storage_root
        self.prompt_store = storage_root / "prompt_store"
        self.prompt_store.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and store session context
        
        Args:
            context: {
                "session_context": str,
                "attached_files": List[Dict],
                "workspace_path": Optional[str],
                "user_intent": Optional[str]
            }
        """
        self.log("Extracting session context...")
        
        session_id = context.get("session_id", datetime.now().strftime("%Y%m%d_%H%M%S"))
        
        extraction_result = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "session_context": context.get("session_context", ""),
            "attached_files": await self._process_attached_files(
                context.get("attached_files", [])
            ),
            "workspace_context": await self._extract_workspace_context(
                context.get("workspace_path")
            ),
            "intent_analysis": await self._analyze_intent(
                context.get("session_context", ""),
                context.get("user_intent")
            )
        }
        
        context_file = self.prompt_store / f"{session_id}_context.json"
        context_file.write_text(json.dumps(extraction_result, indent=2))
        
        self.log(f"Context extracted and saved to {context_file}")
        
        return {
            "session_id": session_id,
            "context_file": str(context_file),
            "metadata": extraction_result
        }
    
    async def _process_attached_files(self, files: List[Dict]) -> List[Dict]:
        """Process attached files and extract their content"""
        processed = []
        
        for file_info in files:
            file_path = Path(file_info.get("path", ""))
            
            if file_path.exists():
                processed.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix,
                    "content": file_path.read_text() if file_path.suffix in [".md", ".txt", ".py", ".js", ".json"] else None
                })
        
        return processed
    
    async def _extract_workspace_context(self, workspace_path: Optional[str]) -> Dict[str, Any]:
        """Extract relevant workspace context"""
        if not workspace_path:
            return {}
        
        workspace = Path(workspace_path)
        if not workspace.exists():
            return {}
        
        return {
            "path": str(workspace),
            "name": workspace.name,
            "structure": await self._get_directory_structure(workspace)
        }
    
    async def _get_directory_structure(self, path: Path, max_depth: int = 2) -> Dict:
        """Get directory structure up to max_depth"""
        if max_depth == 0:
            return {}
        
        structure = {}
        try:
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    structure[item.name] = await self._get_directory_structure(item, max_depth - 1)
                elif item.is_file():
                    structure[item.name] = "file"
        except PermissionError:
            pass
        
        return structure
    
    async def _analyze_intent(self, session_context: str, user_intent: Optional[str]) -> Dict[str, Any]:
        """Analyze user intent from context"""
        return {
            "explicit_intent": user_intent,
            "inferred_type": self._infer_task_type(session_context),
            "complexity": self._estimate_complexity(session_context)
        }
    
    def _infer_task_type(self, context: str) -> str:
        """Simple intent classification"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["implement", "create", "build", "develop"]):
            return "implementation"
        elif any(word in context_lower for word in ["fix", "debug", "error", "issue"]):
            return "debugging"
        elif any(word in context_lower for word in ["refactor", "improve", "optimize"]):
            return "refactoring"
        elif any(word in context_lower for word in ["explain", "understand", "how does"]):
            return "explanation"
        else:
            return "general"
    
    def _estimate_complexity(self, context: str) -> str:
        """Estimate task complexity"""
        word_count = len(context.split())
        
        if word_count < 50:
            return "low"
        elif word_count < 200:
            return "medium"
        else:
            return "high"
