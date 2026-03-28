# src/database/neo4j_driver.py
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path

# Setup root path to find .env
root = Path(__file__).resolve().parent.parent.parent
load_dotenv(root / ".env")

class Neo4jManager:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        pwd = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            # Use consume() to ensure the result is fully processed
            return [record.data() for record in result]

# Initialize a singleton instance
db = Neo4jManager()