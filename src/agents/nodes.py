import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import json
import time

from config import settings
from src.utils.llms import llm
from src.retrieval.simple_retriever import vector_search as simple_vector_search
from src.retrieval.hybrid_retriever import get_detailed_occupation_data as vector_cypher_retriever
from src.database.neo4j_driver import graph_db

PROMPTS = settings.PROMPTS


def safe_query(query, params=None, retries=3, delay=1):
    params = params or {}
    last_error = None

    for i in range(retries):
        try:
            return graph_db.query(query, params)
        except Exception as e:
            last_error = e
            print(f"⚠️ Neo4j retry {i + 1}/{retries}: {e}")
            time.sleep(delay)

    print(f"❌ Neo4j query failed after {retries} retries: {last_error}")
    return []


def _parse_json_response(raw: str) -> dict:
    try:
        return json.loads(raw)
    except Exception:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            return {}


def _skills_to_text(skills):
    if not skills:
        return "No skills linked in graph."

    items = []
    for s in skills:
        if isinstance(s, dict) and s.get("name"):
            level = s.get("level")
            if level is None:
                items.append(s["name"])
            else:
                items.append(f'{s["name"]} ({level})')

    return ", ".join(items) if items else "No skills linked in graph."


def _tasks_to_text(tasks):
    if not tasks:
        return "No tasks linked in graph."

    items = [t for t in tasks if isinstance(t, str) and t.strip()]
    return "; ".join(items[:5]) if items else "No tasks linked in graph."


def _gaps_to_text(gaps):
    if not gaps:
        return "No reliable gap data found."

    items = []
    for g in gaps:
        if isinstance(g, dict) and g.get("skill") is not None:
            gap_val = g.get("gap", 0)
            try:
                gap_val = round(float(gap_val), 2)
            except Exception:
                gap_val = gap_val
            items.append(f'{g["skill"]} (+{gap_val})')

    return ", ".join(items) if items else "No reliable gap data found."


def role_extractor_node(state):
    print("🧠 Role Extractor: Understanding user intent...")

    query = state["user_query"]
    
    
    existing_current = state.get("current_role")
    existing_target = state.get("target_role")

    prompt = PROMPTS["role_extractor"]["system"] + f'\nQuery: "{query}"'
    
   
    if existing_current:
        prompt += f"\n[Context: User previously stated they are a {existing_current}]"

    try:
        response = llm.invoke(prompt).content.strip()
        data = _parse_json_response(response)
    except Exception as e:
        print(f"LLM ERROR in role_extractor: {e}")
        data = {}

    
    extracted_current = data.get("current_role")
    if extracted_current and str(extracted_current).lower() != "none":
        current_role = extracted_current.lower().strip()
    else:
        current_role = existing_current 

    extracted_target = data.get("target_role")
    if extracted_target and str(extracted_target).lower() != "none":
        target_role = extracted_target.lower().strip()
    else:
        target_role = existing_target 

    
    intent = data.get("intent", "transition")
    needs_clarification = data.get("needs_clarification", False)

    
    if intent == "transition" and current_role:
        needs_clarification = False

    print(f"   -> current_role: {current_role}")
    print(f"   -> target_role: {target_role}")

    return {
        "current_role": current_role,
        "target_role": target_role,
        "intent": intent,
        "needs_clarification": needs_clarification,
        "next_action": "gatekeeper",
    }


def gatekeeper_node(state):
    print("🛡️ Gatekeeper: Validating query...")

    if state["intent"] == "off_topic":
        return {
            "final_response": "I only handle career-related queries.",
            "next_action": "end",
        }

    if state["needs_clarification"]:
        return {
            "final_response": "Please tell me your current profession so I can guide your transition.",
            "next_action": "end",
        }

    return {"next_action": "locator"}


def locator_node(state):
    print("📍 Locator: Finding current role...")

    role = state.get("current_role") or state.get("target_role")

    if not role:
        return {
            "final_response": "Role not found.",
            "next_action": "end",
        }

    print(f"   -> Searching for: {role}")

    result = simple_vector_search(role)

    if not result:
        return {
            "final_response": f"No match for {role}",
            "next_action": "end",
        }

    print(f"   -> Found: {result['title']}")

    return {
        "locator_data": result,
        "next_action": "connector",
    }


def connector_node(state):
    print("🔗 Connector: Fetching graph data...")

    code = state["locator_data"]["code"]
    data = vector_cypher_retriever(code)

    if not data:
        print("⚠️ No graph data found")

        empty_summary = "No graph details available for this occupation."
        return {
            "connector_data": {
                "title": state["locator_data"]["title"],
                "skills": [],
                "tasks": [],
                "summary": empty_summary,
            },
            "next_action": "pathfinder" if state["intent"] == "transition" else "market_researcher",
        }

    skills = [
        s for s in data.get("skills", [])
        if isinstance(s, dict) and s.get("name") is not None
    ]
    tasks = [
        t for t in data.get("tasks", [])
        if isinstance(t, str) and t.strip()
    ]

    data["skills"] = skills
    data["tasks"] = tasks

    print(f"   -> Skills retrieved: {len(skills)}")
    print(f"   -> Tasks retrieved: {len(tasks)}")

    connector_prompt = PROMPTS["connector"]["summarize"].format(
        current_role=data.get("title", "Unknown"),
        skills=_skills_to_text(skills),
        tasks=_tasks_to_text(tasks),
    )

    try:
        connector_summary = llm.invoke(connector_prompt).content.strip()
    except Exception as e:
        print(f"LLM ERROR in connector summary: {e}")
        connector_summary = f"{data.get('title', 'This role')} has {len(skills)} skills and {len(tasks)} tasks linked in the graph."

    data["summary"] = connector_summary

    if state["intent"] == "transition":
        return {
            "connector_data": data,
            "next_action": "pathfinder",
        }

    return {
        "connector_data": data,
        "next_action": "market_researcher",
    }


