import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from google.adk.agents import Agent
from .tools.marketData import get_current_price,get_price_history

def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(
    os.path.join(BASE_DIR, "prompt.md")
)
    
analyzer_agent = Agent(
    name="analyze_agent",
    model="gemini-2.0-flash",
    description="Stock market analysis agent with live data and analyst-backed predictions",
    instruction=instructions,  # your stock prompt with tool rules added
    tools=[
        get_current_price,
        get_price_history
    ]
)
