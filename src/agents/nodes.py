# src/agents/nodes.py
import pandas as pd
import sys
import os

# Adds the root directory (POC-LFDT) to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.retrieval.simple_retriever import vector_search
from src.retrieval.hybrid_retriever import get_detailed_occupation_data
from src.database.neo4j_driver import graph_db
from src.utils.llms import llm
from src.utils.helpers import PROMPTS
from src.agents.state import TalentAngelState

def gatekeeper_node(state: TalentAngelState):
    print("🛡️ Gatekeeper: Securing input...")
    query = state['user_query']
    prompt = PROMPTS['gatekeeper']['system'].format(query=query)
    classification = llm.invoke(prompt).content.strip().upper()
    
    if "YES" in classification:
        return {"next_action": "locator"}
    return {"final_response": "I am a Talent Angel for career mapping. Please ask a career-related question.", "next_action": "end"}

def locator_node(state: TalentAngelState):
    print("📍 Locator: Finding anchor career...")
    result = vector_search(state['user_query'])
    if not result:
        return {"final_response": "I couldn't find that career in O*NET.", "next_action": "end"}
    return {"locator_data": result, "next_action": "connector"}

def connector_node(state: TalentAngelState):
    print("🔗 Connector: Fetching graph relationships...")
    code = state['locator_data']['code']
    data = get_detailed_occupation_data(code)
    
    query_lower = state['user_query'].lower()
    needs_path = any(w in query_lower for w in ["path", "how to", "become", "transition", "gap"])
    return {"connector_data": data, "next_action": "pathfinder" if needs_path else "market_researcher"}

def pathfinder_node(state: TalentAngelState):
    print("🛤️ Pathfinder: Calculating skill gap...")
    extract_prompt = PROMPTS['pathfinder']['extract'].format(query=state['user_query'])
    target_raw = llm.invoke(extract_prompt).content.strip()
    target_job = vector_search(target_raw)
    
    if not target_job:
        return {"pathfinder_data": "Target career not found.", "next_action": "market_researcher"}
    
    # Mathematical Gap Analysis: $Growth = Target - Current$
    gap_query = """
    MATCH (target:Occupation {code: $target_code})-[r_target:REQUIRES]->(s:Skill)
    OPTIONAL MATCH (current:Occupation {code: $current_code})-[r_current:REQUIRES]->(s)
    WITH s, r_target.level AS t_lvl, COALESCE(r_current.level, 0) AS c_lvl
    WHERE t_lvl > c_lvl
    RETURN s.name AS skill, (t_lvl - c_lvl) AS gap ORDER BY gap DESC LIMIT 5
    """
    gap_data = graph_db.query(gap_query, {"current_code": state['locator_data']['code'], "target_code": target_job['code']})
    
    roadmap = f"Target: {target_job['title']}\nGaps: " + ", ".join([f"{g['skill']} (+{round(g['gap'], 1)})" for g in gap_data])
    return {"pathfinder_data": roadmap, "next_action": "market_researcher"}

def market_researcher_node(state: TalentAngelState):
    print("📈 Researcher: Getting market trends...")
    job = state['locator_data']['title']
    prompt = PROMPTS['market_researcher']['research'].format(job_title=job)
    insights = llm.invoke(prompt).content.strip()
    return {"market_data": insights, "next_action": "consultor"}

def consultor_node(state: TalentAngelState):
    print("👼 Consultor: Finalizing roadmap...")
    context = f"Job: {state['locator_data']['title']}\n"
    if state.get('pathfinder_data'): context += f"Gap: {state['pathfinder_data']}\n"
    if state.get('market_data'): context += f"Market: {state['market_data']}\n"
    
    prompt = PROMPTS['consultor']['roadmap'].format(context=context)
    if state.get('critic_feedback'):
        prompt += PROMPTS['consultor']['feedback_loop'].format(feedback=state['critic_feedback'])
        
    response = llm.invoke(prompt)
    return {"final_response": response.content, "next_action": "critic"}

def critic_node(state: TalentAngelState):
    print("🧐 Critic: Validating response...")
    prompt = PROMPTS['critic']['review'].format(draft=state['final_response'])
    evaluation = llm.invoke(prompt).content
    
    try:
        score = int(evaluation.split("SCORE:")[1].split("\n")[0].strip())
        feedback = evaluation.split("FEEDBACK:")[1].strip()
    except: score, feedback = 10, "APPROVED"

    if score < 8:
        return {"critic_feedback": feedback, "next_action": "consultor"}
    return {"next_action": "end"}