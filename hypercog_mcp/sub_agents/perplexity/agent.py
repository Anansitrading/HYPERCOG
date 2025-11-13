import os
import httpx
from typing import Dict, Any, List

class PerplexityAgent:
    """
    Perplexity API integration for real-time web research and validation.
    """
    
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment")
        
        self.base_url = "https://api.perplexity.ai"
        self.model = "llama-3.1-sonar-large-128k-online"
        self.name = "PerplexityAgent"
    
    async def search(
        self,
        query: str,
        max_tokens: int = 1000,
        temperature: float = 0.2,
        return_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a Perplexity search query and return results with citations.
        
        Args:
            query: Search query
            max_tokens: Maximum response tokens
            temperature: LLM temperature (lower = more factual)
            return_citations: Include source citations
        
        Returns:
            Dict with 'answer' and 'citations' keys
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a precise research assistant. Provide factual, current information with specific details."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "return_citations": return_citations,
                    "return_related_questions": False
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            answer = data["choices"][0]["message"]["content"]
            citations = data.get("citations", [])
            
            return {
                "answer": answer,
                "citations": citations,
                "model": self.model
            }
    
    async def validate_claim(
        self,
        claim: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Validate a specific technical claim against current information.
        
        Args:
            claim: The claim to validate
            context: Additional context for the claim
        
        Returns:
            Validation result with verdict and evidence
        """
        
        query = f"Verify the accuracy and currency of this claim: {claim}"
        if context:
            query += f"\n\nContext: {context}"
        
        result = await self.search(query, max_tokens=500, temperature=0.1)
        
        # Simple verdict extraction
        answer = result["answer"].lower()
        verdict = "verified" if any(word in answer for word in ["correct", "accurate", "true", "yes"]) else "uncertain"
        
        return {
            "claim": claim,
            "verdict": verdict,
            "evidence": result["answer"],
            "sources": result["citations"]
        }


class PerplexitySearchAgent(PerplexityAgent):
    """
    Legacy class name for backward compatibility.
    """
    
    def __init__(self, api_key: str = None):
        super().__init__()
        if api_key:
            self.api_key = api_key
    
    async def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Execute Perplexity searches (legacy interface).
        Supports both single query string and list of queries.
        """
        
        # Handle single query string
        if isinstance(queries, str):
            queries = [queries]
        
        print(f"[{self.name}] Executing {len(queries)} searches...")
        
        results = []
        
        for query in queries:
            try:
                result = await super().search(query)
                results.append({
                    "query": query,
                    "result": result["answer"],
                    "citations": result.get("citations", []),
                    "source": "perplexity",
                    "success": True
                })
            except Exception as e:
                print(f"[{self.name}] Error searching '{query}': {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "source": "perplexity",
                    "success": False
                })
        
        print(f"[{self.name}] Completed {len([r for r in results if r['success']])}/{len(queries)} searches")
        return results
