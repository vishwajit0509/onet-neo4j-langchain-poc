# src/retrieval/graph_retriever.py

import pandas as pd
import sys
import os

# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.database.neo4j_driver import graph_db, vector_store

from src.utils.llms import llm
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain

# 1. Built-in Text2Cypher (from Cell 4)
# Useful for general exploration, though Angel 3 uses custom Cypher for accuracy.
cypher_qa = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph_db,
    verbose=True,
    allow_dangerous_requests=True
)

def simple_vector_search(query: str):
    """Locator Tool: Finds the exact O*NET match for a job title."""
    res = vector_store.similarity_search(query, k=1)
    if res:
        meta = res[0].metadata
        return {
            "title": meta.get("title"),
            "code": meta.get("code"),
            "description": res[0].page_content
        }
    return None

def vector_cypher_retriever(occupation_code: str):
    """Connector Tool: Pulls exact skill/task data for a specific O*NET code."""
    query = """
    MATCH (o:Occupation {code: $code})
    OPTIONAL MATCH (o)-[r:REQUIRES]->(s:Skill)
    OPTIONAL MATCH (o)-[:PERFORMS]->(t:Task)
    RETURN o.title as title, 
           o.code as code,
           collect(distinct {name: s.name, level: r.level})[0..10] as skills,
           collect(distinct t.statement)[0..5] as tasks
    """
    res = graph_db.query(query, {"code": occupation_code})
    return res[0] if res else None