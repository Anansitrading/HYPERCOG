import asyncio
from typing import List, Dict, Any
from cognee import search, SearchType

class CogneeVectorAgent:
    """Cognee Vector search sub-agent for semantic similarity"""
    
    def __init__(self):
        self.name = "CogneeVectorAgent"
    
    async def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute vector similarity searches"""
        print(f"[{self.name}] Executing {len(queries)} vector searches...")
        
        results = []
        
        for query in queries:
            try:
                result = await search(
                    query_type=SearchType.SIMILARITY,
                    query_text=query
                )
                
                results.append({
                    "query": query,
                    "result": result,
                    "source": "cognee_vector",
                    "success": True
                })
            except Exception as e:
                print(f"[{self.name}] Error searching '{query}': {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "source": "cognee_vector",
                    "success": False
                })
        
        print(f"[{self.name}] Completed {len([r for r in results if r['success']])}/{len(queries)} searches")
        return results
