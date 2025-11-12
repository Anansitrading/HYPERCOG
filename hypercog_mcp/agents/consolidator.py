import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from .base_agent import BaseAgent

class ConsolidatorAgent(BaseAgent):
    """Consolidates results from multiple sub-agents"""
    
    def __init__(self, prompt_file: Path, llm_client, storage_root: Path):
        super().__init__("ConsolidatorAgent", prompt_file)
        self.llm_client = llm_client
        self.rough_folder = storage_root / "rough"
        self.rough_folder.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate sub-agent results
        
        Args:
            context: {
                "task": str,
                "original_context": str,
                "sub_agent_results": {
                    "perplexity": List[Dict],
                    "file_search": List[Dict],
                    "cognee_kg": List[Dict],
                    "cognee_vector": List[Dict]
                }
            }
        
        Returns:
            {
                "enriched_context": str,
                "sources_used": Dict,
                "improvements": List[str],
                "estimated_tokens": int,
                "quality_score": float
            }
        """
        self.log("Consolidating sub-agent results...")
        
        await self._save_to_rough_folder(context.get("sub_agent_results", {}))
        
        consolidation_prompt = self._build_consolidation_prompt(context)
        
        response = await self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": consolidation_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            self.log("Failed to parse consolidation response", "ERROR")
            result = {
                "enriched_context": context.get("original_context", ""),
                "sources_used": {},
                "improvements": [],
                "estimated_tokens": 0,
                "quality_score": 0.0
            }
        
        self.log(f"Consolidation complete, quality_score={result.get('quality_score')}")
        
        return result
    
    async def _save_to_rough_folder(self, results: Dict[str, List[Dict]]):
        """Save raw sub-agent results to rough/ folder"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for source, source_results in results.items():
            if source_results:
                file_path = self.rough_folder / f"{timestamp}_{source}.json"
                file_path.write_text(json.dumps(source_results, indent=2))
                self.log(f"Saved {source} results to {file_path}")
    
    def _build_consolidation_prompt(self, context: Dict[str, Any]) -> str:
        """Build consolidation prompt"""
        
        sub_results = context.get("sub_agent_results", {})
        
        results_text = ""
        for source, results in sub_results.items():
            results_text += f"\n\n=== {source.upper()} RESULTS ===\n"
            for result in results:
                if result.get("success"):
                    results_text += f"\nQuery: {result['query']}\n"
                    results_text += f"Result: {result['result']}\n"
        
        return f"""Consolidate the following research results:

ORIGINAL TASK:
{context.get('task', '')}

ORIGINAL CONTEXT:
{context.get('original_context', '')}

SUB-AGENT RESEARCH RESULTS:
{results_text}

Instructions:
1. Extract ONLY information directly relevant to the task
2. Deduplicate and normalize findings
3. Merge with original context coherently
4. Ensure significant improvement over original
5. Track sources for attribution
6. Estimate token count of enriched context

Return JSON with: enriched_context, sources_used, improvements, estimated_tokens, quality_score, conflicts (if any)
"""
