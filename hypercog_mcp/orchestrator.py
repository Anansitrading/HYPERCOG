import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from .agents.context_extractor import ContextExtractor
from .agents.evaluator import EvaluatorAgent
from .agents.deep_thinking import DeepThinkingAgent
from .agents.consolidator import ConsolidatorAgent
from .agents.optimizer import OptimizerAgent
from .agents.scrum_agent import ScrumAgent
from .sub_agents.perplexity.agent import PerplexitySearchAgent
from .sub_agents.cognee_kg.agent import CogneeKGAgent
from .sub_agents.cognee_vector.agent import CogneeVectorAgent
from .sub_agents.file_search.agent import FileSearchAgent

class HyperCogOrchestrator:
    """Main orchestrator following the corrected HyperCog flow"""
    
    def __init__(self, storage_root: Path, llm_client):
        self.storage_root = storage_root
        self.llm_client = llm_client
        self.max_tokens_per_task = 100000
        
        prompts_dir = Path(__file__).parent / "agents" / "prompts"
        
        self.context_extractor = ContextExtractor(storage_root)
        self.evaluator = EvaluatorAgent(prompts_dir / "evaluator_agent.md", llm_client)
        self.deep_thinker = DeepThinkingAgent(prompts_dir / "deep_thinking_agent.md", llm_client)
        self.consolidator = ConsolidatorAgent(prompts_dir / "consolidator_agent.md", llm_client, storage_root)
        self.optimizer = OptimizerAgent(prompts_dir / "optimizer_agent.md", llm_client, storage_root)
        self.scrum_agent = ScrumAgent(prompts_dir / "scrum_agent.md", llm_client)
        
        self.perplexity = PerplexitySearchAgent()
        self.cognee_kg = CogneeKGAgent()
        self.cognee_vector = CogneeVectorAgent()
        self.file_search = FileSearchAgent()
    
    async def enrich(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main HyperCog enrichment flow following corrected flowchart
        """
        print("\n" + "="*80)
        print("🔥 HyperCog --enrich")
        print("="*80 + "\n")
        
        extraction_result = await self.context_extractor.execute(context)
        session_id = extraction_result["session_id"]
        current_context = extraction_result["metadata"]["session_context"]
        
        evaluation = await self.evaluator.execute({
            "task": task,
            "current_context": current_context,
            "metadata": extraction_result["metadata"]
        })
        
        if evaluation["sufficient"]:
            print("\n✓ Context is sufficient for world-class outcome")
            
            estimated_tokens = self._estimate_tokens(current_context)
            
            if estimated_tokens <= self.max_tokens_per_task:
                print("✓ Context size is manageable")
                optimized = await self.optimizer.execute({
                    "task": task,
                    "context_to_optimize": current_context,
                    "session_id": session_id
                })
                
                return {
                    "status": "ready_for_execution",
                    "session_id": session_id,
                    "optimized_context": optimized,
                    "path": "sufficient_manageable"
                }
            else:
                print("⚠ Context too large - invoking SCRUM breakdown")
                breakdown = await self.scrum_agent.execute({
                    "task": task,
                    "context": current_context,
                    "reason": "Context sufficient but too large for single execution"
                })
                
                subtask_results = await self._execute_subtasks(breakdown["subtasks"], session_id)
                
                return {
                    "status": "subtasks_completed",
                    "session_id": session_id,
                    "subtask_results": subtask_results,
                    "path": "sufficient_too_large_scrum"
                }
        
        else:
            print("\n⚠ Context insufficient - starting ENRICHMENT phase")
            
            thinking_result = await self.deep_thinker.execute({
                "task": task,
                "current_context": current_context,
                "evaluation": evaluation
            })
            
            search_queries = thinking_result["search_queries"]
            
            print("\n🔍 Dispatching sub-agents for research...")
            sub_agent_results = await self._dispatch_sub_agents(search_queries)
            
            print("\n📦 Consolidating results...")
            consolidation = await self.consolidator.execute({
                "task": task,
                "original_context": current_context,
                "sub_agent_results": sub_agent_results
            })
            
            enriched_context = consolidation["enriched_context"]
            estimated_tokens = consolidation.get("estimated_tokens", self._estimate_tokens(enriched_context))
            
            if estimated_tokens <= self.max_tokens_per_task:
                print("✓ Enriched context is manageable")
                optimized = await self.optimizer.execute({
                    "task": task,
                    "context_to_optimize": enriched_context,
                    "session_id": session_id
                })
                
                return {
                    "status": "ready_for_execution",
                    "session_id": session_id,
                    "optimized_context": optimized,
                    "path": "enriched_manageable"
                }
            else:
                print("⚠ Enriched context too large - invoking SCRUM breakdown")
                breakdown = await self.scrum_agent.execute({
                    "task": task,
                    "context": enriched_context,
                    "reason": "Enriched context too large for single execution"
                })
                
                subtask_results = await self._execute_subtasks(breakdown["subtasks"], session_id)
                
                return {
                    "status": "subtasks_completed",
                    "session_id": session_id,
                    "subtask_results": subtask_results,
                    "path": "enriched_too_large_scrum"
                }
    
    async def _dispatch_sub_agents(self, search_queries: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """Dispatch all sub-agents in parallel"""
        
        tasks = []
        
        if search_queries.get("perplexity"):
            tasks.append(("perplexity", self.perplexity.search(search_queries["perplexity"])))
        
        if search_queries.get("file_search"):
            tasks.append(("file_search", self.file_search.search(search_queries["file_search"])))
        
        if search_queries.get("cognee_kg"):
            tasks.append(("cognee_kg", self.cognee_kg.search(search_queries["cognee_kg"])))
        
        if search_queries.get("cognee_vector"):
            tasks.append(("cognee_vector", self.cognee_vector.search(search_queries["cognee_vector"])))
        
        results = {}
        completed = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        for i, (name, _) in enumerate(tasks):
            if isinstance(completed[i], Exception):
                print(f"[ERROR] {name} failed: {completed[i]}")
                results[name] = []
            else:
                results[name] = completed[i]
        
        return results
    
    async def _execute_subtasks(self, subtasks: List[Dict], session_id: str) -> List[Dict]:
        """Execute subtasks, each going through optimization"""
        results = []
        
        for subtask in subtasks:
            print(f"\n📋 Executing subtask: {subtask['name']}")
            
            optimized = await self.optimizer.execute({
                "task": subtask["description"],
                "context_to_optimize": subtask["context"],
                "session_id": f"{session_id}_subtask_{subtask['id']}"
            })
            
            results.append({
                "subtask_id": subtask["id"],
                "subtask_name": subtask["name"],
                "optimized_context": optimized,
                "status": "ready_for_execution"
            })
        
        return results
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)"""
        return len(text) // 4