def pathfinder_node(state):
    print("🛤️ Pathfinder: Calculating transition gap...")

    target_role = state.get("target_role")
    if not target_role:
        return {
            "pathfinder_data": {
                "target_role": None,
                "gaps": [],
                "summary": "No target role provided.",
            },
            "next_action": "market_researcher",
        }

    target_job = simple_vector_search(target_role)

    if not target_job:
        print("   -> Target role not found")

        summary = f"Target role '{target_role}' not found in the graph."
        return {
            "pathfinder_data": {
                "target_role": target_role,
                "gaps": [],
                "summary": summary,
            },
            "target_data": None,
            "next_action": "market_researcher",
        }

    print(f"   -> Target matched: {target_job['title']}")

    gap_query = """
    MATCH (target:Occupation {code: $target_code})-[r_target:REQUIRES]->(s:Skill)
    OPTIONAL MATCH (current:Occupation {code: $current_code})-[r_current:REQUIRES]->(s)
    WITH s, r_target.level AS t, COALESCE(r_current.level, 0) AS c
    WHERE t > c
    RETURN s.name AS skill, (t - c) AS gap
    ORDER BY gap DESC LIMIT 5
    """

    gap_data = safe_query(
        gap_query,
        {
            "current_code": state["locator_data"]["code"],
            "target_code": target_job["code"],
        },
    )

    clean_gaps = []
    for g in gap_data:
        if isinstance(g, dict) and g.get("skill") is not None:
            clean_gaps.append(g)

    if not clean_gaps:
        clean_gaps = []

    pathfinder_prompt = PROMPTS["pathfinder"]["summarize"].format(
        current_role=state["locator_data"]["title"],
        target_role=target_job["title"],
        gaps=_gaps_to_text(clean_gaps),
    )

    try:
        pathfinder_summary = llm.invoke(pathfinder_prompt).content.strip()
    except Exception as e:
        print(f"LLM ERROR in pathfinder summary: {e}")
        pathfinder_summary = f"Transition from {state['locator_data']['title']} to {target_job['title']} requires closing {len(clean_gaps)} key skill gaps."

    return {
        "pathfinder_data": {
            "target_role": target_job["title"],
            "gaps": clean_gaps,
            "summary": pathfinder_summary,
        },
        "target_data": target_job,
        "next_action": "market_researcher",
    }


def market_researcher_node(state):
    print("📈 Researcher: Getting market insights...")

    if state["intent"] == "transition":
        target_data = state.get("target_data") or {}
        job = target_data.get("title") or state.get("target_role") or state["locator_data"]["title"]
    else:
        job = state["locator_data"]["title"]

    connector_data = state.get("connector_data") or {}
    skills_text = _skills_to_text(connector_data.get("skills", []))

    prompt = PROMPTS["market_researcher"]["research"].format(
        job_title=job,
        skills=skills_text,
    )

    try:
        insights = llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"LLM ERROR in market_researcher: {e}")
        insights = "Market data unavailable currently."

    return {
        "market_data": insights,
        "next_action": "consultor",
    }


def consultor_node(state):
    print("👼 Consultor: Generating roadmap...")

    connector_data = state.get("connector_data") or {}
    pathfinder_data = state.get("pathfinder_data") or {}
    target_data = state.get("target_data") or {}

    current_role = state.get("locator_data", {}).get("title") if state.get("locator_data") else state.get("current_role")
    target_role = target_data.get("title") or state.get("target_role")

    skills_text = _skills_to_text(connector_data.get("skills", []))
    gaps_text = _gaps_to_text(pathfinder_data.get("gaps", []))
    connector_summary = connector_data.get("summary", "No connector summary available.")
    pathfinder_summary = pathfinder_data.get("summary", "No pathfinder summary available.")
    market_text = state.get("market_data") or "No market data available."

    prompt = PROMPTS["consultor"]["roadmap"].format(
        current_role=current_role or "Unknown",
        target_role=target_role or "Unknown",
        connector_summary=connector_summary,
        pathfinder_summary=pathfinder_summary,
        skills=skills_text,
        gaps=gaps_text,
        market=market_text,
    )

    if state.get("critic_feedback"):
        prompt += "\n\n" + PROMPTS["consultor"]["feedback_loop"].format(
            feedback=state["critic_feedback"]
        )

    response = llm.invoke(prompt)

    return {
        "final_response": response.content.strip(),
        "next_action": "critic",
    }


def critic_node(state):
    print("🧐 Critic: Reviewing response...")

    draft = state["final_response"]

    prompt = PROMPTS["critic"]["review"].format(draft=draft)

    try:
        evaluation = llm.invoke(prompt).content.strip()
        score_part = evaluation.split("SCORE:")[1].split("\n")[0].strip()
        score = int(score_part)
        feedback = evaluation.split("FEEDBACK:")[1].strip()
    except Exception as e:
        print(f"LLM ERROR in critic: {e}")
        score, feedback = 10, "APPROVED"

    if score < 9:
        return {
            "critic_feedback": feedback,
            "next_action": "consultor",
        }

    return {"next_action": "end"}