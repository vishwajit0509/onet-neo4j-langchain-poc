import os
import yaml  
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Load environment variables
load_dotenv(BASE_DIR / ".env")



PROMPTS_PATH = BASE_DIR / "config" / "prompts.yaml" 
PROMPTS_V2_PATH = BASE_DIR / "config" / "prompts_v2.yaml" 

with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)


PROMPTS_V2 = {}
if PROMPTS_V2_PATH.exists():
    with open(PROMPTS_V2_PATH, "r", encoding="utf-8") as f:
        PROMPTS_V2 = yaml.safe_load(f)
else:
    print(f"⚠️ Warning: {PROMPTS_V2_PATH} not found.")


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


GEMINI_MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.5


# 📂 DATA PATHS

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

ONET_DIR = RAW_DATA_DIR / "onet"
ESCO_DIR = RAW_DATA_DIR / "esco"


# ✅ UPDATED VALIDATION
def validate_config():
    required = [
        "NEO4J_URI", 
        "NEO4J_PASSWORD", 
        "GOOGLE_API_KEY", 
        "TAVILY_API_KEY", 
        "YOUTUBE_API_KEY" 
    ]
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print(f"❌ Missing env variables: {', '.join(missing)}")
        return False

    print("✅ Settings Loaded Successfully.")
    print(f"✅ V1 Prompts: {list(PROMPTS.keys()) if PROMPTS else 'Empty'}")
    print(f"✅ V2 Prompts: {list(PROMPTS_V2.keys()) if PROMPTS_V2 else 'Empty'}")
    return True


if __name__ == "__main__":
    validate_config()