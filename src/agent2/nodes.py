import os
import sys
from typing import Dict,List,Any
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.llms import llm
from src.utils.helpers import (
    PROMPTS_V2, 
    safe_json_loads, 
    clean_role
)

from src.agent2.state import TalentAngelState

from src.tools.resume_engine import parse_resume
from src.retrieval.simple_retriever import vector_search as simple_vector_search
from src.retrieval.hybrid_retriever import get_detailed_occupation_data as vector_cypher_retriever
from src.database.neo4j_driver import graph_db
from src.tools.search_engine import youtube_search,tavily_client, extract_items_from_tavily

def parser_node(state:TalentAngelState):
    print("📄 Parser: Processing resume...")

    pdf_path = state.get("resume_path")

    if pdf_path and os.path.exists(pdf_path):
        raw_text = parse_resume(pdf_path)
        return {"resume_text":raw_text}
    return {"resume_text":None}


def role_extractor_node(state:TalentAngelState):
    print("🧠 Role Extractor: Understanding intent...")
    query = state.get("user_query") or ""
    resume = state.get("resume_text") or ""

    existing_current = state.get("current_role")
    existing_target = state.get("target_role")
    prompt = PROMPTS_V2.get("extraction_prompt","")

    try:
        response = llm.invoke(
            prompt+f'\nQuery: "{query}"\nResume:{resume[:1500]}'
        ).content.strip()
    except Exception:
        response = "{}"

    data = safe_json_loads(response,{})

    extracted_current = clean_role(data.get("current_role"))
    extracted_target = clean_role(data.get("target_role"))

    if extracted_current == "none": extracted_current = None
    if extracted_target == "none": extracted_target = None

    current_role = extracted_current if extracted_current else existing_current
    target_role = extracted_target if extracted_target else existing_target

    intent = data.get("intent") or "transition"

    if target_role and target_role != current_role:
        intent = "transition"

    # Clarification logic
    if current_role:
        needs_clarification = False
    elif intent == "transition" and not current_role:
        needs_clarification = True
    else:
        needs_clarification = False

    print(f"   -> Current Role: '{current_role}' | Target Role: '{target_role}'")
    print(f"   -> Intent: '{intent}' | Clarification Needed: {needs_clarification}")

    return {
        "current_role": current_role,
        "target_role": target_role,
        "intent": intent,
        "needs_clarification": needs_clarification,
        "resume_skills": data.get("resume_skills", []),
        "next_action": "gatekeeper",
    }

def gatekeeper_node(state: TalentAngelState):
    print("🛡️ Gatekeeper: Validating query...")
    intent = state.get("intent", "transition")
    needs_clarification = state.get("needs_clarification", False)

    if intent == "off_topic":
        return {
            "final_response": "I can only help with career-related queries.",
            "next_action": "end",
        }

    if needs_clarification:
        return {
            "final_response": "Please tell me your current profession so I can guide the transition.",
            "next_action": "end",
        }
        
    return {"next_action": "locator"}

def locator_node(state: TalentAngelState):
    print("📍 Locator: Finding role in O*NET taxonomy...")
    role_to_search = state.get("current_role") or state.get("target_role")
    
    if not role_to_search:
        return {
            "final_response": "I need to know your current or target profession to guide you.",
            "next_action": "end"
        }

    try:
        result = simple_vector_search(role_to_search)
        if not result or not isinstance(result, dict) or "code" not in result:
            raise ValueError("Invalid vector search data.")
    except Exception as e:
        print(f"   ⚠️ Locator Search Failed: {e}")
        return {
            "final_response": f"I had trouble finding '{role_to_search}' in my database. Could you try describing it differently?",
            "next_action": "end"
        }

    print(f"   -> Matched: '{result.get('title')}' (Code: {result.get('code')})")
    return {"locator_data": result, "next_action": "connector"}

def connector_node(state: TalentAngelState):
    print("🔗 Connector: Fetching graph data...")
    locator_data = state.get("locator_data") or {}
    code = locator_data.get("code")

    if not code:
        return {"connector_data":None,"next_action":"supervisor"}
    
    try:
        data = vector_cypher_retriever(code)
    except Exception as e:
        print(f"   ⚠️ Connector DB Error: {e}")
        data = None

    if data:
        skills = data.get("skills", [])
        data["skills"] = [s for s in skills if s and isinstance(s, dict) and s.get("name")]

    return {"connector_data": data, "next_action": "supervisor"}

def supervisor_node(state:TalentAngelState):
    print("👔 Supervisor: Analyzing semantics for fan-out...")
    query = state.get("user_query") or ""
    intent = state.get("intent") or "transition"
    has_target = bool(state.get("target_role"))

    raw_prompt = PROMPTS_V2.get("supervisor_prompt", "")
    prompt = raw_prompt.format(query=query,intent=intent)

    try:
        raw_response = llm.invoke(prompt).content.strip()
        routes = safe_json_loads(raw_response,[])
        if not isinstance(routes,list):routes=[]

    except Exception as e:
        print(f"   ⚠️ Semantic Routing failed ({e}).")
        routes = []

    if intent == "transition" and has_target and "pathfinder" not in routes:
        routes.append("pathfinder")
    if not has_target and "pathfinder" in routes:
        routes.remove("pathfinder")

    if not routes:
        routes = ["market_researcher", "academic_advisor"]

    routes = sorted(list(routes))
    print(f"   -> Parallel Routing Decision: {routes}")
    return {"supervisor_routes":routes,"next_action":"dispatch"}


