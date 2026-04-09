from typing import TypedDict, Optional, Dict

class TalentAngelState(TypedDict):
    user_query: str

    # Extraction
    current_role: Optional[str]
    target_role: Optional[str]
    intent: Optional[str]
    needs_clarification: bool

    # Retrieval
    locator_data: Optional[Dict]
    target_data: Optional[Dict]
    connector_data: Optional[Dict]

    # Analysis
    pathfinder_data: Optional[Dict]
    market_data: Optional[str]

    # Output
    final_response: Optional[str]
    critic_feedback: Optional[str]

    next_action: str