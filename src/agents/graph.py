from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agents.state import TalentAngelState
from src.agents.nodes import (
    role_extractor_node,
    gatekeeper_node,
    locator_node,
    connector_node,
    pathfinder_node,
    market_researcher_node,
    consultor_node,
    critic_node,
)

workflow = StateGraph(TalentAngelState)

workflow.add_node("role_extractor", role_extractor_node)
workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("locator", locator_node)
workflow.add_node("connector", connector_node)
workflow.add_node("pathfinder", pathfinder_node)
workflow.add_node("market_researcher", market_researcher_node)
workflow.add_node("consultor", consultor_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("role_extractor")


def route(state):
    return state["next_action"]


workflow.add_edge("role_extractor", "gatekeeper")
workflow.add_conditional_edges("gatekeeper", route, {"locator": "locator", "end": END})
workflow.add_edge("locator", "connector")

workflow.add_conditional_edges(
    "connector",
    route,
    {
        "pathfinder": "pathfinder",
        "market_researcher": "market_researcher",
    },
)

workflow.add_edge("pathfinder", "market_researcher")
workflow.add_edge("market_researcher", "consultor")
workflow.add_edge("consultor", "critic")

workflow.add_conditional_edges(
    "critic",
    route,
    {
        "consultor": "consultor",
        "end": END,
    },
)

memory = MemorySaver()
talent_app = workflow.compile(checkpointer=memory)