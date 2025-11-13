import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

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
from .utils.token_counter import TokenCounter

logger = structlog.get_logger()

class HyperCogOrchestrator:
    """Main orchestrator following the corrected HyperCog flow"""
    
    def __init__(self, storage_root: Path, llm_client, max_tokens: int = 100000, max_concurrency: int = 10):
        self.storage_root = storage_root
        self.llm_client = llm_client
        self.max_tokens_per_task = max_tokens
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.token_counter = TokenCounter()
        
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
    
    async def enrich(self, task: str, context: Dict[str, Any], timeout: float = 300.0) -> Dict[str, Any]:
        """
        Main HyperCog enrichment flow following corrected flowchart
        
        Args:
            task: Task description
            context: Session context dictionary
            timeout: Maximum seconds for enrichment (default 5 minutes)
            
        Returns:
            Dictionary with status and optimized context
            
        Raises:
            asyncio.TimeoutError: If enrichment exceeds timeout
            ValueError: If inputs are invalid
        """
        log = logger.bind(task=task[:50])
        log.info("hypercog_enrich_started")
        
        try:
            async with asyncio.timeout(timeout):
                return await self._enrich_internal(task, context, log)
        except asyncio.TimeoutError:
            log.error("enrichment_timeout", timeout=timeout)
            raise
        except Exception as e:
            log.exception("enrichment_failed", error=str(e))
            raise
    
    async def _enrich_internal(self, task: str, context: Dict[str, Any], log) -> Dict[str, Any]:
        """Internal enrichment logic"""
        
        extraction_result = await self.context_extractor.execute(context)
        session_id = extraction_result["session_id"]
        current_context = extraction_result["metadata"]["session_context"]
        
        log = log.bind(session_id=session_id)
        
        # Run enhanced evaluation with Perplexity validation
        evaluation = await self._run_evaluator_with_perplexity(
            extraction_result,
            task,
            current_context
        )
        
        if evaluation["sufficient"]:
            log.info("context_sufficient", confidence=evaluation.get("confidence"))
            
            estimated_tokens = self.token_counter.count_tokens(current_context)
            
            if estimated_tokens <= self.max_tokens_per_task:
                log.info("context_manageable", tokens=estimated_tokens)
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
                log.warning("context_too_large", tokens=estimated_tokens, max_tokens=self.max_tokens_per_task)
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
            log.info("context_insufficient_enriching", missing_areas=evaluation.get("missing_areas", []))
            
            thinking_result = await self.deep_thinker.execute({
                "task": task,
                "current_context": current_context,
                "evaluation": evaluation
            })
            
            search_queries = thinking_result["search_queries"]
            
            log.info("dispatching_sub_agents", query_counts={k: len(v) for k, v in search_queries.items()})
            sub_agent_results = await self._dispatch_sub_agents(search_queries)
            
            log.info("consolidating_results")
            consolidation = await self.consolidator.execute({
                "task": task,
                "original_context": current_context,
                "sub_agent_results": sub_agent_results
            })
            
            enriched_context = consolidation["enriched_context"]
            estimated_tokens = consolidation.get("estimated_tokens", self.token_counter.count_tokens(enriched_context))
            
            if estimated_tokens <= self.max_tokens_per_task:
                log.info("enriched_context_manageable", tokens=estimated_tokens)
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
                log.warning("enriched_context_too_large", tokens=estimated_tokens)
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
        """
        Dispatch all sub-agents in parallel with concurrency control
        
        Args:
            search_queries: Dict mapping agent names to query lists
            
        Returns:
            Dict mapping agent names to results (empty list on failure)
        """
        log = logger.bind()
        tasks = []
        
        if search_queries.get("perplexity"):
            tasks.append(("perplexity", self._run_with_semaphore(
                self.perplexity.search(search_queries["perplexity"])
            )))
        
        if search_queries.get("file_search"):
            tasks.append(("file_search", self._run_with_semaphore(
                self.file_search.search(search_queries["file_search"])
            )))
        
        if search_queries.get("cognee_kg"):
            tasks.append(("cognee_kg", self._run_with_semaphore(
                self.cognee_kg.search(search_queries["cognee_kg"])
            )))
        
        if search_queries.get("cognee_vector"):
            tasks.append(("cognee_vector", self._run_with_semaphore(
                self.cognee_vector.search(search_queries["cognee_vector"])
            )))
        
        results = {}
        completed = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        for i, (name, _) in enumerate(tasks):
            if isinstance(completed[i], Exception):
                log.error("sub_agent_failed", agent=name, error=str(completed[i]))
                results[name] = []
            else:
                results[name] = completed[i]
                log.info("sub_agent_success", agent=name, result_count=len(completed[i]))
        
        return results
    
    async def _run_with_semaphore(self, coro):
        """Run coroutine with semaphore for concurrency control"""
        async with self.semaphore:
            return await coro
    
    async def _execute_subtasks(self, subtasks: List[Dict], session_id: str) -> List[Dict]:
        """
        Execute subtasks, each going through optimization
        
        Args:
            subtasks: List of subtask dictionaries
            session_id: Parent session ID
            
        Returns:
            List of results with optimized contexts
        """
        log = logger.bind(session_id=session_id, subtask_count=len(subtasks))
        log.info("executing_subtasks")
        
        results = []
        
        for subtask in subtasks:
            log.info("executing_subtask", subtask_id=subtask['id'], name=subtask['name'])
            
            try:
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
                
            except Exception as e:
                log.error("subtask_failed", subtask_id=subtask['id'], error=str(e))
                results.append({
                    "subtask_id": subtask["id"],
                    "subtask_name": subtask["name"],
                    "error": str(e),
                    "status": "failed"
                })
        
        return results
    
    async def _run_evaluator_with_perplexity(
        self,
        extraction_result: Dict[str, Any],
        task: str,
        current_context: str
    ) -> Dict[str, Any]:
        """
        Run evaluator with enhanced Perplexity validation enabled.
        
        Args:
            extraction_result: Result from context extraction
            task: User's task/prompt
            current_context: Extracted session context
            
        Returns:
            Enhanced evaluation result with external validation
        """
        enable_perplexity = os.getenv("ENABLE_PERPLEXITY_VALIDATION", "true").lower() == "true"
        
        evaluation = await self.evaluator.evaluate(
            session_context=current_context,
            attached_files=extraction_result.get("attached_files", []),
            workspace_info=extraction_result.get("workspace_info"),
            user_intent=task,
            current_prompt=task,
            enable_perplexity=enable_perplexity
        )
        
        logger.info(
            "evaluation_complete",
            sufficient=evaluation["sufficient"],
            confidence=evaluation.get("confidence", 0),
            external_validation="enabled" if enable_perplexity else "disabled",
            has_perplexity_sources=bool(evaluation.get("perplexity_sources"))
        )
        
        return evaluation
