# run_ingestion.py
from pathlib import Path
from src.ingestion.loader import ingest_occupations, ingest_skills, ingest_tasks
from src.database.neo4j_driver import db

# Setup Paths
root = Path(__file__).resolve().parent
ONET_DIR = root / "data" / "raw" / "onet"

def main():
    print("🛠️ Starting Graph Ingestion Pipeline...")
    
    try:
        ingest_occupations(ONET_DIR / "Occupation Data.txt")
        ingest_skills(ONET_DIR / "Skills.txt")
        ingest_tasks(ONET_DIR / "Task Statements.txt")
        
        # Verify
        print("\n📊 Final Database Stats:")
        stats = db.run_query("MATCH (n) RETURN labels(n)[0] as Label, count(n) as Count")
        for s in stats:
            print(f"- {s['Label']}: {s['Count']}")
            
    except Exception as e:
        print(f"❌ Ingestion Failed: {e}")
    finally:
        db.close()
        print("\n✅ Process Finished.")

if __name__ == "__main__":
    main()