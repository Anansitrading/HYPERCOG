import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from .base_agent import BaseAgent

class DeepThinkingAgent(BaseAgent):
    """Deep Thinking Agent using Hermeneutic Circle methodology"""
    
    def __init__(self, prompt_file: Path, llm_client):
        super().__init__("DeepThinkingAgent", prompt_file)
        self.llm_client = llm_client
        self.max_iterations = 3
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use hermeneutic circle to identify knowledge gaps
        
        Args:
            context: {
                "task": str,
                "current_context": str,
                "evaluation": Dict (from evaluator)
            }
        
        Returns:
            {
                "iterations": List[Dict],
                "final_gaps": Dict,
                "search_queries": Dict
            }
        """
        self.log("Starting Deep Thinking with Hermeneutic Circle...")
        
        iterations = []
        current_understanding = context.get("current_context", "")
        
        for i in range(1, self.max_iterations + 1):
            self.log(f"Iteration {i}/{self.max_iterations}")
            
            iteration_result = await self._hermeneutic_iteration(
                iteration_num=i,
                task=context.get("task", ""),
                current_understanding=current_understanding,
                previous_iterations=iterations,
                evaluation=context.get("evaluation", {})
            )
            
            iterations.append(iteration_result)
            current_understanding = iteration_result.get("refined_understanding", current_understanding)
        
        final_gaps = await self._synthesize_gaps(iterations)
        search_queries = await self._craft_search_queries(final_gaps, context)
        
        self.log("Deep Thinking complete")
        
        return {
            "iterations": iterations,
            "final_gaps": final_gaps,
            "search_queries": search_queries
        }
    
    async def _hermeneutic_iteration(
        self,
        iteration_num: int,
        task: str,
        current_understanding: str,
        previous_iterations: List[Dict],
        evaluation: Dict
    ) -> Dict[str, Any]:
        """Single iteration of hermeneutic circle"""
        
        prompt = self._build_iteration_prompt(
            iteration_num, task, current_understanding, previous_iterations, evaluation
        )
        
        response = await self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {
                "iteration": iteration_num,
                "understanding": "Failed to parse",
                "gaps_identified": [],
                "refined_understanding": current_understanding
            }
        
        return result
    
    def _build_iteration_prompt(
        self,
        iteration_num: int,
        task: str,
        current_understanding: str,
        previous_iterations: List[Dict],
        evaluation: Dict
    ) -> str:
        """Build prompt for hermeneutic iteration"""
        
        previous_context = ""
        if previous_iterations:
            previous_context = f"\nPREVIOUS ITERATIONS:\n{json.dumps(previous_iterations, indent=2)}\n"
        
        return f"""HERMENEUTIC CIRCLE ITERATION {iteration_num}/3

TASK:
{task}

CURRENT UNDERSTANDING (WHOLE):
{current_understanding}

EVALUATION FEEDBACK:
{json.dumps(evaluation, indent=2)}
{previous_context}

Instructions for Iteration {iteration_num}:
{'- Initial examination: Identify obvious gaps and surface-level relationships' if iteration_num == 1 else ''}
{'- Deeper analysis: Re-examine gaps in context of the whole, find hidden dependencies' if iteration_num == 2 else ''}
{'- Synthesis: Final refinement, prioritize gaps by criticality' if iteration_num == 3 else ''}

Return JSON with:
- iteration: {iteration_num}
- understanding: "your updated understanding"
- gaps_identified: ["gap1", "gap2", ...]
- refined_understanding: "synthesized whole understanding"
"""
    
    async def _synthesize_gaps(self, iterations: List[Dict]) -> Dict[str, List[str]]:
        """Synthesize final knowledge gaps from all iterations"""
        
        all_gaps = []
        for iteration in iterations:
            all_gaps.extend(iteration.get("gaps_identified", []))
        
        unique_gaps = list(set(all_gaps))
        
        critical = [g for g in unique_gaps if any(
            word in g.lower() for word in ["must", "required", "critical", "essential"]
        )]
        
        important = [g for g in unique_gaps if g not in critical and any(
            word in g.lower() for word in ["should", "important", "necessary"]
        )]
        
        supplementary = [g for g in unique_gaps if g not in critical and g not in important]
        
        return {
            "critical": critical,
            "important": important,
            "supplementary": supplementary
        }
    
    async def _craft_search_queries(self, gaps: Dict[str, List[str]], context: Dict) -> Dict[str, List[str]]:
        """Craft targeted search queries for each sub-agent"""
        
        task = context.get("task", "")
        
        queries = {
            "perplexity": [],
            "file_search": [],
            "cognee_kg": [],
            "cognee_vector": []
        }
        
        for gap in gaps.get("critical", []) + gaps.get("important", []):
            queries["perplexity"].append(f"{task}: {gap}")
            queries["cognee_vector"].append(gap)
            
            if "how" in gap.lower() or "what" in gap.lower():
                queries["cognee_kg"].append(gap)
            
            if "documentation" in gap.lower() or "api" in gap.lower():
                queries["file_search"].append(gap)
        
        return queries
