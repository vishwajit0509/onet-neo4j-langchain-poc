# src/ingestion/vectorizer.py
import sys
import os

# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tqdm import tqdm
from src.database.neo4j_driver import db
from src.utils.llms import embeddings  # Ensure your filename is correct here!

def create_vector_index():
    """Phase 2: Define the 768-Dimension Index in Neo4j."""
    print("🛡️ Checking Vector Index...")
    query = """
    CREATE VECTOR INDEX occupation_embeddings IF NOT EXISTS
    FOR (o:Occupation)
    ON (o.embedding)
    OPTIONS {
      indexConfig: {
        `vector.dimensions`: 768,
        `vector.similarity_function`: 'cosine'
      }
    }
    """
    try:
        db.run_query(query)
        # Verify status
        status = db.run_query("SHOW INDEXES YIELD name, state WHERE name = 'occupation_embeddings'")
        print(f"✅ Vector Index Status: {status[0]['state']}")
    except Exception as e:
        print(f"❌ Index Creation Failed: {e}")

def vectorize_occupations(batch_size=50):
    """Phase 3: Turbo Mode Semantic Enrichment."""
    # 1. Fetch jobs that need embeddings
    to_embed = db.run_query("""
        MATCH (o:Occupation) 
        WHERE o.embedding IS NULL 
        RETURN o.code as code, o.description as text
    """)

    if not to_embed:
        print("✨ All occupations are already vectorized!")
        return

    total_nodes = len(to_embed)
    print(f"🚀 Turbo Mode: Vectorizing {total_nodes} nodes in batches of {batch_size}...")

    # 2. Process in chunks
    for i in tqdm(range(0, total_nodes, batch_size)):
        batch = to_embed[i : i + batch_size]
        batch_texts = [row['text'] for row in batch]
        batch_codes = [row['code'] for row in batch]

        try:
            # 3. Mass Embedding (Gemini)
            batch_vectors = embeddings.embed_documents(batch_texts)

            # 4. Mass Write (Neo4j UNWIND)
            update_query = """
            UNWIND $data as item
            MATCH (o:Occupation {code: item.code})
            CALL db.create.setNodeVectorProperty(o, 'embedding', item.vector)
            """
            data_to_send = [
                {"code": code, "vector": vector} 
                for code, vector in zip(batch_codes, batch_vectors)
            ]
            db.run_query(update_query, {"data": data_to_send})

        except Exception as e:
            print(f"⚠️ Batch starting at index {i} failed: {e}")
            continue

    print("✅ Semantic Enrichment Finished.")

