# Project Plan: Bass Lure Inventory & AI Recommendation App

## Purpose
A portfolio project that shows full-stack and AI-integration skills. Users log the lures they own, enter fishing conditions, and get AI recommendations chosen only from their own inventory. It's open to other users, so it needs real accounts and auth.

The job-search reasoning and resume framing are in `docs/CAREER_CONTEXT.md`.

## Personal Growth Goals
Shipping the app is only half the point. The project is also a deliberate way for Erik to get better as a software engineer. Each goal below comes with concrete practices so progress can be checked.

### 1. Understand and explain every part of the codebase
Nothing gets merged that Erik can't explain line by line. By the end, Erik should be able to walk an interviewer through any file, any design decision and any tradeoff.
- **Hand-write the core pieces:** password hashing and JWT auth, the pgvector similarity query, the prompt assembly for the LLM, and the eval harness's scoring logic (the scoring functions and the variant comparison; Claude can help with the runner and boilerplate). These are the parts interviewers will ask about most.
  - **"Hand-written" means Erik types the code and makes the decisions, not that it's written from memory or without help.** Docs, tutorials and questions to Claude are all expected.
  - **How Claude helps, from lightest to heaviest:** explain the concept → point to the right docs section → outline the steps in plain English or pseudocode → give a targeted hint on a specific line or error → review the finished code. Claude doesn't write the implementation.
  - **Break the work into single-function steps.** Each step is small enough to finish in one sitting, gets reviewed before moving on, and has tests where it makes sense.
  - **Fallback if it isn't working:** Claude writes the piece, Erik studies it until every line can be explained, then writes a related feature solo (for auth, a "change password" endpoint). Stuck for an hour on one line? Ask for a bigger hint rather than grinding.
  - **The test for any code, whoever typed it:** could Erik rebuild it from a blank file, using the docs, in a reasonable amount of time?
