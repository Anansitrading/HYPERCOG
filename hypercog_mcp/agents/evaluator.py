import json
import asyncio
from pathlib import Path
from typing import Dict, Any
from .base_agent import BaseAgent

class EvaluatorAgent(BaseAgent):
    """Evaluates context sufficiency for world-class outcomes"""
    
    def __init__(self, prompt_file: Path, llm_client):
        super().__init__("EvaluatorAgent", prompt_file)
        self.llm_client = llm_client
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if context is sufficient for world-class outcome
        
        Args:
            context: {
                "task": str,
                "current_context": str,
                "metadata": Dict
            }
        
        Returns:
            {
                "sufficient": bool,
                "confidence": float,
                "reasons": List[str],
                "missing_areas": List[str]
            }
        """
        self.log("Evaluating context sufficiency...")
        
        evaluation_prompt = self._build_evaluation_prompt(context)
        
        response = await self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": evaluation_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            self.log("Failed to parse LLM response as JSON", "ERROR")
            result = {
                "sufficient": False,
                "confidence": 0.0,
                "reasons": ["Evaluation failed"],
                "missing_areas": ["Unknown"]
            }
        
        self.log(f"Evaluation complete: sufficient={result.get('sufficient')}, confidence={result.get('confidence')}")
        
        return result
    
    def _build_evaluation_prompt(self, context: Dict[str, Any]) -> str:
        """Build evaluation prompt"""
        return f"""Evaluate the following context for sufficiency:

TASK:
{context.get('task', 'No task specified')}

CURRENT CONTEXT:
{context.get('current_context', 'No context provided')}

METADATA:
{json.dumps(context.get('metadata', {}), indent=2)}

Assess whether this context is sufficient to produce a WORLD-CLASS outcome.
Be conservative - only return sufficient=true if you are highly confident.

Return JSON with: sufficient, confidence, reasons, missing_areas
"""
