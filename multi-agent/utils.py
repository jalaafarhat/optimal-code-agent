from datetime import datetime
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import google_search




class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"


def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    session = session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    interaction_history = session.state.get("interaction_history", [])

    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    interaction_history.append(entry)

    updated_state = session.state.copy()
    updated_state["interaction_history"] = interaction_history

    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=updated_state,
    )


def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {"action": "user_query", "query": query},
    )


def add_agent_response_to_history(
    session_service, app_name, user_id, session_id, agent_name, response
):
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )


def display_state(session_service, app_name, user_id, session_id, label="State"):
    session = session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    print(f"\n{'-' * 10} {label} {'-' * 10}")

    state = session.state

    print(f"👤 User: {state.get('user_name', 'Unknown')}")

    # ===== SUBSCRIPTION INFO =====
    subscribed = state.get("subscription_status", False)
    plan = state.get("subscription_plan")
    expiry = state.get("subscription_expiry")

    if subscribed:
        print(f"🔐 Subscription: ACTIVE ({plan})")
        print(f"⏳ Expiry: {expiry}")
    else:
        print("🔐 Subscription: INACTIVE")

    # ===== INTERACTION HISTORY =====
    history = state.get("interaction_history", [])
    if history:
        print("📝 Interaction History:")
        for i, item in enumerate(history, 1):
            action = item.get("action")
            ts = item.get("timestamp", "N/A")

            if action == "user_query":
                print(f'  {i}. User @ {ts}: "{item.get("query")}"')
            elif action == "agent_response":
                agent = item.get("agent", "unknown")
                resp = item.get("response", "")
                if len(resp) > 100:
                    resp = resp[:97] + "..."
                print(f'  {i}. {agent} @ {ts}: "{resp}"')
    else:
        print("📝 Interaction History: None")

    print("-" * (22 + len(label)))


async def process_agent_response(event):
    final_response = None

    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")

    if event.is_final_response():
        if event.content and event.content.parts:
            text = event.content.parts[0].text.strip()
            final_response = text
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}"
                f"╔══ AGENT RESPONSE ═══════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}"
                f"╚═════════════════════════════════════════════════{Colors.RESET}\n"
            )

    return final_response


async def call_agent_async(runner, user_id, session_id, query):
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print(
        f"\n{Colors.BG_GREEN}{Colors.BOLD}"
        f"--- Running Query: {query} ---{Colors.RESET}"
    )

    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE processing",
    )

    final_response_text = None
    agent_name = None

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.author:
            agent_name = event.author

        response = await process_agent_response(event)
        if response:
            final_response_text = response

    if final_response_text and agent_name:
        add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            agent_name,
            final_response_text,
        )

    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER processing",
    )

    print(f"{Colors.YELLOW}{'-' * 30}{Colors.RESET}")
    return final_response_text

def require_subscription(tool_context: ToolContext):
    if tool_context.state.get("is_subscribed") is not True:
        raise PermissionError(
            "Subscription required. Please subscribe to access this feature."
        )
# Wrap google_search for subscription enforcement
def google_search_subscribed(query: str, tool_context: ToolContext):
    require_subscription(tool_context)
    return google_search(query)    