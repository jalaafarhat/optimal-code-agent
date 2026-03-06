import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from google.adk.agents import Agent

def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(
    os.path.join(BASE_DIR, "prompt.md")
)
    
math_agent = Agent(
    name="math_agent",
    model="gemini-2.0-flash",
    description="Stock market math maker agent",
    instruction=instructions,  # your stock prompt with tool rules added
)