- **Explain-back rule:** after each feature, Erik explains it out loud or in writing (what it does, why it's built that way, and what the alternatives were) before moving on. If the explanation has gaps, go back to the code.
- **Walkthrough notes:** keep short notes in `docs/walkthroughs/` for each major flow (signup to login to an authenticated request; adding a lure; a recommendation request from start to finish).
- **Interview question bank:** keep a running list of questions an interviewer might ask ("Why pgvector instead of Pinecone?", "How do you keep JWTs from being forged?", "What happens if the LLM recommends a lure the user doesn't own?"), and practice answering them. It stays private: `docs/INTERVIEW_PREP.md` is gitignored and backed up in Erik's notes app.

### 2. Architecture and design
Build the backend the way a professional team would, and be able to explain why it's organized that way.
- **Layered backend:** `routers/` (HTTP only) → `services/` (business logic) → `repositories/` (database access), with Pydantic `schemas/` kept separate from SQLAlchemy `models/`. Dependencies are passed in with FastAPI `Depends`.
- **Migrations:** every schema change goes through Alembic. Never edit the database by hand.
- **API design:** RESTful resources under `/api/v1`, a consistent error response shape, correct status codes, and pagination on list endpoints.
- **Decision records:** write a short ADR (Architecture Decision Record: context, decision, alternatives, consequences) in `docs/decisions/` for each significant choice. The decisions below are the first batch to write up.
  - **When to write one:** the decision is hard to reverse, affects several parts of the system, or an interviewer is likely to ask "why?" Smaller decisions just go in this plan.
  - **Keep it short:** start from `docs/decisions/0000-template.md` and stay within one page (about 400 words), so a reviewer can read it in two minutes.
- **Design before code:** for each feature, sketch the endpoints, data shapes and edge cases before writing any code.
- **Testable by design:** services should be unit-testable with pytest without a running server. This is the proof that the layering works.

### 3. Use Claude Code effectively, and course-correct it
Learn to use AI coding tools the way a strong engineer would: as an assistant Erik directs and checks, not an autopilot.
- **Maintain `CLAUDE.md`:** keep it short and current. When Claude makes the same mistake twice, add a rule to prevent it.
- **Write at least one custom skill:** for a workflow that repeats. Candidates: adding and validating a knowledge base entry, generating an ADR from a decision, or a "walk me through this change" explainer.
- **Plan before big changes:** use plan mode for anything that touches more than one or two files, and read the plan critically before approving it.
- **Review every diff:** read each change before accepting it. If Claude's reasoning isn't clear, ask why before accepting.
- **Know how to recover:** commit before each Claude session so there's a clean point to go back to. Interrupt with Esc when it's heading the wrong way, use `/rewind` to undo, and correct it explicitly ("don't do X, do Y because Z") instead of re-rolling the same prompt.
- **Use hooks for rules that must always happen:** CLAUDE.md is guidance Claude usually follows; a hook is a command Claude Code always runs. Start with the `ruff format` hook in Milestone 1, and add others when a rule keeps getting missed.
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
- RAG has to earn its place: an eval harness compares it against Claude with no knowledge base and with the whole knowledge base in the prompt (see Evaluation and ADR 0001).

**AI providers:** Claude (Anthropic API) generates the recommendations. Voyage AI creates the embeddings; Anthropic recommends it, since Anthropic has no embeddings API of its own. That means two API keys, both kept in environment variables and never committed.

**Auth:** Written by hand with JWT in FastAPI: password hashing (Argon2 via `pwdlib`, the library the current FastAPI docs use), short-lived access tokens, and a `get_current_user` dependency. Chosen over FastAPI-Users or a hosted service because Erik should understand and be able to explain every line, and a mobile client could reuse it.
- **Revocation through a token version:** `users.token_version` (an integer) is included in every JWT, and `get_current_user` rejects tokens whose version doesn't match. Incrementing it invalidates every token the user holds. `get_current_user` already loads the user from the database, so the check costs nothing extra. Regular logout just discards the token on the client.
- **Change password** (while logged in) increments `token_version`, which logs out the user's other sessions. **Log out everywhere** increments it directly.
- **Login rate limiting:** `slowapi` limits per IP and per email (for example 5 attempts per minute), from Milestone 1. No account lockout, because lockout lets an attacker lock real users out by failing on purpose.
- **Error messages:** login says "invalid email or password" without revealing which was wrong. Signup does reveal "email already registered"; that's an accepted tradeoff for usability.
- **Out of scope for launch:** refresh tokens, password reset and email verification (reset and verification need an email provider). All three are stretch goals, and the README lists them as deliberate gaps.
- **How to describe it:** "Implemented JWT authentication from scratch with PyJWT and pwdlib (Argon2): no auth framework, and no hand-written cryptography." Avoid "hand-written auth," which can sound like rolling your own crypto.

**Condition input:** Manual form entry for the MVP. Auto-filling from Open-Meteo (free, no API key) using the user's location is a stretch goal. It shouldn't hold up the core RAG pipeline.

**Conditions considered:** Water clarity, season, water temperature, air temperature, wind, barometric pressure (trend), and sky (sunny, partly cloudy or overcast).

**Lure attribute detail level:** Simple categories (type: jig/spinnerbait/crankbait and so on, brand, color, size, technique), not detailed action or depth-range specs. This keeps the schema manageable. Knowledge base entries should be written at the same level of detail, because the LLM can only match on attributes the lures actually store.

**Quantity:** The lures table has a `quantity` column (integer, defaults to 1), because people often own several of the same lure.

**Lure catalog:** A shared master catalog of popular lures that users can pick from when adding to their inventory. They can still add their own lures by hand. Picking from the catalog is faster than typing everything in, and it keeps lure data consistent (brand names, types and techniques), which improves recommendations.
- **Data source (v2 scraped catalog):** first look for official product data feeds (manufacturer or retailer, often through affiliate programs). Scrape only sites whose `robots.txt` and terms of service allow it. Rate-limit requests and identify the scraper honestly. Store facts only (brand, model, type, sizes, color names), never copied descriptions or product images.
- **Timing:** the schema supports the catalog from Milestone 2 (a nullable `catalog_lure_id` on `lures`), so no migration of existing data is needed later. Before launch, Milestone 10 builds a small **hand-seeded catalog** (30 to 50 popular lures, no scraping) plus catalog search, so a recruiter trying the demo can pick lures instead of typing them in. The full **scraped catalog is a v2 after launch** (see Stretch Goals). It was postponed because it would add 20 to 35 hours before launch for little gain in interviews, while shipping sooner does more for the job search. Shipping it after launch also shows continued work on a live product.

**Recommendation history:** Saved. Each recommendation stores the conditions, the output and an optional "did it work?" rating from the user. This adds about a day of work. It gives users a history of what worked. With few users the ratings will be sparse, so describe them honestly: feedback collected for future re-ranking, not a working feedback loop. Recommendation quality is measured by the eval harness instead (see Evaluation).
- **Which lure was used:** when rating, the user can optionally say which of the picks they actually used. A rating applies to the whole recommendation, so without this, per-lure success rates would credit every pick equally.

**Catch log:** users record their catches, in Milestone 8. Catches are much stronger data than the "did it work?" rating, and they're the main input for analytics.
- **Fields:** date, species (largemouth, smallmouth, spotted), fish count, the biggest fish's weight and length (optional), the lure (a nullable link plus the lure's name snapshotted, so the log still reads correctly after a lure is deleted), conditions (the same typed columns as recommendations, optional), water body name (optional free text) and notes.
- **No GPS or exact locations:** anglers guard their spots, and storing them would create a privacy problem the app doesn't need.
- **Linked to recommendations (optional):** a "Log a catch" button on a recommendation pre-fills its conditions and lures and stores the `recommendation_id`. Catches can also be logged on their own.
- **Not sent to the LLM:** catch history doesn't feed into recommendations yet, so the prompt and the eval stay unchanged. Personalizing recommendations from catches is a stretch goal.

