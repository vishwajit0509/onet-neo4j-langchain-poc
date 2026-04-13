# src/utils/helpers.py
import yaml
from pathlib import Path
import os
import json
from typing import Any,Optional

def load_prompts():
    """Loads the YAML configuration for AI prompts."""
    root = Path(__file__).resolve().parent.parent.parent
    prompt_path = root / "config" / "prompts.yaml"

    with open(prompt_path, "r") as f:
        return yaml.safe_load(f)


PROMPTS = load_prompts()

def safe_json_loads(text:str,default:Any):
    """Robust JSON parser for messy LLM  outputs"""
    text = text.strip()
    try:
        if "{" in text and "}" in text:
            fixed = text[text.index("{"):text.rindex("}")+1]
            return json.loads(fixed)
        if "[" in text and "]" in text:
            fixed = text[text.index("["):text.rindex("]") + 1]
            return json.loads(fixed)
        
    except Exception:
        pass
    return default

def clean_role(role:Optional[str])->Optional[str]:
    """Standardizes job titles"""
    return role.strip().lower() if isinstance(role,str) else None

def pick_role_for_lookup(state) -> Optional[str]:
    """Fallback logic for finding the relevant job title."""
    return (
        state.get("current_role")
        or state.get("target_role")
        or (state.get("locator_data") or {}).get("title")
    )


