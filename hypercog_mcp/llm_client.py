import os
import json
from typing import List, Dict, Any, Optional
import httpx

class LLMClient:
    """Simple LLM client for agent communication"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        response_format: Optional[Dict] = None
    ) -> str:
        """Call OpenAI chat completion API"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            if response_format:
                payload["response_format"] = response_format
            
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
