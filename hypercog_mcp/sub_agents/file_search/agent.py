import os
import asyncio
from typing import List, Dict, Any
import google.generativeai as genai

class FileSearchAgent:
    """Google Gemini File Search sub-agent"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY required")
        
        genai.configure(api_key=self.api_key)
        self.name = "FileSearchAgent"
    
    async def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute file searches via Gemini"""
        print(f"[{self.name}] Executing {len(queries)} file searches...")
        
        results = []
        
        for query in queries:
            try:
                result = await self._execute_file_search(query)
                results.append({
                    "query": query,
                    "result": result,
                    "source": "file_search",
                    "success": True
                })
            except Exception as e:
                print(f"[{self.name}] Error searching '{query}': {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "source": "file_search",
                    "success": False
                })
        
        print(f"[{self.name}] Completed {len([r for r in results if r['success']])}/{len(queries)} searches")
        return results
    
    async def _execute_file_search(self, query: str) -> str:
        """Execute single file search"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = await asyncio.to_thread(
            model.generate_content,
            f"Search for information about: {query}"
        )
        
        return response.text
