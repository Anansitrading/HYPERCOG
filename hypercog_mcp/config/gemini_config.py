import os
import google.generativeai as genai

def setup_gemini_file_search():
    """Configure Google Gemini File Search"""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable required")
    
    genai.configure(api_key=api_key)
    
    store_name = "hypercog-context-store"
    
    print(f"✓ Gemini File Search configured: {store_name}")
    return store_name
