"""
Talent Angels POC - System Verification Script
Checks connectivity to Neo4j AuraDB and Google Gemini API.
"""

import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

def verify_neo4j():
    """Tests the connection to the Neo4j AuraDB instance."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    logger.info(f"Attempting Neo4j connection at {uri}...")
    try:
        # The +ssc protocol in your .env ensures we bypass local SSL certificate issues
        with GraphDatabase.driver(uri, auth=(user, password)) as driver:
            driver.verify_connectivity()
            return True, "Successfully connected to AuraDB."
    except Exception as e:
        return False, str(e)

def verify_gemini():
    """Tests the Google Gemini 2.5 API via LangChain."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    logger.info("Testing Google Gemini 2.5 Flash API...")
    try:
        # Initializing the model confirmed via diagnostics
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=api_key
        )
        
        # A simple check to ensure the API key and model are responsive
        response = llm.invoke("System check: Respond with 'Ready'.")
        return True, f"Gemini Response: {response.content.strip()}"
    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "="*50)
    print("🚀 TALENT ANGELS POC: FINAL SYSTEM CHECK")
    print("="*50 + "\n")

    # Run Neo4j Test
    neo_ok, neo_msg = verify_neo4j()
    if neo_ok:
        print(f"✅ NEO4J: {neo_msg}")
    else:
        print(f"❌ NEO4J: FAILED - {neo_msg}")

    print("-" * 50)

    # Run Gemini Test
    gem_ok, gem_msg = verify_gemini()
    if gem_ok:
        print(f"✅ GEMINI: {gem_msg}")
    else:
        print(f"❌ GEMINI: FAILED - {gem_msg}")

    print("\n" + "="*50)
    if neo_ok and gem_ok:
        print("🎉 SYSTEM READY: You are clear to begin ingestion!")
    else:
        print("⚠️ SYSTEM ERROR: Please check the failures above.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()