# run_ingestion.py (Located in your root POC-LFDT folder)
from pathlib import Path
from src.ingestion.loader import ingest_occupations, ingest_skills, ingest_tasks
from src.ingestion.vectorizer import create_vector_index, vectorize_occupations
from src.database.neo4j_driver import db

# 1. Setup Paths
# This ensures we find the data folder regardless of where the terminal is opened
root = Path(__file__).resolve().parent
ONET_DIR = root / "data" / "raw" / "onet"

def main():
    print("🛠️  Starting Master GraphRAG Ingestion Pipeline...")
    print("-" * 50)
    
    try:
        # --- PHASE 1: Raw Data Ingestion (CSV/TXT to Graph) ---
        # This creates the Nodes and Relationships (Occupations, Skills, Tasks)
        ingest_occupations(ONET_DIR / "Occupation Data.txt")
        ingest_skills(ONET_DIR / "Skills.txt")
        ingest_tasks(ONET_DIR / "Task Statements.txt")
        
        print("\n--- PHASE 1 COMPLETE ---")
        
        # --- PHASE 2: AI Infrastructure (Vector Index) ---
        # This sets up the 768-dim index in Neo4j if it doesn't exist
        create_vector_index()
        
        # --- PHASE 3: AI Enrichment (Semantic Vectorization) ---
        # This sends the descriptions to Gemini and saves the vectors back to Neo4j
        # batch_size=50 is optimal for the Gemini API free tier
        vectorize_occupations(batch_size=50)
        
        print("\n--- PHASE 3 COMPLETE ---")

        # --- FINAL VERIFICATION ---
        print("\n📊 Final Database Stats:")
        # We fetch the counts of all node types to ensure everything is live
        stats = db.run_query("MATCH (n) RETURN labels(n)[0] as Label, count(n) as Count")
        for s in stats:
            label = s.get('Label', 'Unknown')
            count = s.get('Count', 0)
            print(f"- {label}: {count}")
            
    except Exception as e:
        print(f"\n❌ Pipeline Failed: {e}")
    finally:
        # Crucial: Always close the connection to avoid memory leaks in Neo4j AuraDB
        db.close()
        print("\n✅ Process Finished. System is ready for retrieval.")

if __name__ == "__main__":
    main()