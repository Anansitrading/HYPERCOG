import os
from pathlib import Path
from cognee import config
import cognee_community_hybrid_adapter_falkor.register

def setup_cognee():
    """Configure Cognee with FalkorDB for hybrid graph+vector storage"""
    
    system_root = Path(__file__).parent.parent / ".cognee_system"
    data_root = Path(__file__).parent.parent / ".cognee_data"
    
    system_root.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)
    
    config.system_root_directory(str(system_root))
    config.data_root_directory(str(data_root))
    
    config.set_relational_db_config({
        "db_provider": "sqlite",
    })
    
    config.set_graph_db_config({
        "graph_database_provider": "falkordb",
        "graph_database_url": os.getenv("GRAPH_DB_URL", "localhost"),
        "graph_database_port": int(os.getenv("GRAPH_DB_PORT", "6379")),
    })
    
    config.set_vector_db_config({
        "vector_db_provider": "falkordb",
        "vector_db_url": os.getenv("VECTOR_DB_URL", "localhost"),
        "vector_db_port": int(os.getenv("VECTOR_DB_PORT", "6379")),
    })
    
    config.set_llm_config({
        "llm_provider": "openai",
        "llm_model": os.getenv("LLM_MODEL", "gpt-4"),
        "llm_api_key": os.getenv("OPENAI_API_KEY"),
        "llm_temperature": 0.7
    })
    
    print("✓ Cognee configured with FalkorDB")
    return config
