from google.genai import types


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def display_state(session_service, app_name, user_id, session_id, label="Current State"):
    """Display the current agent session state in a formatted way."""
    try:
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        state = session.state or {}

        print(f"\n{'-' * 10} {label} {'-' * 10}")

        # Optional: show user name if available
        user_name = state.get("user_name")
        if user_name:
            print(f"👤 User: {user_name}")

        # Show decision
        print(f"🧠 Decision: {state.get('decision', 'None')}")

        # Show original complexity
        print(f"📊 Original Complexity: {state.get('original_complexity', 'None')}")

        # Show optimized complexity
        print(f"🚀 Optimized Complexity: {state.get('optimized_complexity', 'None')}")

        # Show optimized code
        optimized_code = state.get("optimized_code")
        if optimized_code:
            print("💻 Optimized Code:")
            print(f"```python\n{optimized_code}\n```")
        else:
            print("💻 Optimized Code: None")

        # Show explanation
        explanation = state.get("explanation")
        if explanation:
            print("📖 Explanation:")
            print(explanation)
        else:
            print("📖 Explanation: None")

        # Optionally, show reminders if present (like teacher’s code)
        reminders = state.get("reminders")
        if reminders:
            print("📝 Reminders:")
            for idx, reminder in enumerate(reminders, 1):
                print(f"  {idx}. {reminder}")

        print("-" * (22 + len(label)))

    except Exception as e:
        print(f"Error displaying state: {e}")

async def process_agent_response(event):
    print(f"Event ID: {event.id}, Author: {event.author}")

    final_response = None

    if event.content and event.content.parts:
        for part in event.content.parts:
            if getattr(part, "executable_code", None):
                print(
                    f"\n🔧 Agent Generated Code:\n```python\n{part.executable_code.code}\n```"
                )

            elif getattr(part, "code_execution_result", None):
                print(
                    f"\n📤 Code Execution Result:\nOutcome: {part.code_execution_result.outcome}\nOutput:\n{part.code_execution_result.output}"
                )

            elif getattr(part, "tool_response", None):
                print(f"\n🛠 Tool Response:\n{part.tool_response.output}")

            elif getattr(part, "text", None) and part.text.strip():
                print(f"\n📝 Text Chunk:\n{part.text.strip()}")

                if event.is_final_response():
                    final_response = part.text.strip()

    if event.is_final_response():
        if final_response:
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}"
                f"╔══ OPTIMAL AGENT FINAL RESPONSE ════════════════════════"
                f"{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}"
                f"╚════════════════════════════════════════════════════════"
                f"{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}"
                f"No final text response"
                f"{Colors.RESET}\n"
            )

    return final_response

async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Running Query: {query} ---{Colors.RESET}"
    )
    final_response_text = None

    # Display state before processing
    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE processing",
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Process each event and get the final response if available
            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"Error during agent call: {e}")

    # Display state after processing the message
    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER processing",
    )

    return final_response_text