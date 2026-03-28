# src/agents/state.py
from typing import TypedDict, Dict, Optional

class TalentAngelState(TypedDict):
    user_query: str
    locator_data: Optional[Dict]
    connector_data: Optional[Dict]
    pathfinder_data: Optional[str]
    market_data: Optional[str]
    final_response: Optional[str]
    critic_feedback: Optional[str]
    next_action: str