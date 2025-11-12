import asyncio
from typing import List, Dict, Any
from cognee import search, SearchType

class CogneeKGAgent:
    """Cognee Knowledge Graph search sub-agent"""
    
    def __init__(self):
        self.name = "CogneeKGAgent"
    
    async def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute knowledge graph searches"""
        print(f"[{self.name}] Executing {len(queries)} KG searches...")
        
        results = []
        
        for query in queries:
            try:
                result = await search(
                    query_type=SearchType.GRAPH_COMPLETION,
                    query_text=query
                )
                
                results.append({
                    "query": query,
                    "result": result,
                    "source": "cognee_kg",
                    "success": True
                })
            except Exception as e:
                print(f"[{self.name}] Error searching '{query}': {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "source": "cognee_kg",
                    "success": False
                })
        
        print(f"[{self.name}] Completed {len([r for r in results if r['success']])}/{len(queries)} searches")
        return results
