# FinAgent — Multi-Agent Financial Analysis Platform

AI-powered financial analysis with specialized agents for stocks, crypto, and business opportunities. Includes an Angular web frontend and FastAPI backend.

## Architecture

```
User → Angular Frontend (port 4200)
         ↓ HTTP
       FastAPI Server (port 8000)
         ↓
       Manager Agent (routes by intent)
         ├── stock_agent   — equities, ETFs, fundamentals
         ├── crypto_agent  — cryptocurrencies, tokens
         └── business_agent — side business, ROI, passive income
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google AI API key (Gemini) — set in `.env`
- Optional: `SERPAPI_API_KEY` for business agent machine search

## Setup

```bash
# Python backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Create .env in project root
# GOOGLE_API_KEY=your_key
# GEMINI_MODEL=gemini-2.5-flash   (optional, default shown)
# SERPAPI_API_KEY=your_key   (optional, for business agent)

# Angular frontend
cd frontend
npm install
```

## Run

**Terminal 1 — Backend:**
```bash
cd multi-agent
..\.venv\Scripts\activate
uvicorn server:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm start
```

Open [http://localhost:4200](http://localhost:4200)

## CLI Mode (optional)

```bash
cd multi-agent
python main.py
```

## Agent Routing

The manager agent classifies each message and delegates to exactly one specialist:

| Question type | Agent |
|---|---|
| Stocks, ETFs, public companies | `stock_agent` |
| Bitcoin, crypto, tokens | `crypto_agent` |
| Side business, passive income | `business_agent` |

Stock and crypto agents are never called together unless the user explicitly asks about both.

## Stock Analysis Tools

- `get_current_price` — live price via yfinance + scraping fallbacks
- `get_stock_fundamentals` — P/E, market cap, revenue, sector
- `get_analyst_recommendations` — consensus targets and ratings
- `get_technical_summary` — moving averages, returns, volatility
- `get_price_history` — historical OHLCV data
- `calculate_profit_scenario` — investment profit calculator

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/agents` | List agent info |
| POST | `/api/sessions` | Create chat session |
| POST | `/api/chat` | Send message, get response |
