# Bass Fishing App

Bass lure inventory tracker with AI recommendations: users log the lures they own, enter fishing conditions, and get recommendations drawn from their own inventory. It's a portfolio project, so clean code, a live deployment, and a clear technical story matter.

The full plan, decisions, and timeline are in `docs/PROJECT_PLAN.md`. Read it before starting significant work, and keep it updated when decisions change.

## Status
Planning and brainstorming. No code yet.

## Stack (decided)
- Backend: FastAPI (Python)
- Database: PostgreSQL + pgvector (embeddings live in the same DB)
- Frontend: React
- Web first; a mobile app is a stretch goal only, so the backend is a JSON API that a mobile client can reuse unchanged

## Recommendation approach
RAG, not a trained model. A hand-curated knowledge base of 50–150 bass-fishing entries is embedded into pgvector. At request time, retrieve the entries relevant to the conditions and pass them plus the user's lure inventory to an LLM, which recommends lures the user actually owns.

## Key decisions (details and reasoning in the plan)
- AI: Claude API for generation, Voyage AI for embeddings
- Auth: hand-written JWT in FastAPI (no auth library or hosted auth)
- Lures use simple attributes (type, brand, color, size, technique, quantity, notes), not detailed action or depth specs
- Recommendations are saved with conditions, result and a "did it work?" rating
- Conditions are entered manually for the MVP; auto-filling weather from Open-Meteo is a stretch goal
- Hosting: Render (API), Neon (Postgres + pgvector), Vercel (frontend)
- Backend layers: routers → services → repositories, Pydantic schemas separate from SQLAlchemy models, all schema changes through Alembic

## Working with Erik
Erik must understand every line of this codebase and be able to explain it in interviews. Learning to direct and correct Claude is also an explicit goal.
- Explain the reasoning and tradeoffs behind every change, not just what changed.
- Keep changes small and reviewable. Don't scaffold whole subsystems in one go.
- Erik hand-writes the core pieces: auth, the pgvector query and prompt assembly. Review and explain these, but don't write them unless Erik asks.
- Suggest decisions with a recommendation; don't make them silently.

## Conventions
- Keep `docs/PROJECT_PLAN.md` in sync when decisions are made or scope changes.
- Record significant decisions as ADRs in `docs/decisions/`.
- Career and resume context is in `docs/CAREER_CONTEXT.md`. It isn't needed for coding tasks.
