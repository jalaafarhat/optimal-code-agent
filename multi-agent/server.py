"""
FastAPI server for the multi-agent financial platform.
Run: uvicorn server:app --reload --port 8000
"""

import asyncio
import os
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from config import GEMINI_MODEL
import telemetry_patch

telemetry_patch.apply()

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

APP_NAME = "FinAgent Platform"
session_service = InMemorySessionService()
runner: Runner | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global runner
    from stateful_multi_agent.manager.agent import root_agent

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    yield


app = FastAPI(
    title="FinAgent Multi-Agent API",
    description="Financial analysis platform powered by specialized AI agents",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:4201",
        "http://127.0.0.1:4201",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "web_user"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent: str | None = None


class SessionResponse(BaseModel):
    session_id: str
    user_id: str


def _extract_response_text(event) -> str | None:
    if not event.content or not event.content.parts:
        return None
    chunks: list[str] = []
    for part in event.content.parts:
        if getattr(part, "text", None) and part.text.strip():
            chunks.append(part.text.strip())
    return "\n".join(chunks) if chunks else None


AGENTS_INFO = [
    {
        "id": "stock_agent",
        "name": "Stock Analyst",
        "description": "Analyzes equities, ETFs, and public companies with live market data",
        "icon": "trending_up",
        "examples": ["Analyze Apple stock", "Compare MSFT and GOOGL", "Tesla price target"],
    },
    {
        "id": "crypto_agent",
        "name": "Crypto Analyst",
        "description": "Tracks cryptocurrency prices, trends, and digital asset performance",
        "icon": "currency_bitcoin",
        "examples": ["Bitcoin price today", "Compare BTC and ETH", "Solana analysis"],
    },
    {
        "id": "business_agent",
        "name": "Business Strategist",
        "description": "Finds side business opportunities, ROI estimates, and passive income ideas",
        "icon": "business_center",
        "examples": ["Side business with $5000", "Vending machine ROI", "Passive income ideas"],
    },
]


@app.get("/api/health")
def health():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    return {
        "status": "ok",
        "app": APP_NAME,
        "model": GEMINI_MODEL,
        "api_key_configured": bool(api_key),
    }


@app.get("/api/agents")
def list_agents():
    return AGENTS_INFO


@app.post("/api/sessions", response_model=SessionResponse)
def create_session(user_id: str = "web_user"):
    session_id = str(uuid.uuid4())
    session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
        state={
            "user_name": "Web User",
            "subscription_status": False,
            "interaction_history": [],
        },
    )
    return SessionResponse(session_id=session_id, user_id=user_id)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not runner:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    user_id = req.user_id
    session_id = req.session_id

    if not session_id:
        session_id = str(uuid.uuid4())
        session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state={"interaction_history": []},
        )
    elif not session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    ):
        session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state={"interaction_history": []},
        )

    content = types.Content(
        role="user", parts=[types.Part(text=req.message)]
    )

    final_text = None
    agent_name = None

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.author:
                agent_name = event.author
            if event.is_final_response():
                text = _extract_response_text(event)
                if text:
                    final_text = text
    except Exception as exc:
        error_msg = str(exc)
        if "404 NOT_FOUND" in error_msg and "model" in error_msg.lower():
            raise HTTPException(
                status_code=502,
                detail=f"Gemini model '{GEMINI_MODEL}' unavailable. Set GEMINI_MODEL in .env (try gemini-2.5-flash).",
            ) from exc
        if "API key" in error_msg or "PERMISSION_DENIED" in error_msg or "401" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Google API key missing or invalid. Set GOOGLE_API_KEY in your .env file.",
            ) from exc
        raise HTTPException(status_code=500, detail=f"Agent error: {error_msg}") from exc

    if not final_text:
        final_text = "I couldn't generate a response. Please try again."

    return ChatResponse(
        response=final_text,
        session_id=session_id,
        agent=agent_name,
    )
