# src/ingestion/loader.py
import pandas as pd
import sys
import os

# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# NOW your imports will work
from src.database.neo4j_driver import db

def ingest_occupations(file_path):
    print("🚀 Ingesting Occupations...")
    df = pd.read_csv(file_path, sep='\t')
    
    query = """
    UNWIND $rows AS row
    MERGE (o:Occupation {code: row.code})
    SET o.title = row.title, o.description = row.description
    """
    rows = [
        {"code": r['O*NET-SOC Code'], "title": r['Title'], "description": r['Description']} 
        for _, r in df.iterrows()
    ]
    db.run_query(query, {"rows": rows})
    print(f"✅ {len(rows)} Occupations live!")

def ingest_skills(file_path):
    print("🚀 Ingesting Skills and Relationships...")
    df = pd.read_csv(file_path, sep='\t')

    # 1. Create Unique Skill Nodes
    unique_skills = df[['Element ID', 'Element Name']].drop_duplicates()
    skill_rows = [{"id": r['Element ID'], "name": r['Element Name']} for _, r in unique_skills.iterrows()]
    db.run_query("UNWIND $rows AS row MERGE (s:Skill {id: row.id}) SET s.name = row.name", {"rows": skill_rows})

    # 2. Pivot for weighted relationships (IM and LV)
    skills_pivot = df.pivot_table(
        index=['O*NET-SOC Code', 'Element ID'], 
        columns='Scale ID', 
        values='Data Value'
    ).reset_index()

    query_rel = """
    UNWIND $rows AS row
    MATCH (o:Occupation {code: row.occ})
    MATCH (s:Skill {id: row.skill})
    MERGE (o)-[r:REQUIRES]->(s)
    SET r.importance = toFloat(row.IM), r.level = toFloat(row.LV)
    """
    rows_rel = [
        {"occ": r['O*NET-SOC Code'], "skill": r['Element ID'], "IM": r.get('IM', 0), "LV": r.get('LV', 0)} 
        for _, r in skills_pivot.iterrows()
    ]
    db.run_query(query_rel, {"rows": rows_rel})
    print(f"✅ {len(rows_rel)} Skill relationships mapped!")

def ingest_tasks(file_path):
    print("🚀 Ingesting Tasks...")
    df = pd.read_csv(file_path, sep='\t')
    
    query = """
    UNWIND $rows AS row
    MATCH (o:Occupation {code: row.occ_code})
    MERGE (t:Task {id: row.id})
    SET t.statement = row.task
    MERGE (o)-[:PERFORMS]->(t)
    """
    rows = [
        {"occ_code": r['O*NET-SOC Code'], "id": r['Task ID'], "task": r['Task']} 
        for _, r in df.iterrows()
    ]
    db.run_query(query, {"rows": rows})
    print(f"✅ {len(rows)} Tasks linked!")