# src/utils/llm.py
import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 1. Load Environment Variables
# Finds the .env file by going up 3 levels from src/utils/llm.py to POC-LFDT/
root = Path(__file__).resolve().parent.parent.parent
load_dotenv(root / ".env")

# 2. Initialize 2026 Gemini Flash
# This is your primary "Thinking" engine
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 3. Initialize Modern Embeddings
# Task-type 'retrieval_document' and 768 dims ensure perfect 
# alignment with your Neo4j Vector Index
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="retrieval_document",
    output_dimensionality=768
)