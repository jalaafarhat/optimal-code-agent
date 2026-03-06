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

class Decision(str, Enum):
    OPTIMIZATION_APPLIED = "optimization_applied"
    ALREADY_OPTIMAL = "already_optimal"
    NO_SAFE_OPTIMIZATION = "no_safe_optimization"

class OptimizationResult(BaseModel):
    decision: Decision = Field(
        description="Whether a real optimization was applied"
    )
    original_complexity: str = Field(
        description="Time and space complexity of the original code"
    )
    optimized_complexity: str = Field(
        description="Time and space complexity after optimization"
    )
    optimized_code: str | None = Field(
        description="Optimized code if and only if decision == OPTIMIZATION_APPLIED"
    )
    explanation: str = Field(
        description="Clear justification of the decision"
    )
    
root_agent = Agent(
    name="structured_optimal_agent",
    model=model,
    description="Optimal code optimization agent",
    instruction=instructions,
    output_schema=OptimizationResult,
    output_key="optimization_result"
   #  ,tools=[google_search]
)
