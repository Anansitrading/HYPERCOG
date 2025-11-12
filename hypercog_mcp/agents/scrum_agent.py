import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from .base_agent import BaseAgent

class ScrumAgent(BaseAgent):
    """Breaks down large contexts into manageable subtasks"""
    
    def __init__(self, prompt_file: Path, llm_client):
        super().__init__("ScrumAgent", prompt_file)
        self.llm_client = llm_client
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Break down task into subtasks
        
        Args:
            context: {
                "task": str,
                "context": str,
                "reason": str (why breakdown needed)
            }
        
        Returns:
            {
                "subtasks": List[Dict],
                "execution_strategy": str,
                "integration_plan": str
            }
        """
        self.log("Breaking down task into subtasks...")
        
        breakdown_prompt = self._build_breakdown_prompt(context)
        
        response = await self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": breakdown_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            self.log("Failed to parse breakdown response", "ERROR")
            result = {
                "subtasks": [{
                    "id": "subtask_1",
                    "name": context.get("task", "Task"),
                    "description": context.get("task", ""),
                    "context": context.get("context", ""),
                    "dependencies": [],
                    "execution_order": 1,
                    "success_criteria": "Complete the task"
                }],
                "execution_strategy": "sequential",
                "integration_plan": "N/A"
            }
        
        self.log(f"Created {len(result.get('subtasks', []))} subtasks")
        
        return result
    
    def _build_breakdown_prompt(self, context: Dict[str, Any]) -> str:
        """Build task breakdown prompt"""
        return f"""TASK BREAKDOWN REQUIRED

REASON: {context.get('reason', 'Context too large')}

ORIGINAL TASK:
{context.get('task', '')}

FULL CONTEXT:
{context.get('context', '')}

Break this down into logical, independently executable subtasks.

GUIDELINES:
1. Each subtask should be self-contained
2. Minimize inter-subtask dependencies
3. Allocate only necessary context to each subtask
4. Don't over-fragment - maintain cohesion
5. Remember: Each subtask will be optimized independently

Return JSON with:
- subtasks: [{id, name, description, context, dependencies, execution_order, success_criteria}]
- execution_strategy: "sequential" | "parallel" | "mixed"
- integration_plan: "how to combine subtask results"
"""
