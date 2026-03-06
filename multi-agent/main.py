import asyncio

# Import the main customer service agent
from stateful_multi_agent.manager.agent import root_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import add_user_query_to_history, call_agent_async

load_dotenv()

# ===== PART 1: Initialize In-Memory Session Service =====
session_service = InMemorySessionService()

# ===== PART 2: Define Initial State =====
# UPDATED: subscription-based state (no courses)
initial_state = {
    "user_name": "Jalaa Farhat",
    "subscription_status": False,
    "subscription_plan": None,
    "subscription_expiry": None,
    "last_purchase_id": None,
    "interaction_history": [],
}


async def main_async():
    APP_NAME = "AI Multi-Agent Platform"
    USER_ID = "jalaa_farhat"

    # ===== PART 3: Session Creation =====
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"Created new session: {SESSION_ID}")

    # ===== PART 4: Agent Runner Setup =====
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to AI Platform Chat!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, user_input
        )

        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    # ===== PART 6: Final State Inspection =====
    final_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()