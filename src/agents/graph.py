# src/agents/graph.py
import os
import sys


# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Internal Imports
from src.agents.state import TalentAngelState
from src.agents.nodes import (
    gatekeeper_node, locator_node, connector_node, 
    pathfinder_node, market_researcher_node, 
    consultor_node, critic_node
)

# 1. The Switchboard (Routing Logic)
def route_action(state: TalentAngelState):
    """
    Reads the 'next_action' key set by the previous node 
    to decide the next destination in the graph.
    """
    return state["next_action"]

# 2. Initializing the State Machine
workflow = StateGraph(TalentAngelState)

# 3. Registering the Angels (Nodes)
workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("locator", locator_node)
workflow.add_node("connector", connector_node)
workflow.add_node("pathfinder", pathfinder_node)
workflow.add_node("market_researcher", market_researcher_node)
workflow.add_node("consultor", consultor_node)
workflow.add_node("critic", critic_node)

# 4. Defining the Logic Flow (Edges)

# Entry Point
workflow.set_entry_point("gatekeeper")

# Gatekeeper decides if we proceed or end immediately
workflow.add_conditional_edges(
    "gatekeeper", 
    route_action, 
    {"locator": "locator", "end": END}
)

# Locator always flows into the Connector
workflow.add_edge("locator", "connector")

# Connector decides: Deep Dive (Pathfinder) or Market Pulse (Researcher)
workflow.add_conditional_edges(
    "connector", 
    route_action, 
    {"pathfinder": "pathfinder", "market_researcher": "market_researcher"}
)

# Both Pathfinder and Researcher feed into the Consultor
workflow.add_edge("pathfinder", "market_researcher")
workflow.add_edge("market_researcher", "consultor")

# Consultor draft always goes to the Critic for a QA check
workflow.add_edge("consultor", "critic")

# THE CRITIC LOOP: If score is low, go back to Consultor. If approved, end.
workflow.add_conditional_edges(
    "critic", 
    route_action, 
    {"consultor": "consultor", "end": END}
)

# 5. Compiling with Persistence
# MemorySaver allows the graph to 'remember' conversation states using a thread_id
memory = MemorySaver()
talent_app = workflow.compile(checkpointer=memory)

print("🚀 Level 10 Enterprise Graph Compiled and Ready for Launch!")