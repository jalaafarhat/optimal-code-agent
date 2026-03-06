import os
from enum import Enum
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field


model=LiteLlm(model="openrouter/openai/gpt-4.1",api_key=os.getenv("OPENROUTER_API_KEY"))

def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(
    os.path.join(BASE_DIR, "prompt.md")
)

    
root_agent = Agent(
    name="optimal_agent",
    model=model,
    description="Optimal code optimization agent",
    instruction=instructions,
   #  ,tools=[google_search]
)