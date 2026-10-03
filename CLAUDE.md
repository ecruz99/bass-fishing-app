# Bass Fishing App

Bass lure inventory tracker with AI recommendations: users log the lures they own, enter fishing conditions, and get recommendations drawn from their own inventory. It's a portfolio project, so clean code, a live deployment, and a clear technical story matter.

`docs/PROJECT_PLAN.md` holds the plan, every decision and its reasoning. It's the single source of truth: read the relevant milestone and Decisions sections before starting work, and keep them updated when decisions change. `/milestone-brief <number> <kickoff|wrap-up>` summarizes a milestone at its start and checks it at its end.

## Status
Planning done. No code yet.

## Stack and code conventions
- FastAPI (Python), PostgreSQL + pgvector, React. Claude API for generation, Voyage AI for embeddings. Web first; the backend is a JSON API a future mobile client could reuse.
- Backend layers: routers (HTTP only) → services (business logic) → repositories (database access). Pydantic schemas stay separate from SQLAlchemy models.
- Every schema change goes through an Alembic migration. Never edit the database by hand.
- Tooling: `uv`, `ruff`, `mypy`, `pytest`; docker-compose runs only the local Postgres + pgvector.

## Rules the code must never break
- Recommendations only include lures the user owns, and only cite knowledge base entries that were retrieved for that request. Both are checked in code, not just requested in the prompt.
- Knowledge base entry content is never sent to the client. The API returns titles, sources and scores only.
- Every query for user data (lures, recommendations, catches) is scoped to the current user.
- No paid API call happens before the rate limit, quota and empty-inventory checks.
- User text in prompts is wrapped in delimiters and length-limited.
- No GPS or exact locations are stored.
- The shared demo account can't edit free text and can't be deleted.
- Secrets live only in environment variables and are never committed.

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
- Run the tests and linters locally before opening a PR. CI runs on the PR and must pass before merging (enforced by branch protection once it's set up).

## Conventions
- Keep this file short: rules and pointers only. Decisions and their details live in the plan. Don't put milestone numbers here; refer to features by name.
- Keep `docs/PROJECT_PLAN.md` in sync when decisions are made or scope changes.
- Record significant decisions as ADRs in `docs/decisions/`: ones that are hard to reverse, affect several parts of the system, or that an interviewer would ask about. Start from `0000-template.md` and keep each to one page (about 400 words).
- Career and resume context is in `docs/CAREER_CONTEXT.md`. It isn't needed for coding tasks.
- `docs/INTERVIEW_PREP.md` is Erik's private question bank. It may not exist in a fresh clone. Whenever a decision, tradeoff or pattern comes up that an interviewer is likely to ask about (during design discussions too, not only when a feature is finished), add it in the same turn: a `###` question with **Key points:** and an empty **My answer:** (Erik writes the answers in his own words). Update or flag questions that later decisions make outdated, and say in the reply which questions were added. The file is gitignored, so these edits don't go through a PR.
  - **Keep it focused:** add only questions an interviewer is very likely to ask about this project, and skip minor points. A short list Erik actually knows beats a long one he doesn't.
  - **Capture early, answer late:** Erik writes "My answer" only after building the piece, so answers come from his own code. When a feature is finished, revisit its questions: update the key points to match what was actually built, and add questions about implementation details that only showed up in the code.
