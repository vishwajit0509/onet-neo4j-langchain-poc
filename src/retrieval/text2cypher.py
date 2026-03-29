import pandas as pd
import sys
import os

# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.neo4j_driver import graph_db
from src.utils.llms import llm
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain

# Initialized here so the schema is cached once
cypher_qa = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph_db,
    verbose=True,
    allow_dangerous_requests=True
)
