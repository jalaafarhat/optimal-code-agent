import os

from google.adk.agents import Agent
from google.adk.tools import google_search

from config import GEMINI_MODEL
from .tools.cryptoData import compare_cryptos, get_crypto_history, get_crypto_price

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


instructions = load_instructions(os.path.join(BASE_DIR, "prompt.md"))

crypto_agent = Agent(
    name="crypto_agent",
    model=GEMINI_MODEL,
    description="Cryptocurrency market analyst for digital assets and tokens",
    instruction=instructions,
    tools=[
        get_crypto_price,
        get_crypto_history,
        compare_cryptos,
        google_search,
    ],
)
