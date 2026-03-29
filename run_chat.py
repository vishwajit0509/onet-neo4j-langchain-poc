# run_chat.py
import uuid
from src.agents.graph import talent_app

def start_career_session():
    # A unique thread_id allows the MemorySaver to track this specific conversation
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    print("\n" + "="*50)
    print("🌟 WELCOME TO TALENT ANGEL: YOUR GRAPH-POWERED CAREER STRATEGIST 🌟")
    print("="*50)
    print("Type 'exit' to end the session.\n")

    while True:
        user_input = input("👤 You: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\n👼 Angel: Good luck on your journey, Vishwajit! Closing session...")
            break

        # Initial state for the graph
        inputs = {"user_query": user_input}
        
        try:
            # We use .invoke to run the full graph logic including the Critic loop
            final_state = talent_app.invoke(inputs, config=config)
            
            print(f"\n👼 Angel: {final_state['final_response']}\n")
            print("-" * 30)
            
        except Exception as e:
            print(f"\n❌ Error in the Angel Network: {e}")

if __name__ == "__main__":
    start_career_session()