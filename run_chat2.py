import uuid
import os
import sys

from src.agent2.orchestrator import carrer_forge_app 

def test_modular_agent():
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print("🔥 CareerForge V2: Modular Orchestrator Test")
    print(f"Session Thread ID: {thread_id}")
    print("-" * 50)

    
    query = input("Enter your career query: ")
    
    
    resume_name = "Vishwajit Sarak-Patil CV .pdf"
    resume_path = os.path.join("data", "raw", resume_name)
    
    use_resume = False
    if os.path.exists(resume_path):
        choice = input(f"📄 Found resume '{resume_name}'. Use it? (y/n): ").lower()
        use_resume = (choice == 'y')
    else:
        print(f"⚠️ Resume not found at {resume_path}. Running without PDF.")

    # 3. Initialize the State
    initial_state = {
        "user_query": query,
        "resume_path": resume_path if use_resume else None,
        "retry_count": 0
    }

    # 4. Stream Execution
    print("\n🚀 Initializing Graph Pipeline...")
    print("=" * 50)

    try:
        
        for event in carrer_forge_app.stream(initial_state, config=config):
            for node_name, state_update in event.items():
                print(f"✅ Node Finished: [{node_name}]")
                
                
                if "next_action" in state_update:
                    print(f"   ↳ Transitioning to: {state_update['next_action']}")

                
                if "final_response" in state_update and state_update["final_response"]:
                    print("\n" + "✨" * 15)
                    print("ANGEL STRATEGY RECEIVED:")
                    print("✨" * 15)
                    print(state_update["final_response"])
                    print("\n" + "=" * 50)

    except Exception as e:
        print(f"\n❌ CRITICAL SYSTEM ERROR: {e}")
        print("Check your API keys and Neo4j connection in .env")

if __name__ == "__main__":
    test_modular_agent()