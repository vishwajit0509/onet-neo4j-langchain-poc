# run_chat.py

import uuid
from src.agents.graph import talent_app


def start_career_session():
    # Unique session ID (for memory)
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print("\n" + "=" * 50)
    print("🌟 WELCOME TO TALENT ANGEL 🌟")
    print("=" * 50)
    print("Type 'exit' to end the session.\n")

    while True:
        user_input = input("👤 You: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\n👼 Angel: Good luck on your journey, Vishwajit! 🚀")
            break

        if not user_input:
            print("⚠️ Please enter a valid query.\n")
            continue

        inputs = {"user_query": user_input}

        try:
            final_state = talent_app.invoke(inputs, config=config)

            # ✅ SAFE RESPONSE HANDLING
            response = final_state.get("final_response")

            if not response:
                print("\n⚠️ Angel could not generate a response.\n")
                print("🔍 Debug State:", final_state)
            else:
                print(f"\n👼 Angel: {response}\n")

            print("-" * 40)

        except Exception as e:
            print("\n❌ Error in the Angel Network")
            print("🔍 Details:", str(e))
            print("-" * 40)


if __name__ == "__main__":
    start_career_session()