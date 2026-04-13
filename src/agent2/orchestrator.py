import sys
import os
from langgraph.graph import StateGraph,END
from langgraph.checkpoint.memory import MemorySaver
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent2.state import TalentAngelState
from src.agent2.nodes import (
    parser_node, role_extractor_node, gatekeeper_node,
    locator_node, connector_node, supervisor_node,
    pathfinder_node, market_researcher_node, social_scout_node,
    media_expert_node, academic_advisor_node, project_architect_node,
    data_aggregator_node, consultor_node, critic_node
)

def route_standard(state:TalentAngelState):
    """Handles basic next_action routing for Gatekeeper and Critic."""
    return state.get("next_action","end")

def route_from_supervisor(state: TalentAngelState):
    """Dynamic routing for parallel workers based on LLM decision."""
    return state.get("supervisor_routes", ["pathfinder"])

workflow = StateGraph(TalentAngelState)

workflow.add_node("parser",parser_node)
workflow.add_node("role_extractor",role_extractor_node)
workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("locator", locator_node)
workflow.add_node("connector", connector_node)
workflow.add_node("supervisor", supervisor_node)

workflow.add_node("pathfinder", pathfinder_node)
workflow.add_node("market_researcher", market_researcher_node)
workflow.add_node("social_scout", social_scout_node)
workflow.add_node("media_expert", media_expert_node)
workflow.add_node("academic_advisor", academic_advisor_node)
workflow.add_node("project_architect", project_architect_node)


workflow.add_node("data_aggregator", data_aggregator_node)
workflow.add_node("consultor", consultor_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("parser")
workflow.add_edge("parser","role_extractor")
workflow.add_edge("role_extractor","gatekeeper")

workflow.add_conditional_edges(
    "gatekeeper",
    route_standard,
    {"locator":"locator","end":END}

)

workflow.add_edge("locator","connector")
workflow.add_edge("connector","supervisor")

possible_workers = [
    "pathfinder",
    "market_researcher",
    "social_scout",
    "media_expert",
    "academic_advisor",
    "project_architect",
]

workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    possible_workers
)

for worker in possible_workers:
    workflow.add_edge(worker,"data_aggregator")

workflow.add_edge("data_aggregator", "consultor")
workflow.add_edge("consultor", "critic")

workflow.add_conditional_edges(
    "critic", 
    route_standard, 
    {"consultor": "consultor", "end": END}
)

memory = MemorySaver()

carrer_forge_app = workflow.compile(checkpointer=memory)