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
RAG, not a trained model. A hand-curated knowledge base is embedded into pgvector. It starts with 50–150 of Erik's own entries and grows in stages (personal recommendations plus transcribed charts, facts only, each entry tagged with conditions and source). At request time, retrieve the entries relevant to the conditions and pass them plus the user's lure inventory to an LLM, which recommends lures the user actually owns.

RAG has to earn its place: an eval harness (Milestone 6, ADR 0001) compares no knowledge base, the whole knowledge base in the prompt, vector top-k, and metadata filter + vector, using Erik's scenarios with a held-out set.

Each recommended lure cites the knowledge base entries it's based on. Citations are validated against the retrieved entries (like lure ownership), shown in the UI as titles with source labels, and snapshotted into history. Entry content is never sent to the client; the API returns only titles, sources and scores. Entries have a stable `slug`, so re-seeding never changes their IDs.

## Key decisions (details and reasoning in the plan)
- AI: Claude API for generation, Voyage AI for embeddings
- Auth: hand-written JWT in FastAPI (no auth framework or hosted auth; PyJWT and pwdlib only), with Argon2 via `pwdlib`. Revocation uses `users.token_version`; change password and log out everywhere increment it. Login and signup are rate limited per IP and per email from Milestone 1. Refresh tokens, password reset and email verification are post-launch stretch goals
- Lures use simple attributes (type, brand, color, size, technique, quantity, notes), not detailed action or depth specs
- Recommendations are saved with conditions, result and a "did it work?" rating
- Shared lure catalog: a hand-seeded catalog of 30 to 50 lures before launch (Milestone 8); a scraped catalog is a post-launch v2 (official data feeds first, scraping only where `robots.txt` and the terms of service allow it, facts only). `lures.catalog_lure_id` is nullable, so users can still add lures by hand
- Conditions are entered manually for the MVP; auto-filling weather from Open-Meteo is a stretch goal
- Hosting: Render (API), Neon (Postgres + pgvector), Vercel (frontend). Deployed early (backend in Milestone 1, frontend in Milestone 3) with auto-deploy on merge to `main`; the cold start is handled with a frontend wake-up screen and a keep-warm ping
- Demo: a shared demo account with a stocked inventory and history, reset nightly, plus a pre-computed real recommendation on the landing page (Milestone 9). Demo visitors can't edit free text, and demo recommendations are limited per IP and per day
- Safeguards: provider spend limits, a per-user daily quota (a count of `recommendations` rows), per-IP rate limiting with `slowapi`, defined LLM failure handling, cost and latency metrics on each recommendation, and prompt injection mitigations (delimited user data, length limits)
- Backend layers: routers → services → repositories, Pydantic schemas separate from SQLAlchemy models, all schema changes through Alembic
- Tooling: `uv`, `ruff`, `mypy`; docker-compose runs only the local Postgres + pgvector; GitHub Actions CI on every PR; branch protection on `main`; a Claude Code hook and a pre-commit hook run `ruff`

## Working with Erik
Erik must understand every line of this codebase and be able to explain it in interviews. Learning to direct and correct Claude is also an explicit goal.
- Explain the reasoning and tradeoffs behind every change, not just what changed.
- Keep changes small and reviewable. Don't scaffold whole subsystems in one go.
- Erik hand-writes the core pieces: auth, the pgvector query, prompt assembly and the eval scoring logic. Help at the lightest level that works (explain the concept, point to docs, outline in pseudocode, give a targeted hint, review), but don't write the implementation unless Erik asks. See Growth Goal 1 in the plan for the full approach and the fallback.
- Suggest decisions with a recommendation; don't make them silently.

## Git workflow
Follow a professional team workflow, even when working solo.
- **Never commit directly to `main`.** Every change, including docs, goes through a pull request.
- **One branch per change**, created from an up-to-date `main` (`git switch main && git pull`). Name it with a type prefix: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/` (for example `feat/lure-crud`).
- **Small, focused commits** using Conventional Commits: `type: short imperative summary` (for example `feat: add lure CRUD endpoints`). The body explains *why* when that isn't obvious.
- **Open the PR with `gh pr create`.** The description covers what changed, why, how it was tested, and screenshots for UI changes. Reference the issue if there is one (`Closes #12`).
- **Erik reviews and merges every PR.** Claude opens PRs but never merges them, and never pushes to `main` or force-pushes.
- **Squash merge**, then delete the branch.
- Run the tests and linters locally before opening a PR. CI runs on the PR and must pass before merging (enforced by branch protection once it's set up in Milestone 1).

## Conventions
- Keep `docs/PROJECT_PLAN.md` in sync when decisions are made or scope changes.
- Record significant decisions as ADRs in `docs/decisions/`: ones that are hard to reverse, affect several parts of the system, or that an interviewer would ask about. Start from `0000-template.md` and keep each to one page (about 400 words).
- Career and resume context is in `docs/CAREER_CONTEXT.md`. It isn't needed for coding tasks.
- `docs/INTERVIEW_PREP.md` is Erik's private question bank. It may not exist in a fresh clone. Whenever a decision, tradeoff or pattern comes up that an interviewer is likely to ask about (during design discussions too, not only when a feature is finished), add it in the same turn: a `###` question with **Key points:** and an empty **My answer:** (Erik writes the answers in his own words). Update or flag questions that later decisions make outdated, and say in the reply which questions were added. The file is gitignored, so these edits don't go through a PR.
