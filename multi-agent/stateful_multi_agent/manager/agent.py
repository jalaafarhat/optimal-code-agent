from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.business_agent.agent import business_agent
from .sub_agents.stock_agent.agent import stock_agent
from .sub_agents.crypto_agent.agent import crypto_agent

from datetime import datetime

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_current_time() -> dict:
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(
    os.path.join(BASE_DIR, "prompt.md")
)

root_agent  = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Manager agent",
    instruction=instructions,  # optional additional prompt instructions
    tools=[
        # Tools from agents that use google_search or external data
        AgentTool(stock_agent),        # stock_agent tools (e.g., get_stock_price)
        AgentTool(business_agent),     # business_agent tools (e.g., ROI estimators, google_search)
        AgentTool(crypto_agent),
        get_current_time
    ],
)
