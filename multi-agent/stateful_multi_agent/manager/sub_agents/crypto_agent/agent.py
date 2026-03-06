import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from google.adk.agents import Agent
from google.adk.tools import google_search

def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(
    os.path.join(BASE_DIR, "prompt.md")
)
    
crypto_agent = Agent(
    name="crypto_agent",
    model="gemini-2.0-flash",
    description="Crypto market analysis agent with live data and analyst-backed predictions",
    instruction=instructions,  # your stock prompt with tool rules added
    tools=[
        google_search,
    ],
)