**Analytics:** user-facing charts for anglers about their own tackle box and history, in Milestone 9. There's no visitor tracking (product analytics).
- **Inventory breakdown** by type, technique and color. It needs no history, so it's useful from day one.
- **Recommendation timeline** by month or season, plus **most and never recommended lures** ("dead weight in your tackle box").
- **Catches over time, by lure and by condition**, from the catch log.
- **Success rates** by lure and by condition, from catches and from ratings (using "which lure was used"). They're shown only with at least 5 data points, otherwise "not enough data yet." Refusing to chart a handful of data points is deliberate.
- **A public system stats page:** total recommendations, average cost, median latency and the eval results, built from the Observability metrics. No personal data.
- **Charts:** Recharts.
- **Empty states:** new users see a clear message instead of blank charts. The demo's seed data includes enough rated history and catches for the charts to show real data.

**Knowledge base authoring:** Erik writes or transcribes every entry, and Claude refines it for clarity, gaps and consistent format. The domain knowledge stays Erik's to explain.
- **One entry = one self-contained tip.** Entries are written by hand, so no automatic chunking is needed. Revisit this only if long documents are ever imported directly.
- **Grown in stages:** stage 1 is 50 to 150 entries from Erik's own knowledge. After the first eval run, expand toward a larger knowledge base (more personal recommendations plus external charts and flow charts), then re-run the eval to measure whether the expansion helped.
- **Charts and flow charts are transcribed into text entries**, tagged with the conditions they apply to (for example season, clarity, water temperature range). The tags also power eval variant D. Images are not embedded directly.
- **External sources follow the catalog's facts-only rule:** restate facts in Erik's own words, never copy text or images, and record each entry's source type (personal or external), source name and URL.
- **Conflicting advice:** keep both entries, tagged with their source. The prompt tells Claude to prefer Erik's personal entries when they conflict. Only exact duplicates are merged.

**Real users:** after launch, recruit 5 to 10 anglers (fishing friends) to use the app for a season. Real usage is the only way the "did it work?" ratings become real data, and usage numbers in the README ("used by N anglers over X weeks, Y rated recommendations") beat any feature. Real users mean real responsibilities, so these exist before anyone signs up:
- **A short privacy note:** what's stored (email, password hash, lures, recommendations, catches), why, and that it's never sold or shared.
- **Account deletion:** `DELETE /api/v1/auth/me` deletes the user and all their lures, recommendations and catches. It's blocked for the shared demo account.
- **A feedback channel:** for example a simple form, or a link to open a GitHub issue.

**Presenting the AI-assisted development:** every commit already carries a `Co-Authored-By: Claude` line, so the README tells the same story the history shows. The framing is "directed and verified," backed by evidence:
- **A short "How this was built" README section:** CLAUDE.md, hooks, small reviewed PRs, the explain-back rule, and a link to `docs/CLAUDE_LESSONS.md`.
- **An explicit list of what Erik hand-wrote:** auth, the pgvector query, prompt assembly and the eval scoring logic. This list gives the rest of the story its credibility.
- **Keep it short:** the app and the eval results lead, and the process supports them. A longer blog or LinkedIn write-up is optional in Milestone 12.

**Showing the reasoning:** a reviewer who doesn't fish can't judge whether a recommendation is good, but they can judge visible, traceable reasoning.
- **Per-lure citations:** each pick in Claude's structured output includes `cited_entry_ids`. The service drops any citation that wasn't in the entries retrieved for this request. It's the same guardrail as checking lure ownership, and it catches Claude citing something it never saw.
- **On each recommended lure:** the reasoning plus "Based on" chips with the cited entries' titles.
- **Source labels:** "From Erik's notes" for personal entries, or the source name with a link for external ones.
- **"What the AI looked at":** a collapsible panel, hidden by default, listing the titles of all retrieved entries with their similarity scores, including the ones Claude didn't cite.
- **Titles only, never entry content:** the knowledge base stays private. This is enforced in the API response schema (titles, sources and scores only), not just hidden in the UI; otherwise anyone could read the content in the browser's dev tools.
- **Titles must stand on their own,** since they're all a reviewer sees. For example "Stained water, early spring: slow-rolled spinnerbait," not "Spring tip #3."
- **History stays correct:** each entry has a stable `slug` so re-seeding never changes IDs, and the cited entries' titles and sources are snapshotted into the stored result.