def pathfinder_node(state: TalentAngelState):
    print("🛤️ Pathfinder: Computing skill gaps using Neo4j...")
    
    current = state.get("locator_data") or {}
    target_role = state.get("target_role")
    intent = state.get("intent")

    
    if not current.get("code") or intent != "transition" or not target_role:
        return {"graph_gap_data": None, "target_data": None}

    
    raw_ctx = PROMPTS_V2.get("pathfinder_context_prompt", "")
    context_prompt = raw_ctx.format(current_title=current.get('title'), target_role=target_role)
    
    try:
        raw_search = llm.invoke(context_prompt).content.strip()
        search_query = raw_search.replace("```text", "").replace("```", "").strip()
    except Exception:
        search_query = target_role
        
    print(f"   -> Refined Database Search Term: '{search_query}'")
    
    
    target_job = simple_vector_search(search_query)
    if not target_job or "code" not in target_job:
        return {"graph_gap_data": None, "target_data": None}

    
    gap_query = """
    MATCH (target:Occupation {code: $target_code})-[r_target:REQUIRES]->(s:Skill)
    OPTIONAL MATCH (current:Occupation {code: $current_code})-[r_current:REQUIRES]->(s)
    WITH s, COALESCE(r_target.level, 0) AS t, COALESCE(r_current.level, 0) AS c
    WHERE t > c AND s.name IS NOT NULL
    RETURN s.name AS skill, c AS current_level, t AS target_level, (t - c) AS gap
    ORDER BY gap DESC LIMIT 8
    """
    
    try:
        gap_data = graph_db.query(
            gap_query,
            {"current_code": current["code"], "target_code": target_job["code"]},
        )
        clean_gaps = [g for g in gap_data if isinstance(g, dict) and g.get("skill")]
    except Exception as e:
        print(f"   ⚠️ Pathfinder Neo4j Error: {e}")
        clean_gaps = []
    
    return {
        "target_data": target_job,
        "graph_gap_data": {
            "current_role": current.get("title", "Unknown"),
            "target_role": target_job.get("title", "Unknown"),
            "gaps": clean_gaps,
        },
    }

def market_researcher_node(state: TalentAngelState):
    print("📈 Market Researcher: Fetching live salary and demand...")
    role = state.get("target_role") or state.get("current_role") or "the role"
    query = f"Average salary and hiring market demand in India for {role}"
    
    try:
        result = tavily_client.search(query, search_depth="basic")
        
        links = extract_items_from_tavily(result, limit=4)
        
        
        results_list = result.get("results", [])
        snippet_text = "\n".join([r.get("content", "") for r in results_list[:2] if isinstance(r, dict)])
    except Exception as e:
        print(f"   ⚠️ Market Researcher API Error: {e}")
        links, snippet_text = [], ""

    return {
        "market_research_data": {
            "role": role,
            "summary": snippet_text[:700] or f"Salary data unavailable for {role}.",
            "links": links,
        }
    }

def social_scout_node(state: TalentAngelState):
    print("🌐 Social Scout: Scraping networking links...")
    role = state.get("target_role") or state.get("current_role") or "the role"
    query = f"site:reddit.com OR site:linkedin.com career networking advice for {role}"
    
    try:
        result = tavily_client.search(query, search_depth="basic")
        
        links = extract_items_from_tavily(result, limit=4)
    except Exception as e:
        print(f"   ⚠️ Social Scout API Error: {e}")
        links = []

    tips = [
        f"Join '{role}' specific LinkedIn groups for industry updates.",
        f"Search Reddit for '{role} interview experience' to find real-world prep.",
        "Use a clear, value-driven subject line for cold networking."
    ]

    return {
        "social_data": {
            "role": role,
            "tips": tips,
            "links": links,
        }
    }


def media_expert_node(state: TalentAngelState):
    print("🎥 Media Expert: Sourcing 'Day in the Life' videos...")
    role = state.get("target_role") or state.get("current_role") or "the role"

    try:
        # Using the centralized tool we built earlier
        videos = youtube_search(f"day in the life of a {role}", max_results=3)
        if not isinstance(videos, list):
            videos = []
    except Exception as e:
        print(f"   ⚠️ Media Expert API Error: {e}")
        videos = []
        
    return {
        "media_data": {
            "role": role,
            "videos": videos,
        }
    }

def academic_advisor_node(state: TalentAngelState):
    print("🎓 Academic Advisor: Searching for top-tier courses...")
    role = state.get("target_role") or state.get("current_role") or "the role"

    try:
        query = f"Best online courses and certifications for {role} Coursera Udemy edX"
        result = tavily_client.search(query, search_depth="basic")
        
        
        courses = extract_items_from_tavily(result, limit=4)
        
    except Exception as e:
        print(f"   ⚠️ Academic Advisor API Error: {e}")
        courses = []

    return {
        "academic_data": {
            "role": role,
            "courses": courses,
        }
    }

def project_architect_node(state: TalentAngelState):
    print("🏗️ Project Architect: Brainstorming portfolio ideas...")
    role = state.get("target_role") or state.get("current_role") or "the role"

    
    raw_prompt = PROMPTS_V2.get("project_prompt", "")
    prompt = raw_prompt.format(role=role)
    
    try:
        response = llm.invoke(prompt).content
        
        data = safe_json_loads(response, {})
        projects = data.get("projects", [])
        
        if not isinstance(projects, list):
            projects = []
            
    except Exception as e:
        print(f"   ⚠️ Project Architect LLM Error: {e}")
        projects = []

    
    if not projects:
        projects = [{
            "title": f"{role} Portfolio Showcase",
            "difficulty": "intermediate",
            "stack": [role, "Relevant Industry Tools"],
            "why_it_helps": "Demonstrates core technical proficiency and domain knowledge.",
            "deliverables": ["GitHub Repository", "Architecture Diagram", "Project Summary"]
        }]

    return {
        "project_data": {
            "role": role,
            "projects": projects,
        }
    }

