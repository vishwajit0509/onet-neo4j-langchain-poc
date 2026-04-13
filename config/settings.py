import os
import yaml  # ✅ FIX 1: Add this
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Load environment variables
load_dotenv(BASE_DIR / ".env")


PROMPTS_PATH = BASE_DIR / "config" / "prompts.yaml" 

with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


GEMINI_MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.1

# -------------------------
# 📂 DATA PATHS
# -------------------------
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

ONET_DIR = RAW_DATA_DIR / "onet"
ESCO_DIR = RAW_DATA_DIR / "esco"

# -------------------------
# ✅ VALIDATION
# -------------------------
def validate_config():
    required = ["NEO4J_URI", "NEO4J_PASSWORD", "GOOGLE_API_KEY"]
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print(f"❌ Missing env variables: {', '.join(missing)}")
        return False

    print("✅ Settings Loaded Successfully.")
    print(f"✅ Prompts Loaded: {list(PROMPTS.keys())}")  # 🔥 DEBUG
    return True


if __name__ == "__main__":
    validate_config()