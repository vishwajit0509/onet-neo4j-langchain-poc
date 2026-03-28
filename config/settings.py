import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Setup Base Directory (The root POC-LFDT folder)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Load environment variables from the .env file in the root
load_dotenv(BASE_DIR / ".env")

# --- 🔐 SECURE CREDENTIALS ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- 🤖 AI MODEL SETTINGS ---
GEMINI_MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.1  # Keep it low for factual data extraction

# --- 📂 FOLDER PATHS ---
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Sub-folders for specific taxonomies
ONET_DIR = RAW_DATA_DIR / "onet"
ESCO_DIR = RAW_DATA_DIR / "esco"

# --- ✅ VALIDATION ---
def validate_config():
    """Checks if critical environment variables are loaded."""
    required = ["NEO4J_URI", "NEO4J_PASSWORD", "GOOGLE_API_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        print(f"❌ Error: Missing env variables: {', '.join(missing)}")
        return False
    print("✅ Settings Loaded Successfully.")
    return True

if __name__ == "__main__":
    validate_config()