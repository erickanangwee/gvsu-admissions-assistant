# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI)
```bash
# Activate virtual environment first (Windows)
venv\Scripts\activate

# Run API server (from project root)
uvicorn api.main:app --reload

# API runs at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
npm run build
```

### Docker (full stack with PostgreSQL)
```bash
docker compose up --build
# API: http://localhost:8000, Frontend: http://localhost:80
```

### First-time setup
```bash
python setup.py   # creates venv, installs deps, scaffolds .env template
```

## Environment Variables

Required in `.env` at project root:
```
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
DATABASE_URL=sqlite:///./gvsu_chatbot.db  # or postgresql:// for prod
```

## Architecture

This is a **live-search RAG chatbot** — it has no offline vector store. Every user question triggers a real-time Google Custom Search restricted to `gvsu.edu`, fetches and parses the top pages, then passes the extracted text as context to Claude.

**Request flow:**
```
User message → POST /api/v1/chat
  → answer_engine.answer()
    → search_engine.search_and_fetch()   # Google CSE → fetch top N pages
    → generate_answer()                  # assemble context block → Claude API
  → QueryLog written to DB
  → ChatResponse returned to frontend
```

**Key modules:**
- `config.py` — single source of truth for all env vars and tuneable constants (`MAX_SEARCH_RESULTS`, `MAX_PAGE_CHARS`, `MAX_CONVERSATION_TURNS`, `LLM_MODEL`)
- `api/search_engine.py` — Google Custom Search + BeautifulSoup page scraper; strips nav/header/footer/script tags and caps text at `MAX_PAGE_CHARS`
- `api/answer_engine.py` — builds numbered context blocks, manages conversation history window, calls Anthropic SDK; defines `SYSTEM_PROMPT`
- `api/routes/chat.py` — single FastAPI route; logs every query to `QueryLog` with latency, pages fetched, and fallback flag
- `api/database.py` — SQLAlchemy setup; `QueryLog` is the only table; defaults to SQLite locally, PostgreSQL in Docker
- `api/models.py` — Pydantic `ChatRequest` / `ChatResponse` shapes the API contract
- `frontend/src/App.jsx` — single-file React app; manages session UUID, conversation history (last 10 turns sent to API), topic chip filter

**No tests exist yet.** The `evaluation/` directory is scaffolded but empty.

**CORS:** The API allows `http://localhost:5173` (Vite dev) and a placeholder production domain — update `main.py` before deploying.

**SQLite vs PostgreSQL:** The Docker compose wires PostgreSQL automatically via `DATABASE_URL`. Local dev uses SQLite (`gvsu_chatbot.db`) by default.