**Development tooling and CI:**
- **Python tooling:** `uv` for dependencies (a lockfile means CI and local installs match exactly), `ruff` for linting and formatting, and `mypy` for type checking (non-strict to start, tightened later).
- **CI:** a GitHub Actions workflow runs on every pull request: `ruff` lint and format check, `mypy` and `pytest`. A Postgres + pgvector service container lets repository and integration tests run alongside the service unit tests. Frontend lint, type check and build get added in Milestone 3.
- **Branch protection on `main`:** require a pull request and passing CI before merging, with no bypass for admins. That makes "tests must pass" and "never push to `main`" rules GitHub enforces, not just promises.
- **Local database:** docker-compose runs only Postgres + pgvector (the `pgvector/pgvector` image, matching Neon's Postgres major version). The API runs directly with `uv` for fast reloads and easy debugging, so no Dockerfile is needed; Render deploys Python natively.
- **Formatting hooks:** a Claude Code hook in `.claude/settings.json` runs `ruff format` whenever Claude edits a Python file, and a pre-commit git hook runs `ruff` on every commit, so Erik's commits are covered too. CI is the final check.

**Hosting:**
- Backend: Render (free tier sleeps when idle, so the first request is slow. That's acceptable for a portfolio app; note it in the README.)
- Database: Neon Postgres (free tier, supports pgvector)
- Frontend: Vercel

**Deployment:** deploy early as a walking skeleton, not at the end. The backend goes live at the end of Milestone 1 and the frontend in Milestone 3. After that, Render and Vercel redeploy automatically whenever a PR merges to `main`. This surfaces production problems (CORS, environment variables, migrations on Neon, enabling pgvector) one at a time while they're small, and there's always a live link to share.

**Cold start:** Render's free tier sleeps after about 15 minutes idle and can take up to a minute to wake.
- **Wake-up screen:** the static Vercel frontend loads instantly, pings the API on page load, and shows a friendly "waking up the server" message until it answers.
- **Keep-warm ping:** a scheduled job calls `/health` every 10 to 14 minutes. Check Render's terms of service before relying on it.
- Neon also suspends when idle, but it wakes in well under a second, so it needs no special handling.

**Demo experience:** a recruiter should see the app working within seconds, without signing up.
- **Shared demo account, reset nightly:** a "Try the demo" button logs into one demo user with a realistic inventory and past recommendations (with ratings, so the history view isn't empty). A scheduled job restores the demo data every night. Visitors may briefly see each other's changes; that's accepted for simplicity.
- **Demo recommendation limits:** every visitor shares the demo account, so a per-user quota would let one visitor use it up. Instead: 3 recommendations per visitor IP per day, plus 50 per day in total (a count of the demo user's `recommendations` rows). When either limit is hit, show the landing page sample and "Demo limit reached, sign up to keep going," so the limit never produces a broken page.
- **Demo free text is locked:** demo visitors can add lures (by picking from the catalog, so the name comes from the catalog), delete them and change structured fields like quantity, but can't edit `name` or `notes`. The same applies to catches: demo visitors can log them, but without notes or a water body name. This stops one visitor from planting prompt injection text that every other visitor would see until the nightly reset.
- **Landing page sample:** one real recommendation, pre-computed, saved as JSON and labeled as real output. It's free, appears instantly, and still works while the backend is asleep.

**Cost and abuse safeguards:** signup is free and every recommendation calls paid APIs, so several cheap layers each catch what the others miss.
- **Provider spend limits:** set in each provider's console when its key is created. The backstop: if everything else fails, the feature stops instead of running up a bill.
- **Per-user daily quota:** 20 recommendations per day to start. It's a count of the user's `recommendations` rows created today, so no extra table is needed, and failed calls never count because they don't save a row.
- **Per-IP rate limiting** with `slowapi` on signup and login (from Milestone 1, when auth goes live) and on recommendations (Milestone 5). Its counters live in memory and reset when Render restarts, which is acceptable at this scale.
- **No CAPTCHA:** it adds friction for recruiters, and the layers above already cover bot signups.
- All the numbers are starting defaults. Tune them once Milestone 5 logs real costs per call.

**LLM failure handling:**
- **Slow or no response:** an explicit timeout. The Anthropic SDK already retries transient errors (rate limits, 5xx, dropped connections) with backoff, so there's no hand-rolled retry loop.
- **Malformed output:** the output schema is enforced with tool use or structured outputs and validated with Pydantic. Retry once, then return an error.
- **IDs the user doesn't own:** drop them and log them. If no valid picks remain, retry once, then show a clear "no recommendation" message.
- **Provider down or spend limit reached:** a 503 in the standard error shape and a friendly "temporarily unavailable" message. The demo falls back to the landing page sample.
- **Empty inventory:** return a clear message without calling Voyage or Claude.

**Observability:** each saved recommendation records the model, input and output tokens, the computed cost, latency for each stage (embedding, retrieval, generation) and how many invalid IDs were dropped. Failures don't save a row, so they're written to structured JSON logs (visible in Render). The stored numbers feed the README ("each recommendation costs about $X and takes Y seconds") and the public system stats page (see Analytics).

**Prompt injection:** lure `name` and `notes` are user text that goes into the prompt. Mitigations:
- User data is wrapped in clear delimiters (for example XML tags), and the prompt tells Claude to treat it as data, not instructions.
- `name` and `notes` have length limits, enforced by Pydantic validation.
- Structured output and ID validation limit what an attack can achieve. The reasoning text is the remaining exposure; React escapes displayed text, so it isn't an XSS risk.
- On a normal account an injection only affects that user's own results. The remaining risk is documented in the README.

## Database Schema (finalize column types in Milestone 1)
- `users`: id, email (unique), hashed_password, token_version (integer, default 0; incremented to invalidate all of the user's tokens), created_at
- `lures`: id, user_id (FK → users), catalog_lure_id (nullable FK → catalog_lures; null for lures the user added by hand), name, type, brand, color, size, technique, quantity (default 1), notes, created_at, updated_at
- `catalog_lures`: id, brand, model, type, technique, sizes (text[]), colors (text[]), source_name (`seed` for hand-seeded entries), source_url (nullable), last_scraped_at (nullable; set by the v2 scraper), created_at. Shared by all users; unique on (brand, model). `type` and `technique` use the same fixed lists as `lures`.
- `knowledge_base_entries`: id, slug (unique, stable; the seed script upserts by it), title, content (text), category (e.g. clarity, season, structure, weather), condition tags (for example season, clarity, water temperature range; exact columns decided in Milestone 4), source_type (`personal` or `external`), source_name, source_url (nullable), embedding (vector, whose dimension must match the Voyage model's output), created_at. Shared by all users; not per-user.
- `recommendations`: id, user_id (FK → users), condition columns (water_clarity, season, water_temp_f, air_temp_f, wind, pressure_trend, sky; values match the condition form and the knowledge base tags; exact types finalized in Milestone 5), retrieved_entry_ids (int[]), result (JSONB: the recommended lures with their reasoning and cited entries (titles and sources), saved as a snapshot so the history still reads correctly if a lure is later deleted or an entry changes), worked (nullable boolean: the "did it work?" rating), model, input_tokens, output_tokens, cost_usd, embedding_ms, retrieval_ms, generation_ms, invalid_ids_dropped, created_at
- `recommendation_picks`: id, recommendation_id (FK → recommendations), lure_id (nullable FK → lures, set to null if the lure is deleted), rank, used (boolean, default false; at most one per recommendation: the "which lure did you use?" answer). Makes per-lure analytics simple joins.
- `catches`: id, user_id (FK → users), caught_on (date), species, fish_count, biggest_weight (nullable), biggest_length (nullable), lure_id (nullable FK → lures, set to null if the lure is deleted), lure_name (snapshot), recommendation_id (nullable FK → recommendations), the same condition columns as `recommendations` (all nullable), water_body (nullable), notes (nullable), created_at. No GPS or exact location.

Why columns for conditions but JSONB for the result: **query what you filter, snapshot what you display.** Analytics groups and filters by condition (success rate in stained water), and the condition set is now fixed (it matches the form and the knowledge base tags), so typed columns give database-level constraints and simpler SQL. The result is only ever displayed as a whole and must survive lure deletions and entry edits, so it stays a JSONB snapshot. Per-lure queries use `recommendation_picks` rather than unpacking the JSON.

## Recommendation Pipeline
1. The user submits the conditions form, and the request goes to `POST /api/v1/recommendations`.
2. The service checks the per-IP rate limit and the user's daily quota (or the demo limits), and returns early with a clear message if the inventory is empty. All of this happens before any paid API call.
3. The service builds a text query from the conditions (for example "stained water, early spring, 52°F water, windy, falling pressure, overcast").
4. The query is embedded with Voyage AI.
5. pgvector returns the top-k most similar knowledge base entries by cosine distance (start with k=5 and tune it).
6. The prompt sent to Claude contains the conditions, the retrieved entries and the user's lure inventory (wrapped in delimiters and marked as data), with instructions to recommend **only** lures from that inventory, to explain why each one fits, and to prefer Erik's personal entries when retrieved entries conflict.
7. Claude returns structured output (lure IDs, reasoning and cited entry IDs for each pick), validated with Pydantic. The service checks that every returned lure ID belongs to the user's inventory and drops any that don't, so the model can't recommend a lure the user doesn't own. It also drops any citation that wasn't among the retrieved entries. Failures are handled as described in LLM failure handling.
8. The service saves a `recommendations` row (conditions, result snapshot, and cost, token and latency metrics) plus one `recommendation_picks` row per pick, and returns the result.
9. Later, the user can rate it with `PATCH /api/v1/recommendations/{id}` (`worked: true/false`, plus optionally which pick was used).

## Evaluation
An eval harness measures whether the knowledge base and retrieval actually improve recommendations. Without it there's no answer to "why retrieve at all?" or "does the knowledge base beat Claude's own knowledge?" (ADR 0001).

**Scenarios:** 30 to 50 test cases. Each has a set of conditions plus "good picks" and "bad picks" by lure type, written by Erik as the domain expert. Every scenario runs against the same fixed test inventory (about 25 lures), so scores are comparable across runs. Include edge cases: a tiny inventory, and conditions with no good match.

**Held-out set:** about a third of the scenarios stay unseen while the knowledge base is written and are used only for the final measurement. This keeps the knowledge base from being tailored to the test.

**Variants compared:**
- **A. No knowledge base:** Claude's own knowledge only. The baseline every other variant must beat.
- **B. Whole knowledge base in the prompt:** tests whether retrieval beats simply giving Claude everything. It stops being viable as the knowledge base grows, and the eval shows where that crossover happens.
- **C. Vector top-k:** the planned pipeline.
- **D. Metadata filter, then vector:** filter entries by condition tags (season, clarity and so on), then rank by similarity.

**Scoring:**
- **Picks (scored by code):** the share of recommended lures whose type is in the scenario's good list, the share in its bad list, and any invalid IDs. This works because Claude returns structured output (lure IDs) and every lure has a `type`.
- **Retrieval (scored by code):** recall@5, meaning how many of the entries Erik marked relevant for a scenario appear in the top 5. This separates retrieval misses from generation misses. It doesn't apply to variants A and B.
- **Citation accuracy (scored by code):** the share of cited entries that Erik marked relevant for the scenario. It reuses the recall@5 labels, so it needs no extra labeling. It applies to variants B, C and D.
- **Reasoning (reviewed by Erik):** a hand review of a sample of explanations each run.
- LLM output varies, so each scenario runs about 3 times per variant and scores are averaged.

**Presentation:** publish a results table and a short write-up in the README. Any outcome is useful. If variant A matches C, that shows the knowledge base should focus on what Claude doesn't know (Erik's own patterns and local knowledge) rather than general bass-fishing advice.

## API Sketch
- Auth: `POST /api/v1/auth/signup`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/change-password`, `POST /api/v1/auth/logout-all`, `DELETE /api/v1/auth/me` (account deletion)
- Lures: `GET/POST /api/v1/lures`, `GET/PATCH/DELETE /api/v1/lures/{id}`, all limited to the current user
- Recommendations: `POST /api/v1/recommendations`, `GET /api/v1/recommendations` (history), `PATCH /api/v1/recommendations/{id}` (rating, optionally with the pick used)
- Catches: `GET/POST /api/v1/catches`, `GET/PATCH/DELETE /api/v1/catches/{id}`, all limited to the current user
- Analytics: `GET /api/v1/analytics/...` (aggregations for the current user's charts; exact endpoints designed in Milestone 9), `GET /api/v1/stats` (public system stats, no personal data)
- Catalog: `GET /api/v1/catalog?search=...` (search the shared catalog when adding a lure); filled by the seed script (v2: the scraper or feed importer), not by users
- Knowledge base: loaded by a seed/admin script, not a public endpoint

## Milestones
Work in order, with no fixed dates. Erik works on the app as much as possible, so progress is measured by milestones finished, not weeks spent. Each milestone has a **Done when** checklist; don't start the next one until everything on it is true.

Every milestone also includes:
- An ADR for each significant decision made along the way
- A walkthrough note in `docs/walkthroughs/` for any new flow
- New entries in the interview question bank
- Passing the explain-back rule: Erik can explain everything built in that milestone without looking at the code
- From Milestone 1 on, the merged work is live: check the deployed app, not just the local one

### Milestone 1: Backend foundation and auth
Set up the repo structure, the layered backend skeleton, Alembic, and the development tooling: `uv`, `ruff`, `mypy`, docker-compose for local Postgres with pgvector, the CI workflow, branch protection, and the Claude Code and pre-commit formatting hooks. Hand-write signup, login and the JWT dependency. Deploy the backend to Render and Neon as a walking skeleton.
- **Decide:** where the frontend stores tokens (in memory with an `Authorization` header, or an httpOnly cookie). Look up the XSS/CSRF tradeoff and write an ADR.
- **Write ADRs:** stack, RAG vs. a trained model, hand-written auth.
- **Auth, hand-written in single-function steps** (Erik writes each one; Claude explains, points to docs and reviews):
  1. Hash a password and verify one (`pwdlib`), with tests
  2. Create a JWT with an expiry and the user's token version
  3. Decode and validate a JWT, rejecting ones that are expired or have a bad signature
  4. The `get_current_user` dependency, rejecting tokens whose version doesn't match the user's
  5. The signup endpoint
  6. The login endpoint
  7. The change password endpoint (increments `token_version`)
  8. The log out everywhere endpoint
- **Rate limiting:** set up `slowapi` with limits on signup and on login (per IP and per email).
- **Check-in (Claude: ask Erik after auth steps 1 and 2):** is the step-by-step approach working? If yes, continue through step 8. If it feels like no progress is being made, switch to the fallback in Growth Goal 1: Claude writes steps 3 to 6, Erik learns them until they can be explained line by line, then writes steps 7 and 8 (change password and log out everywhere) alone.
- **Deploy:** a `/health` endpoint; the backend on Render and the database on Neon (with pgvector enabled); migrations run as part of each deploy; auto-deploy on merge to `main`; secrets only in Render's environment variables. Check Render's terms of service, then set up the keep-warm ping.
- **Done when:** a user can sign up, log in and call a protected endpoint, **on the live API**; changing the password or logging out everywhere makes old tokens fail (with a test); login and signup are rate limited (with a test); migrations run cleanly from an empty database, locally and on Neon; merging to `main` deploys automatically; the auth logic has pytest tests; `docker compose up` gives a fresh clone a working local database; CI runs on every PR, and `main` can't be merged into while CI fails.

### Milestone 2: Lure inventory API
CRUD endpoints for lures, limited to the current user.
- **Decide:** should `type` and `technique` be fixed lists (enums or lookup tables) or free text? Recommendation: fixed lists. Consistent values make it much easier for the LLM to match lures to knowledge base entries, while free text like "crank" vs. "crankbait" gets messy.
- **Decide (ADR):** when a lure is linked to the catalog, should its attributes be copied onto the user's row (simple, and users can edit them) or read through the link (no duplication, but harder to customize)? Include the nullable `catalog_lure_id` column either way.
- **Done when:** all lure endpoints work with validation (including length limits on `name` and `notes`), pagination and consistent errors; one user can never read or change another user's lures (with a test that proves it); service-layer tests pass.

### Milestone 3: Frontend inventory
Scaffold the React app. Build the signup and login pages and the inventory screens, working end to end. Deploy the frontend to Vercel, with auto-deploy on merge, and add the wake-up screen for the cold start. Add frontend lint, type check and build to CI.
- **Decide:** frontend tooling (Vite) and whether to use TypeScript. TypeScript is worth considering because it's widely expected in industry.
- **Done when:** a new user can sign up, log in, and add, edit and delete lures **on the live site** against the live API; the wake-up screen shows while the backend is waking.

### Milestone 4: Knowledge base and embeddings
**First, write the eval scenarios** (see Evaluation), before any knowledge base entries, like writing tests before code, and set the held-out third aside. Then Erik writes stage 1 of the knowledge base (50 to 150 entries from Erik's own knowledge, with condition tags and source fields) and Claude refines it. Build the embedding and seed pipeline with Voyage AI and pgvector.
- **Decide:** which Voyage embedding model to use. This sets the dimension of the `vector` column.
- **Set up:** a spend limit on the Voyage account when creating its API key.
- **Decide:** the exact condition tag columns on `knowledge_base_entries`. They should match the condition form's values so variant D can filter on them.
- **Claude skill:** write the first custom skill here. A strong candidate: validating and adding knowledge base entries.
- **Done when:** the eval scenarios and the fixed test inventory are written, with the held-out set stored separately; all stage 1 entries are embedded and stored with tags and source fields; a manual similarity query for a sample set of conditions returns entries that make sense; the seed script can be re-run safely and upserts by `slug`, so entry IDs never change.

### Milestone 5: Recommendation pipeline
Build retrieval and the Claude generation step, including checking the output against the inventory and validating citations against the retrieved entries. Build the recommendation endpoints and save history, including `recommendation_picks` rows (ADR: typed condition columns plus a JSONB result snapshot).
Add the safeguards from Decisions: the per-user quota, per-IP rate limiting on recommendations, LLM failure handling, the cost and latency metrics, and the prompt injection mitigations.
- **Decide:** which Claude model to use, weighing cost against quality on this task. Compare a few real outputs before committing.
- **Set up:** a spend limit in the Anthropic Console when creating the Claude API key.
- **Done when:** `POST /recommendations` returns reasoned picks drawn only from the user's inventory; results are saved with their metrics, condition columns and `recommendation_picks` rows; a rating can record which pick was used; responses include entry titles, sources and scores but never entry content (with a test); ratings work; the quota and rate limits reject excess requests (with tests); timeouts, malformed output, invalid IDs and provider errors are handled (with tests that mock the API); failures appear in the logs; it's been tested against realistic combinations of conditions, including an empty or tiny inventory.

### Milestone 6: Evaluation
Build the eval harness and run all four variants (see Evaluation). Erik hand-writes the scoring functions and the variant comparison; Claude can help with the runner and boilerplate.
- **Decide:** where the harness lives in the repo and the format of the scenario files.
- **Done when:** all four variants run on every scenario (about 3 runs each); picks, retrieval and citation accuracy are scored by code; Erik has reviewed a sample of the reasoning; the final numbers come from the held-out set; a results table and short write-up are drafted for the README.
- **Check-in (Claude: ask Erik when this milestone is finished):** based on the results, should stage 2 of the knowledge base (the larger expansion) happen before launch or after? Re-run the eval after the expansion either way.

### Milestone 7: Frontend recommendations
The conditions form, the results display (with citation chips, source labels and the "What the AI looked at" panel), the history view and the "did it work?" rating, with an optional "Which lure did you use?"
- **Done when:** the whole flow works in the browser, from entering conditions to seeing results to rating them later from history; every recommended lure shows the entries it's based on, and history still shows them correctly after an entry is edited.

### Milestone 8: Catch log
Catch CRUD in the API and the UI (see Catch log in Decisions), plus a "Log a catch" button on recommendations that pre-fills conditions and lures.
- **Decide:** units for weight and length (pounds and ounces, or decimal pounds; inches) and whether the user can switch them.
- **Done when:** a user can log, edit and delete catches, standalone or from a recommendation; one user can never read or change another user's catches (with a test); a catch still reads correctly after its lure is deleted; length limits apply to `water_body` and `notes`.

### Milestone 9: Analytics
User-facing charts built with Recharts (see Analytics in Decisions): the inventory breakdown, the recommendation timeline, most and never recommended lures, catches over time and by lure and condition, success rates with a minimum sample size, and the public system stats page.
- **Done when:** each chart is backed by a tested aggregation endpoint; success rates show "not enough data yet" below 5 data points; a brand-new user sees a useful inventory breakdown and clear empty states instead of blank charts; the system stats page shows no personal data.

### Milestone 10: Seeded lure catalog
Erik curates a data file (JSON or CSV) of 30 to 50 popular bass lures, storing facts only: brand, model, type, technique, sizes and color names. A seed script loads it into `catalog_lures`, and the add-lure screen gets catalog search. Roughly 3 to 5 hours, with no scraping.
- **Done when:** the seed script can be re-run safely without creating duplicates; users can search the catalog and add a lure from it, or still add one by hand; catalog entries use the same fixed `type` and `technique` lists as `lures`.

### Milestone 11: Demo and polish
The app has been live since Milestone 1, so this milestone is about the first impression. Build the shared demo account (seed data: a realistic inventory plus enough past recommendations with ratings, including which lure was used, and enough catches for the analytics charts to show real data), its nightly reset, its recommendation limits and its locked free-text fields, the landing page with a pre-computed real recommendation, and a "Try the demo" button. Add what real users need before they sign up: the privacy note, account deletion and a feedback channel. Polish the UI and write the README (including an architecture diagram, the eval results table from Milestone 6, the "How this was built" section with the hand-written list, and a note about the free tier's slow first request).
- **Decide:** how the nightly reset runs (for example a scheduled GitHub Actions workflow, which could also run the keep-warm ping).
- **Done when:** a first-time visitor sees a real recommendation within 10 seconds of opening the URL, without signing up; the demo data resets every night; the demo limits fall back to the landing page sample; demo visitors can't edit `name` or `notes`; a user can delete their account and all their data (with a test), but the demo account can't be deleted; the privacy note and feedback channel are live; the live URL works for a brand-new user; secrets are only in environment variables; the README explains how to run the app locally and how it works.

### Milestone 12: Showcase
Write a short demo write-up and consider a demo video for LinkedIn (optionally with a longer write-up on the AI-assisted process). Do a full mock-interview walkthrough of the codebase, and write the resume bullets (see `docs/CAREER_CONTEXT.md`). Recruit 5 to 10 real users and collect their feedback.
- **Done when:** Erik can give a 5-minute walkthrough of the app and a 15-minute deep dive into the architecture, and answer every question in the interview question bank; real users have been recruited, and once there's enough usage, the README shows real usage numbers.

## Stretch Goals (after the core app ships)
- **Lure catalog v2:** expand the seeded catalog using official data feeds, or responsible scraping where allowed. Research sources, build the importer, and clean and de-duplicate the data (for example "KVD 1.5" vs. "KVD 1.5 Squarebill"). Before writing any scraper, check each site's `robots.txt` and terms of service, and write an ADR on which sources are used and why. Follow the data source rules in Decisions.
- Auto-fill conditions from Open-Meteo using the user's location
- Use the "did it work?" ratings to improve retrieval or re-rank recommendations
- A mobile client that reuses the same API
- Photo upload for lures
- **Refresh tokens:** a short-lived access token plus a rotating refresh token stored hashed in a `refresh_tokens` table, for per-device logout. Revisit the token storage ADR when doing this, since refresh tokens usually live in an httpOnly cookie.
- **Password reset and email verification:** need an email provider and single-use, expiring reset tokens
- **Personalize recommendations from the catch log:** include the user's past catches in similar conditions in the prompt. This changes the eval too: scenarios would need fixed catch histories, and it would be a new variant to compare.
