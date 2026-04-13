from typing import TypedDict,Optional,Dict,List,Any

class TalentAngelState(TypedDict,total=False):
    retry_count: int
    next_action: str

    user_query: str
    resume_path: Optional[str]
    resume_text: Optional[str]
    resume_skills: Optional[List[str]]

    current_role: Optional[str]
    target_role: Optional[str]
    intent: Optional[str]
    needs_clarification: bool

    locator_data: Optional[Dict[str, Any]]
    target_data: Optional[Dict[str, Any]]
    connector_data: Optional[Dict[str, Any]]

    graph_gap_data: Optional[Dict[str, Any]]      
    market_research_data: Optional[Dict[str, Any]] 
    social_data: Optional[Dict[str, Any]]          
    media_data: Optional[Dict[str, Any]]           
    academic_data: Optional[Dict[str, Any]]        
    project_data: Optional[Dict[str, Any]]  

    supervisor_routes: Optional[List[str]]
    final_response: Optional[str]
    critic_feedback: Optional[str]       
