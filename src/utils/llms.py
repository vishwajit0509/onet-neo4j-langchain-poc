# src/utils/llm.py
import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings



root = Path(__file__).resolve().parent.parent.parent
load_dotenv(root / ".env")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class FixedGoogleEmbeddings(GoogleGenerativeAIEmbeddings):
    def embed_query(self,text:str):
        return super().embed_documents([text])[0]
    

embeddings = FixedGoogleEmbeddings(
    model="models/gemini-embedding-001",
    #task_type="retrieval_document",
    output_dimensionality=768
)

