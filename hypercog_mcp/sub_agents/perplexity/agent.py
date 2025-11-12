import os
import asyncio
from typing import List, Dict, Any
from pathlib import Path

class PerplexitySearchAgent:
    """Perplexity search sub-agent for web research"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY required")
        
        self.name = "PerplexitySearchAgent"
    
    async def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute Perplexity searches"""
        print(f"[{self.name}] Executing {len(queries)} searches...")
        
        results = []
        
        for query in queries:
            try:
                result = await self._execute_search(query)
                results.append({
                    "query": query,
                    "result": result,
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
    
    async def _execute_search(self, query: str) -> str:
        """Execute single Perplexity search via MCP"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a research assistant. Provide accurate, well-sourced information."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
