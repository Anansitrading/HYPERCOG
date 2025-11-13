#!/usr/bin/env python3
"""
Quick diagnostic script to test MCP server environment setup
Run this to verify your .env is loading correctly before starting the MCP server
"""

from pathlib import Path
from dotenv import load_dotenv
import os

def test_env_loading():
    """Test environment variable loading"""
    print("=" * 60)
    print("HyperCog MCP Environment Diagnostic")
    print("=" * 60)
    
    # Find .env file
    env_path = Path(__file__).parent / ".env"
    print(f"\n1. Checking .env file...")
    print(f"   Path: {env_path}")
    print(f"   Exists: {env_path.exists()}")
    
    if not env_path.exists():
        print("\n❌ ERROR: .env file not found!")
        print("   Create .env from .env.example:")
        print("   cp .env.example .env")
        return False
    
    # Load environment
    print(f"\n2. Loading environment variables...")
    load_dotenv(env_path, override=True)
    print("   ✓ Loaded")
    
    # Check required variables
    print(f"\n3. Checking REQUIRED variables...")
    required = {
        "OPENAI_API_KEY": "OpenAI API access"
    }
    
    all_present = True
    for var, description in required.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   ✓ {var}: {masked} ({description})")
        else:
            print(f"   ❌ {var}: MISSING ({description})")
            all_present = False
    
    # Check optional variables
    print(f"\n4. Checking OPTIONAL variables...")
    optional = {
        "PERPLEXITY_API_KEY": "Enhanced evaluator validation",
        "GOOGLE_API_KEY": "Google services",
    }
    
    optional_present = []
    for var, description in optional.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   ✓ {var}: {masked} ({description})")
            optional_present.append(var)
        else:
            print(f"   ⚠ {var}: Missing - {description} disabled")
    
    # Check configuration
    print(f"\n5. Checking configuration variables...")
    config = {
        "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-4"),
        "MAX_TOKENS_PER_TASK": os.getenv("MAX_TOKENS_PER_TASK", "100000"),
        "ENABLE_PERPLEXITY_VALIDATION": os.getenv("ENABLE_PERPLEXITY_VALIDATION", "true"),
    }
    
    for var, value in config.items():
        print(f"   • {var}: {value}")
    
    # Summary
    print(f"\n" + "=" * 60)
    if all_present:
        print("✅ MCP SERVER READY TO START")
        print(f"   Required variables: ALL PRESENT")
        print(f"   Optional variables: {len(optional_present)}/{len(optional)} present")
        if len(optional_present) < len(optional):
            print(f"   Note: Some features will be disabled")
        print("\n   You can now restart Windsurf/Amp to reload the MCP server")
    else:
        print("❌ MCP SERVER CANNOT START")
        print("   Missing required variables - add them to .env file")
        print("\n   Edit .env and add missing keys, then run this test again")
    print("=" * 60)
    
    return all_present

if __name__ == "__main__":
    success = test_env_loading()
    exit(0 if success else 1)
