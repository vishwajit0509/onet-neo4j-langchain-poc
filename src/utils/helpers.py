# src/utils/helpers.py
import yaml
from pathlib import Path

def load_prompts():
    """Loads the YAML configuration for AI prompts."""
    root = Path(__file__).resolve().parent.parent.parent
    prompt_path = root / "config" / "prompts.yaml"
    with open(prompt_path, "r") as f:
        return yaml.safe_load(f)

# Initialize a global prompts object
PROMPTS = load_prompts()