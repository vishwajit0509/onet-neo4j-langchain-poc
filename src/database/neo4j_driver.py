# src/database/neo4j_driver.py
import os
import sys


# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from src.utils.llms import embeddings # Import from your utils
from dotenv import load_dotenv
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
load_dotenv(root / ".env")

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PWD = os.getenv("NEO4J_PASSWORD")

# 1. Raw Driver (For Ingestion)
class Neo4jManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    def close(self):
        self.driver.close()
    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

db = Neo4jManager()

# 2. LangChain Wrappers (For Retrieval)
graph_db = Neo4jGraph(url=URI, username=USER, password=PWD)

vector_store = Neo4jVector.from_existing_index(
    embeddings,
    url=URI,
    username=USER,
    password=PWD,
    index_name="occupation_embeddings",
    text_node_property="description",
    # ADD THIS LINE TO SKIP THE "FOO" TEST:
    embedding_dimension=768 
)