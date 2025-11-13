import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..sub_agents.perplexity.agent import PerplexityAgent

class EvaluatorAgent(BaseAgent):
    """
    Enhanced Evaluator Agent with real-time Perplexity validation.
    Assesses context sufficiency against world-class standards using external verification.
    """
    
    def __init__(self, prompt_file: Path, llm_client):
        super().__init__("EvaluatorAgent", prompt_file)
        self.llm_client = llm_client
        self.perplexity_agent = None
        self.validation_cache = {}
        
    def _init_perplexity(self):
        """Lazy initialization of Perplexity agent"""
        if self.perplexity_agent is None:
            try:
                import warnings
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    self.perplexity_agent = PerplexityAgent()
                    if w:
                        for warning in w:
                            self.log(f"Perplexity warning: {warning.message}", "WARNING")
            except Exception as e:
                self.log(f"Perplexity agent unavailable: {e}", "WARNING")
                self.perplexity_agent = None
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy execute method for backward compatibility.
        """
        return await self.evaluate(
            session_context=context.get('current_context', ''),
            attached_files=[],
            workspace_info=context.get('metadata'),
            user_intent=context.get('task', ''),
            current_prompt=context.get('task', ''),
            enable_perplexity=True
        )
    
    async def evaluate(
        self,
        session_context: str,
        attached_files: List[Dict[str, Any]],
        workspace_info: Optional[Dict[str, Any]],
        user_intent: str,
        current_prompt: str,
        enable_perplexity: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate context sufficiency with optional Perplexity validation.
        
        Args:
            session_context: Raw conversation history
            attached_files: List of file metadata
            workspace_info: Directory structure and file contents
            user_intent: Classified user intent
            current_prompt: Current user query
            enable_perplexity: Whether to use Perplexity for validation
        
        Returns:
            Enhanced evaluation with external validation data
        """
        
        self.log("Starting context evaluation...")
        
        # Step 1: Initial Static Assessment
        initial_assessment = await self._perform_static_assessment(
            session_context,
            attached_files,
            workspace_info,
            user_intent,
            current_prompt
        )
        
        # Step 2: Perplexity-Enhanced Validation (if enabled)
        if enable_perplexity:
            self._init_perplexity()
            
            if self.perplexity_agent:
                try:
                    perplexity_validations = await self._validate_with_perplexity(
                        initial_assessment,
                        session_context,
                        user_intent,
                        current_prompt
                    )
                    
                    # Step 3: Synthesize Final Assessment
                    enhanced_assessment = await self._synthesize_assessment(
                        initial_assessment,
                        perplexity_validations
                    )
                    
                    self.log(f"Enhanced evaluation complete: sufficient={enhanced_assessment['sufficient']}, confidence={enhanced_assessment['confidence']:.2f}")
                    return enhanced_assessment
                    
                except Exception as e:
                    self.log(f"Perplexity validation failed: {e}, falling back to static assessment", "WARNING")
        
        self.log(f"Static evaluation complete: sufficient={initial_assessment['sufficient']}, confidence={initial_assessment['confidence']:.2f}")
        return initial_assessment
    
    async def _perform_static_assessment(
        self,
        session_context: str,
        attached_files: List[Dict[str, Any]],
        workspace_info: Optional[Dict[str, Any]],
        user_intent: str,
        current_prompt: str
    ) -> Dict[str, Any]:
        """Perform initial assessment using only extracted context."""
        
        context = {
            "session_context": session_context,
            "attached_files": attached_files,
            "workspace_info": workspace_info,
            "user_intent": user_intent,
            "current_prompt": current_prompt
        }
        
        evaluation_request = self._format_evaluation_request(context)
        
        response = await self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": evaluation_request}
            ],
            response_format={"type": "json_object"}
        )
        
        return self._parse_evaluation_response(response)
    
    async def _validate_with_perplexity(
        self,
        initial_assessment: Dict[str, Any],
        session_context: str,
        user_intent: str,
        current_prompt: str
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Call Perplexity sub-agent to validate each assessment criterion.
        
        Returns validation results organized by criterion.
        """
        
        validation_tasks = []
        task_names = []
        
        # 1. Completeness Validation
        if initial_assessment.get("missing_elements") or initial_assessment.get("missing_areas"):
            validation_tasks.append(
                self._validate_completeness(
                    current_prompt,
                    user_intent,
                    initial_assessment.get("missing_elements", initial_assessment.get("missing_areas", []))
                )
            )
            task_names.append("completeness")
        
        # 2. Accuracy Validation
        technical_claims = self._extract_technical_claims(session_context)
        if technical_claims:
            validation_tasks.append(
                self._validate_accuracy(technical_claims)
            )
            task_names.append("accuracy")
        
        # 3. Relevance Validation (Domain-Specific)
        domain = self._extract_domain(user_intent, current_prompt)
        if domain:
            validation_tasks.append(
                self._validate_relevance(domain, current_prompt)
            )
            task_names.append("relevance")
        
        # 4. Depth Validation (for complex tasks)
        complexity = initial_assessment.get("complexity", "medium")
        if complexity in ["high", "expert"]:
            validation_tasks.append(
                self._validate_depth(current_prompt, user_intent)
            )
            task_names.append("depth")
        
        # 5. Gotcha Insights (always check for edge cases)
        validation_tasks.append(
            self._validate_gotchas(current_prompt, user_intent)
        )
        task_names.append("gotchas")
        
        # Execute all validations concurrently
        self.log(f"Running {len(validation_tasks)} Perplexity validations: {', '.join(task_names)}")
        validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Organize results by criterion
        results = {}
        for i, name in enumerate(task_names):
            if i < len(validation_results) and not isinstance(validation_results[i], Exception):
                results[name] = validation_results[i]
            else:
                results[name] = []
                if isinstance(validation_results[i], Exception):
                    self.log(f"Validation error for {name}: {validation_results[i]}", "WARNING")
        
        return results
    
    async def _validate_completeness(
        self,
        task: str,
        intent: str,
        missing_elements: List[str]
    ) -> List[Dict[str, str]]:
        """Validate what information is actually needed for the task."""
        
        query = f"What information and context is required to successfully {intent} for: {task}"
        
        result = await self.perplexity_agent.search(query)
        
        return [{
            "criterion": "completeness",
            "query": query,
            "findings": result.get("answer", ""),
            "sources": result.get("citations", [])
        }]
    
    async def _validate_accuracy(
        self,
        technical_claims: List[str]
    ) -> List[Dict[str, str]]:
        """Verify technical claims against current best practices."""
        
        validations = []
        
        for claim in technical_claims[:3]:
            cache_key = f"accuracy_{hash(claim)}"
            
            if cache_key in self.validation_cache:
                validations.append(self.validation_cache[cache_key])
                continue
            
            query = f"Verify current best practices and accuracy: {claim}"
            result = await self.perplexity_agent.search(query)
            
            validation = {
                "criterion": "accuracy",
                "claim": claim,
                "query": query,
                "findings": result.get("answer", ""),
                "sources": result.get("citations", [])
            }
            
            self.validation_cache[cache_key] = validation
            validations.append(validation)
        
        return validations
    
    async def _validate_relevance(
        self,
        domain: str,
        task: str
    ) -> List[Dict[str, str]]:
        """Check latest developments and relevance in the domain."""
        
        query = f"Latest developments and current best practices in {domain} for: {task}"
        
        result = await self.perplexity_agent.search(query)
        
        return [{
            "criterion": "relevance",
            "domain": domain,
            "query": query,
            "findings": result.get("answer", ""),
            "sources": result.get("citations", [])
        }]
    
    async def _validate_depth(
        self,
        task: str,
        intent: str
    ) -> List[Dict[str, str]]:
        """Verify deep technical requirements for complex tasks."""
        
        query = f"Deep technical requirements, architecture considerations, and implementation details for {intent}: {task}"
        
        result = await self.perplexity_agent.search(query)
        
        return [{
            "criterion": "depth",
            "query": query,
            "findings": result.get("answer", ""),
            "sources": result.get("citations", [])
        }]
    
    async def _validate_gotchas(
        self,
        task: str,
        intent: str
    ) -> List[Dict[str, str]]:
        """Identify common pitfalls and edge cases."""
        
        query = f"Common pitfalls, edge cases, security concerns, and gotchas when {intent}: {task}"
        
        result = await self.perplexity_agent.search(query)
        
        return [{
            "criterion": "gotchas",
            "query": query,
            "findings": result.get("answer", ""),
            "sources": result.get("citations", [])
        }]
    
    async def _synthesize_assessment(
        self,
        initial_assessment: Dict[str, Any],
        perplexity_validations: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """
        Synthesize final assessment by comparing initial assessment
        with Perplexity validation findings.
        """
        
        synthesis_prompt = f"""You are synthesizing an enhanced context evaluation.

INITIAL ASSESSMENT:
{json.dumps(initial_assessment, indent=2)}

PERPLEXITY VALIDATION FINDINGS:
{json.dumps(perplexity_validations, indent=2)}

Compare the initial assessment against real-time Perplexity findings:
1. Identify gaps revealed by Perplexity that weren't in initial assessment
2. Confirm or refute accuracy claims using Perplexity sources
3. Add newly discovered gotchas and edge cases
4. Adjust confidence score based on external validation
5. Update missing_elements with verified gaps

Return enhanced JSON with fields:
- sufficient (bool)
- confidence (0-1, adjusted based on validation)
- reasoning (synthesized from initial + Perplexity)
- missing_elements (verified list)
- context_size_assessment (unchanged from initial)
- external_validation_summary (new - key Perplexity insights)
- perplexity_sources (new - list of citation URLs)
- validation_confidence (new - 0-1 score of how well Perplexity validated)
"""
        
        response = await self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert evaluator synthesizing assessment results."},
                {"role": "user", "content": synthesis_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return self._parse_evaluation_response(response)
    
    def _extract_technical_claims(self, session_context: str) -> List[str]:
        """Extract technical claims from context that should be verified."""
        claims = []
        
        keywords = ["version", "API", "library", "framework", "method", "function", "uses", "requires"]
        lines = session_context.split("\n")
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                claims.append(line.strip())
        
        return claims[:5]
    
    def _extract_domain(self, intent: str, prompt: str) -> Optional[str]:
        """Extract domain/technology from intent and prompt."""
        domains = {
            "web": ["react", "javascript", "html", "css", "frontend", "web"],
            "ai/ml": ["ai", "machine learning", "llm", "model", "training", "neural"],
            "devops": ["docker", "kubernetes", "deployment", "ci/cd", "infrastructure"],
            "database": ["sql", "database", "postgresql", "mongodb", "redis"],
            "backend": ["api", "server", "backend", "microservice"],
        }
        
        text = (intent + " " + prompt).lower()
        
        for domain, keywords in domains.items():
            if any(kw in text for kw in keywords):
                return domain
        
        return None
    
    def _format_evaluation_request(self, context: Dict[str, Any]) -> str:
        """Format evaluation request for LLM."""
        session_preview = context['session_context'][:2000] if context['session_context'] else "No context"
        
        return f"""Evaluate the following context for sufficiency:

USER INTENT: {context['user_intent']}
CURRENT PROMPT: {context['current_prompt']}

SESSION CONTEXT:
{session_preview}...

ATTACHED FILES: {len(context['attached_files'])} files
WORKSPACE INFO: {'Available' if context['workspace_info'] else 'Not available'}

Assess against world-class standards:
1. Completeness - All necessary information present
2. Accuracy - Information is correct and current
3. Relevance - Context relates to task
4. Depth - Sufficient detail for implementation
5. Gotcha Insights - Critical edge cases identified

Return JSON evaluation with fields: sufficient, confidence, reasoning, missing_elements, context_size_assessment
"""
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM evaluation response into structured format."""
        try:
            result = json.loads(response)
            
            # Ensure required fields exist
            if "sufficient" not in result:
                result["sufficient"] = False
            if "confidence" not in result:
                result["confidence"] = 0.3
            if "reasoning" not in result and "reasons" in result:
                result["reasoning"] = result["reasons"]
            if "missing_elements" not in result and "missing_areas" in result:
                result["missing_elements"] = result["missing_areas"]
            
            return result
            
        except json.JSONDecodeError:
            self.log("Failed to parse evaluation response", "ERROR")
            return {
                "sufficient": False,
                "confidence": 0.3,
                "reasoning": "Failed to parse evaluation response",
                "missing_elements": ["Evaluation parsing error"],
                "context_size_assessment": "unknown"
            }
