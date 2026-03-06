import os
from enum import Enum
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field
from google.adk.tools.tool_context import ToolContext



model=LiteLlm(model="openrouter/openai/gpt-4.1",api_key=os.getenv("OPENROUTER_API_KEY"))

def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(
    os.path.join(BASE_DIR, "prompt.md")
)

def update_code_state(
    decision: str,
    original: str,
    optimized: str,
    code: str,
    explanation: str,
    tool_context: ToolContext
) -> dict:
    """Update the session state with optimization results."""
    tool_context.state["decision"] = decision
    tool_context.state["original_complexity"] = original
    tool_context.state["optimized_complexity"] = optimized
    tool_context.state["optimized_code"] = code
    tool_context.state["explanation"] = explanation

    return {
        "action": "update_code_state",
        "message": f"Updated code optimization state with decision: {decision}"
    }
    
root_agent = Agent(
    name="optimal_agent",
    model=model,
    description="Optimal code optimization agent",
    instruction=instructions,
   tools=[update_code_state]
)
