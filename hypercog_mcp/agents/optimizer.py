import json
import asyncio
from pathlib import Path
from typing import Dict, Any
from .base_agent import BaseAgent

class OptimizerAgent(BaseAgent):
    """MANDATORY context optimizer - ALL execution paths flow through here"""
    
    def __init__(self, prompt_file: Path, llm_client, storage_root: Path):
        super().__init__("OptimizerAgent", prompt_file)
        self.llm_client = llm_client
        self.optimized_folder = storage_root / "optimized"
        self.optimized_folder.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        MANDATORY optimization of context before execution
        
        Args:
            context: {
                "task": str,
                "context_to_optimize": str,
                "session_id": str
            }
        
        Returns:
            {
                "optimized_context": {
                    "zone_1_task": str,
                    "zone_2_core": str,
                    "zone_3_supporting": str,
                    "zone_4_gotchas": str
                },
                "token_count": Dict,
                "optimizations_applied": List[str]
            }
        """
        self.log("🎯 MANDATORY OPTIMIZATION - Optimizing context...")
        
        optimization_prompt = self._build_optimization_prompt(context)
        
        response = await self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": optimization_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            self.log("Failed to parse optimization response", "ERROR")
            result = {
                "optimized_context": {
                    "zone_1_task": context.get("task", ""),
                    "zone_2_core": context.get("context_to_optimize", ""),
                    "zone_3_supporting": "",
                    "zone_4_gotchas": ""
                },
                "token_count": {"original": 0, "optimized": 0, "reduction_percent": 0},
                "optimizations_applied": []
            }
        
        await self._save_optimized_context(context.get("session_id", "unknown"), result)
        
        reduction = result.get("token_count", {}).get("reduction_percent", 0)
        self.log(f"✓ Optimization complete: {reduction}% token reduction")
        
        return result
    
    def _build_optimization_prompt(self, context: Dict[str, Any]) -> str:
        """Build optimization prompt"""
        return f"""MANDATORY CONTEXT OPTIMIZATION

TASK:
{context.get('task', '')}

CONTEXT TO OPTIMIZE:
{context.get('context_to_optimize', '')}

Your role is CRITICAL: Optimize this context for optimal LLM performance.

REQUIREMENTS:
1. Zone Placement:
   - Zone 1 (Start): Clear task definition, user intent, success criteria
   - Zone 2 (Middle-Early): Essential technical info, key dependencies
   - Zone 3 (Middle-Late): Supporting/background information
   - Zone 4 (END - MOST CURRENT TOKENS): ⚠️ CRITICAL GOTCHAS

2. Critical Gotchas → Most Current Tokens:
   Place ALL edge cases, warnings, pitfalls, security notes at the END
   These are seen last = highest attention weight

3. Token Compression:
   - Aggressive deduplication
   - Summarize verbose sections
   - Preserve technical precision
   - Keep ALL critical details

4. Priority Ordering:
   - Rank by impact on outcome quality
   - Weight recent info higher
   - Dependencies before dependents

Return JSON with: optimized_context (4 zones), token_count (original, optimized, reduction_percent), optimizations_applied
"""
    
    async def _save_optimized_context(self, session_id: str, result: Dict[str, Any]):
        """Save optimized context to file"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.optimized_folder / f"{session_id}_{timestamp}_optimized.json"
        
        file_path.write_text(json.dumps(result, indent=2))
        self.log(f"Saved optimized context to {file_path}")
