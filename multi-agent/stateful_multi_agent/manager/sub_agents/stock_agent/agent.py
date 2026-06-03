import os

from google.adk.agents import Agent

from config import GEMINI_MODEL

from .subagentss.analyzer.tools.marketData import (
    calculate_profit_scenario,
    get_analyst_recommendations,
    get_current_price,
    get_multiple_prices,
    get_price_history,
    get_stock_fundamentals,
    get_technical_summary,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


instructions = load_instructions(os.path.join(BASE_DIR, "prompt.md"))

stock_agent = Agent(
    name="stock_agent",
    model=GEMINI_MODEL,
    description="Stock market analyst for equities, ETFs, and public companies",
    instruction=instructions,
    tools=[
        get_current_price,
        get_price_history,
        get_multiple_prices,
        get_stock_fundamentals,
        get_analyst_recommendations,
        get_technical_summary,
        calculate_profit_scenario,
    ],
)
