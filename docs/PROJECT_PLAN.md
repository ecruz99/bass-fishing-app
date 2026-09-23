# Project Plan: Bass Lure Inventory & AI Recommendation App

## Purpose
A portfolio project that shows full-stack and AI-integration skills. Users log the lures they own, enter fishing conditions, and get AI recommendations chosen only from their own inventory. It's open to other users, so it needs real accounts and auth.

The job-search reasoning and resume framing are in `docs/CAREER_CONTEXT.md`.

## Personal Growth Goals
Shipping the app is only half the point. The project is also a deliberate way for Erik to get better as a software engineer. Each goal below comes with concrete practices so progress can be checked.

### 1. Understand and explain every part of the codebase
Nothing gets merged that Erik can't explain line by line. By the end, Erik should be able to walk an interviewer through any file, any design decision and any tradeoff.
- **Hand-write the core pieces:** password hashing and JWT auth, the pgvector similarity query, and the prompt assembly for the LLM. Claude can review and explain these, but Erik writes them.
- **Explain-back rule:** after each feature, Erik explains it out loud or in writing (what it does, why it's built that way, and what the alternatives were) before moving on. If the explanation has gaps, go back to the code.
- **Walkthrough notes:** keep short notes in `docs/walkthroughs/` for each major flow (signup to login to an authenticated request; adding a lure; a recommendation request from start to finish).
- **Interview question bank:** keep a running list of questions an interviewer might ask ("Why pgvector instead of Pinecone?", "How do you keep JWTs from being forged?", "What happens if the LLM recommends a lure the user doesn't own?"), and practice answering them. It stays private: `docs/INTERVIEW_PREP.md` is gitignored and backed up in Erik's notes app.

### 2. Architecture and design
Build the backend the way a professional team would, and be able to explain why it's organized that way.
- **Layered backend:** `routers/` (HTTP only) → `services/` (business logic) → `repositories/` (database access), with Pydantic `schemas/` kept separate from SQLAlchemy `models/`. Dependencies are passed in with FastAPI `Depends`.
- **Migrations:** every schema change goes through Alembic. Never edit the database by hand.
- **API design:** RESTful resources under `/api/v1`, a consistent error response shape, correct status codes, and pagination on list endpoints.
- **Decision records:** write a short ADR (Architecture Decision Record: context, decision, alternatives, consequences) in `docs/decisions/` for each significant choice. The decisions below are the first batch to write up.
- **Design before code:** for each feature, sketch the endpoints, data shapes and edge cases before writing any code.
- **Testable by design:** services should be unit-testable with pytest without a running server. This is the proof that the layering works.

### 3. Use Claude Code effectively, and course-correct it
Learn to use AI coding tools the way a strong engineer would: as an assistant Erik directs and checks, not an autopilot.
- **Maintain `CLAUDE.md`:** keep it short and current. When Claude makes the same mistake twice, add a rule to prevent it.
- **Write at least one custom skill:** for a workflow that repeats. Candidates: adding and validating a knowledge base entry, generating an ADR from a decision, or a "walk me through this change" explainer.
- **Plan before big changes:** use plan mode for anything that touches more than one or two files, and read the plan critically before approving it.
- **Review every diff:** read each change before accepting it. If Claude's reasoning isn't clear, ask why before accepting.
- **Know how to recover:** commit before each Claude session so there's a clean point to go back to. Interrupt with Esc when it's heading the wrong way, use `/rewind` to undo, and correct it explicitly ("don't do X, do Y because Z") instead of re-rolling the same prompt.
- **Log the misfires:** keep brief notes in `docs/CLAUDE_LESSONS.md` on times Claude went wrong: what happened, how Erik caught it, and what fixed it. This also makes a good interview story about using AI tools responsibly.

## Decisions

**Core concept:** A lure inventory tracker for bass fishing, with an AI-powered recommendation feature that suggests lures from the user's own inventory based on fishing conditions.

**Stack:**
- Backend: FastAPI (Python)
- Database: PostgreSQL with the pgvector extension, so embeddings live in the same database instead of a separate vector store
- Frontend: React
- Web first. The backend is a JSON API that a future mobile client could reuse unchanged. A mobile app is a **stretch goal only** and not part of the core scope.

**Recommendation approach:** RAG (Retrieval-Augmented Generation), not a custom-trained ML model.
- Reasoning: training a real ML model needs labeled data Erik doesn't have and would take up most of the timeline. RAG is achievable, closer to what employers are hiring for now, and makes a stronger interview story ("I understand embeddings, vector search and prompt engineering", not just "I called an API").
- Recommendation logic lives in the retrieved knowledge base, not in hardcoded if/else rules.

**AI providers:** Claude (Anthropic API) generates the recommendations. Voyage AI creates the embeddings; Anthropic recommends it, since Anthropic has no embeddings API of its own. That means two API keys, both kept in environment variables and never committed.

**Auth:** Written by hand with JWT in FastAPI: password hashing (argon2 or bcrypt via `pwdlib`, the library the current FastAPI docs use), short-lived access tokens, and a `get_current_user` dependency. Chosen over FastAPI-Users or a hosted service because Erik should understand and be able to explain every line, and a mobile client could reuse it.

**Condition input:** Manual form entry for the MVP. Auto-filling from Open-Meteo (free, no API key) using the user's location is a stretch goal. It shouldn't hold up the core RAG pipeline.

**Conditions considered:** Water clarity, season, water temperature, air temperature, wind, barometric pressure (trend), and sky (sunny, partly cloudy or overcast).

**Lure attribute detail level:** Simple categories (type: jig/spinnerbait/crankbait and so on, brand, color, size, technique), not detailed action or depth-range specs. This keeps the schema manageable. Knowledge base entries should be written at the same level of detail, because the LLM can only match on attributes the lures actually store.

**Quantity:** The lures table has a `quantity` column (integer, defaults to 1), because people often own several of the same lure.

**Recommendation history:** Saved. Each recommendation stores the conditions, the output and an optional "did it work?" rating from the user. This adds about a day of work. It gives users a history of what worked, gives the project a feedback loop to talk about, and the ratings could later be used to improve retrieval.

**Knowledge base authoring:** Erik drafts every entry from Erik's own fishing knowledge, and Claude refines it for clarity, gaps and consistent format. The domain knowledge stays Erik's to explain.

**Hosting:**
- Backend: Render (free tier sleeps when idle, so the first request is slow. That's acceptable for a portfolio app; note it in the README.)
- Database: Neon Postgres (free tier, supports pgvector)
- Frontend: Vercel

## Database Schema (finalize column types in Milestone 1)
- `users`: id, email (unique), hashed_password, created_at
- `lures`: id, user_id (FK → users), name, type, brand, color, size, technique, quantity (default 1), notes, created_at, updated_at
- `knowledge_base_entries`: id, title, content (text), category (e.g. clarity, season, structure, weather), embedding (vector, whose dimension must match the Voyage model's output), created_at. Shared by all users; not per-user.
- `recommendations`: id, user_id (FK → users), conditions (JSONB), retrieved_entry_ids (int[]), result (JSONB: the recommended lures with their reasoning, saved as a snapshot so the history still reads correctly if a lure is later deleted), worked (nullable boolean: the "did it work?" rating), created_at

Why JSONB for conditions and results: the set of conditions will probably change while the project is being built, and history rows are only ever read as a whole, never filtered by individual fields. If filtering by field becomes necessary later, move those fields into real columns with a migration.

## Recommendation Pipeline
1. The user submits the conditions form, and the request goes to `POST /api/v1/recommendations`.
2. The service builds a text query from the conditions (for example "stained water, early spring, 52°F water, windy, falling pressure, overcast").
3. The query is embedded with Voyage AI.
4. pgvector returns the top-k most similar knowledge base entries by cosine distance (start with k=5 and tune it).
5. The prompt sent to Claude contains the conditions, the retrieved entries and the user's lure inventory, with instructions to recommend **only** lures from that inventory and to explain why each one fits.
6. Claude returns structured output (lure IDs plus reasoning). The service checks that every returned ID belongs to the user's inventory, so the model can't recommend a lure the user doesn't own.
7. The service saves a `recommendations` row and returns the result.
8. Later, the user can rate it with `PATCH /api/v1/recommendations/{id}` (`worked: true/false`).

## API Sketch
- Auth: `POST /api/v1/auth/signup`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- Lures: `GET/POST /api/v1/lures`, `GET/PATCH/DELETE /api/v1/lures/{id}`, all limited to the current user
- Recommendations: `POST /api/v1/recommendations`, `GET /api/v1/recommendations` (history), `PATCH /api/v1/recommendations/{id}` (rating)
- Knowledge base: loaded by a seed/admin script, not a public endpoint

## Milestones
Work in order, with no fixed dates. Erik works on the app as much as possible, so progress is measured by milestones finished, not weeks spent. Each milestone has a **Done when** checklist; don't start the next one until everything on it is true.

Every milestone also includes:
- An ADR for each significant decision made along the way
- A walkthrough note in `docs/walkthroughs/` for any new flow
- New entries in the interview question bank
- Passing the explain-back rule: Erik can explain everything built in that milestone without looking at the code

### Milestone 1: Backend foundation and auth
Set up the repo structure, the layered backend skeleton, Alembic, and a local Postgres with pgvector. Hand-write signup, login and the JWT dependency.
- **Decide:** where the frontend stores tokens (in memory with an `Authorization` header, or an httpOnly cookie). Look up the XSS/CSRF tradeoff and write an ADR.
- **Write ADRs:** stack, RAG vs. a trained model, hand-written auth.
- **Done when:** a user can sign up, log in and call a protected endpoint; migrations run cleanly from an empty database; the auth logic has pytest tests.

### Milestone 2: Lure inventory API
CRUD endpoints for lures, limited to the current user.
- **Decide:** should `type` and `technique` be fixed lists (enums or lookup tables) or free text? Recommendation: fixed lists. Consistent values make it much easier for the LLM to match lures to knowledge base entries, while free text like "crank" vs. "crankbait" gets messy.
- **Done when:** all lure endpoints work with validation, pagination and consistent errors; one user can never read or change another user's lures (with a test that proves it); service-layer tests pass.

### Milestone 3: Frontend inventory
Scaffold the React app. Build the signup and login pages and the inventory screens, working end to end.
- **Decide:** frontend tooling (Vite) and whether to use TypeScript. TypeScript is worth considering because it's widely expected in industry.
- **Done when:** a new user can sign up, log in, and add, edit and delete lures in the browser against the real API.
- **Check-in (Claude: ask Erik when this milestone is finished):** the current decision is to deploy only in Milestone 7, once the app is ready. Ask whether Erik still wants that, or would now rather do a basic deploy of auth and inventory to get a live link sooner.

### Milestone 4: Knowledge base and embeddings
Erik drafts the knowledge base (50 to 150 entries) and Claude refines it. Build the embedding and seed pipeline with Voyage AI and pgvector.
- **Decide:** which Voyage embedding model to use. This sets the dimension of the `vector` column.
- **Claude skill:** write the first custom skill here. A strong candidate: validating and adding knowledge base entries.
- **Done when:** all entries are embedded and stored; a manual similarity query for a sample set of conditions returns entries that make sense; the seed script can be re-run safely.

### Milestone 5: Recommendation pipeline
Build retrieval and the Claude generation step, including checking the output against the inventory. Build the recommendation endpoints and save history (ADR: JSONB for history).
- **Decide:** which Claude model to use, weighing cost against quality on this task. Compare a few real outputs before committing.
- **Done when:** `POST /recommendations` returns reasoned picks drawn only from the user's inventory; results are saved; ratings work; it's been tested against realistic combinations of conditions, including an empty or tiny inventory.

### Milestone 6: Frontend recommendations
The conditions form, the results display, the history view and the "did it work?" rating.
- **Done when:** the whole flow works in the browser, from entering conditions to seeing results to rating them later from history.

### Milestone 7: Deploy and polish
Polish the UI, deploy to Render, Neon and Vercel, and write the README (including an architecture diagram and a note about the free tier's slow first request).
- **Done when:** the live URL works for a brand-new user; secrets are only in environment variables; the README explains how to run the app locally and how it works.

### Milestone 8: Showcase
Write a short demo write-up and consider a demo video for LinkedIn. Do a full mock-interview walkthrough of the codebase, and write the resume bullets (see `docs/CAREER_CONTEXT.md`).
- **Done when:** Erik can give a 5-minute walkthrough of the app and a 15-minute deep dive into the architecture, and answer every question in the interview question bank.

## Stretch Goals (after the core app ships)
- Auto-fill conditions from Open-Meteo using the user's location
- Use the "did it work?" ratings to improve retrieval or re-rank recommendations
- A mobile client that reuses the same API
- Photo upload for lures
