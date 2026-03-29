import pandas as pd
import sys
import os

# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.neo4j_driver import vector_store

def vector_search(query: str, k: int = 1):
    """Finds the closest O*NET occupation using Vector similarity."""
    res = vector_store.similarity_search(query, k=k)
    if res:
        meta = res[0].metadata
        return {
            "title": meta.get("title"),
            "code": meta.get("code"),
            "description": res[0].page_content
        }
    return None
