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
- RAG has to earn its place: an eval harness compares it against Claude with no knowledge base and with the whole knowledge base in the prompt (see Evaluation and ADR 0001).

**AI providers:** Claude (Anthropic API) generates the recommendations. Voyage AI creates the embeddings; Anthropic recommends it, since Anthropic has no embeddings API of its own. That means two API keys, both kept in environment variables and never committed.

**Auth:** Written by hand with JWT in FastAPI: password hashing (argon2 or bcrypt via `pwdlib`, the library the current FastAPI docs use), short-lived access tokens, and a `get_current_user` dependency. Chosen over FastAPI-Users or a hosted service because Erik should understand and be able to explain every line, and a mobile client could reuse it.

**Condition input:** Manual form entry for the MVP. Auto-filling from Open-Meteo (free, no API key) using the user's location is a stretch goal. It shouldn't hold up the core RAG pipeline.

**Conditions considered:** Water clarity, season, water temperature, air temperature, wind, barometric pressure (trend), and sky (sunny, partly cloudy or overcast).

**Lure attribute detail level:** Simple categories (type: jig/spinnerbait/crankbait and so on, brand, color, size, technique), not detailed action or depth-range specs. This keeps the schema manageable. Knowledge base entries should be written at the same level of detail, because the LLM can only match on attributes the lures actually store.

**Quantity:** The lures table has a `quantity` column (integer, defaults to 1), because people often own several of the same lure.

**Lure catalog:** A shared master catalog of popular lures that users can pick from when adding to their inventory. They can still add their own lures by hand. Picking from the catalog is faster than typing everything in, and it keeps lure data consistent (brand names, types and techniques), which improves recommendations.
- **Data source (v2 scraped catalog):** first look for official product data feeds (manufacturer or retailer, often through affiliate programs). Scrape only sites whose `robots.txt` and terms of service allow it. Rate-limit requests and identify the scraper honestly. Store facts only (brand, model, type, sizes, color names), never copied descriptions or product images.
- **Timing:** the schema supports the catalog from Milestone 2 (a nullable `catalog_lure_id` on `lures`), so no migration of existing data is needed later. Before launch, Milestone 8 builds a small **hand-seeded catalog** (30 to 50 popular lures, no scraping) plus catalog search, so a recruiter trying the demo can pick lures instead of typing them in. The full **scraped catalog is a v2 after launch** (see Stretch Goals). It was postponed because it would add 20 to 35 hours before launch for little gain in interviews, while shipping sooner does more for the job search. Shipping it after launch also shows continued work on a live product.

**Recommendation history:** Saved. Each recommendation stores the conditions, the output and an optional "did it work?" rating from the user. This adds about a day of work. It gives users a history of what worked. With few users the ratings will be sparse, so describe them honestly: feedback collected for future re-ranking, not a working feedback loop. Recommendation quality is measured by the eval harness instead (see Evaluation).

**Knowledge base authoring:** Erik writes or transcribes every entry, and Claude refines it for clarity, gaps and consistent format. The domain knowledge stays Erik's to explain.
- **One entry = one self-contained tip.** Entries are written by hand, so no automatic chunking is needed. Revisit this only if long documents are ever imported directly.
- **Grown in stages:** stage 1 is 50 to 150 entries from Erik's own knowledge. After the first eval run, expand toward a larger knowledge base (more personal recommendations plus external charts and flow charts), then re-run the eval to measure whether the expansion helped.
- **Charts and flow charts are transcribed into text entries**, tagged with the conditions they apply to (for example season, clarity, water temperature range). The tags also power eval variant D. Images are not embedded directly.
- **External sources follow the catalog's facts-only rule:** restate facts in Erik's own words, never copy text or images, and record each entry's source type (personal or external), source name and URL.
- **Conflicting advice:** keep both entries, tagged with their source. The prompt tells Claude to prefer Erik's personal entries when they conflict. Only exact duplicates are merged.

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
- **The demo's recommendation limit is shared** by every visitor, so one visitor could use it up for the day. Set the limit and how it's enforced in issue #10 (cost and abuse safeguards).
- **Landing page sample:** one real recommendation, pre-computed, saved as JSON and labeled as real output. It's free, appears instantly, and still works while the backend is asleep.

## Database Schema (finalize column types in Milestone 1)
- `users`: id, email (unique), hashed_password, created_at
- `lures`: id, user_id (FK → users), catalog_lure_id (nullable FK → catalog_lures; null for lures the user added by hand), name, type, brand, color, size, technique, quantity (default 1), notes, created_at, updated_at
- `catalog_lures`: id, brand, model, type, technique, sizes (text[]), colors (text[]), source_name (`seed` for hand-seeded entries), source_url (nullable), last_scraped_at (nullable; set by the v2 scraper), created_at. Shared by all users; unique on (brand, model). `type` and `technique` use the same fixed lists as `lures`.
- `knowledge_base_entries`: id, title, content (text), category (e.g. clarity, season, structure, weather), condition tags (for example season, clarity, water temperature range; exact columns decided in Milestone 4), source_type (`personal` or `external`), source_name, source_url (nullable), embedding (vector, whose dimension must match the Voyage model's output), created_at. Shared by all users; not per-user.
- `recommendations`: id, user_id (FK → users), conditions (JSONB), retrieved_entry_ids (int[]), result (JSONB: the recommended lures with their reasoning, saved as a snapshot so the history still reads correctly if a lure is later deleted), worked (nullable boolean: the "did it work?" rating), created_at

Why JSONB for conditions and results: the set of conditions will probably change while the project is being built, and history rows are only ever read as a whole, never filtered by individual fields. If filtering by field becomes necessary later, move those fields into real columns with a migration.

## Recommendation Pipeline
1. The user submits the conditions form, and the request goes to `POST /api/v1/recommendations`.
2. The service builds a text query from the conditions (for example "stained water, early spring, 52°F water, windy, falling pressure, overcast").
3. The query is embedded with Voyage AI.
4. pgvector returns the top-k most similar knowledge base entries by cosine distance (start with k=5 and tune it).
5. The prompt sent to Claude contains the conditions, the retrieved entries and the user's lure inventory, with instructions to recommend **only** lures from that inventory, to explain why each one fits, and to prefer Erik's personal entries when retrieved entries conflict.
6. Claude returns structured output (lure IDs plus reasoning). The service checks that every returned ID belongs to the user's inventory, so the model can't recommend a lure the user doesn't own.
7. The service saves a `recommendations` row and returns the result.
8. Later, the user can rate it with `PATCH /api/v1/recommendations/{id}` (`worked: true/false`).

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
- **Reasoning (reviewed by Erik):** a hand review of a sample of explanations each run.
- LLM output varies, so each scenario runs about 3 times per variant and scores are averaged.

**Presentation:** publish a results table and a short write-up in the README. Any outcome is useful. If variant A matches C, that shows the knowledge base should focus on what Claude doesn't know (Erik's own patterns and local knowledge) rather than general bass-fishing advice.

## API Sketch
- Auth: `POST /api/v1/auth/signup`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- Lures: `GET/POST /api/v1/lures`, `GET/PATCH/DELETE /api/v1/lures/{id}`, all limited to the current user
- Recommendations: `POST /api/v1/recommendations`, `GET /api/v1/recommendations` (history), `PATCH /api/v1/recommendations/{id}` (rating)
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
Set up the repo structure, the layered backend skeleton, Alembic, and a local Postgres with pgvector. Hand-write signup, login and the JWT dependency. Deploy the backend to Render and Neon as a walking skeleton.
- **Decide:** where the frontend stores tokens (in memory with an `Authorization` header, or an httpOnly cookie). Look up the XSS/CSRF tradeoff and write an ADR.
- **Write ADRs:** stack, RAG vs. a trained model, hand-written auth.
- **Auth, hand-written in single-function steps** (Erik writes each one; Claude explains, points to docs and reviews):
  1. Hash a password and verify one (`pwdlib`), with tests
  2. Create a JWT with an expiry
  3. Decode and validate a JWT, rejecting ones that are expired or have a bad signature
  4. The `get_current_user` dependency
  5. The signup endpoint
  6. The login endpoint
- **Check-in (Claude: ask Erik after auth steps 1 and 2):** is the step-by-step approach working? If yes, continue through step 6. If it feels like no progress is being made, switch to the fallback in Growth Goal 1: Claude writes the rest of auth, Erik learns it until it can be explained line by line, then writes the "change password" endpoint alone.
- **Deploy:** a `/health` endpoint; the backend on Render and the database on Neon (with pgvector enabled); migrations run as part of each deploy; auto-deploy on merge to `main`; secrets only in Render's environment variables. Check Render's terms of service, then set up the keep-warm ping.
- **Done when:** a user can sign up, log in and call a protected endpoint, **on the live API**; migrations run cleanly from an empty database, locally and on Neon; merging to `main` deploys automatically; the auth logic has pytest tests.

### Milestone 2: Lure inventory API
CRUD endpoints for lures, limited to the current user.
- **Decide:** should `type` and `technique` be fixed lists (enums or lookup tables) or free text? Recommendation: fixed lists. Consistent values make it much easier for the LLM to match lures to knowledge base entries, while free text like "crank" vs. "crankbait" gets messy.
- **Decide (ADR):** when a lure is linked to the catalog, should its attributes be copied onto the user's row (simple, and users can edit them) or read through the link (no duplication, but harder to customize)? Include the nullable `catalog_lure_id` column either way.
- **Done when:** all lure endpoints work with validation, pagination and consistent errors; one user can never read or change another user's lures (with a test that proves it); service-layer tests pass.

### Milestone 3: Frontend inventory
Scaffold the React app. Build the signup and login pages and the inventory screens, working end to end. Deploy the frontend to Vercel, with auto-deploy on merge, and add the wake-up screen for the cold start.
- **Decide:** frontend tooling (Vite) and whether to use TypeScript. TypeScript is worth considering because it's widely expected in industry.
- **Done when:** a new user can sign up, log in, and add, edit and delete lures **on the live site** against the live API; the wake-up screen shows while the backend is waking.

### Milestone 4: Knowledge base and embeddings
**First, write the eval scenarios** (see Evaluation), before any knowledge base entries, like writing tests before code, and set the held-out third aside. Then Erik writes stage 1 of the knowledge base (50 to 150 entries from Erik's own knowledge, with condition tags and source fields) and Claude refines it. Build the embedding and seed pipeline with Voyage AI and pgvector.
- **Decide:** which Voyage embedding model to use. This sets the dimension of the `vector` column.
- **Decide:** the exact condition tag columns on `knowledge_base_entries`. They should match the condition form's values so variant D can filter on them.
- **Claude skill:** write the first custom skill here. A strong candidate: validating and adding knowledge base entries.
- **Done when:** the eval scenarios and the fixed test inventory are written, with the held-out set stored separately; all stage 1 entries are embedded and stored with tags and source fields; a manual similarity query for a sample set of conditions returns entries that make sense; the seed script can be re-run safely.

### Milestone 5: Recommendation pipeline
Build retrieval and the Claude generation step, including checking the output against the inventory. Build the recommendation endpoints and save history (ADR: JSONB for history).
- **Decide:** which Claude model to use, weighing cost against quality on this task. Compare a few real outputs before committing.
- **Done when:** `POST /recommendations` returns reasoned picks drawn only from the user's inventory; results are saved; ratings work; it's been tested against realistic combinations of conditions, including an empty or tiny inventory.

### Milestone 6: Evaluation
Build the eval harness and run all four variants (see Evaluation). Erik hand-writes the scoring functions and the variant comparison; Claude can help with the runner and boilerplate.
- **Decide:** where the harness lives in the repo and the format of the scenario files.
- **Done when:** all four variants run on every scenario (about 3 runs each); picks and retrieval are scored by code; Erik has reviewed a sample of the reasoning; the final numbers come from the held-out set; a results table and short write-up are drafted for the README.
- **Check-in (Claude: ask Erik when this milestone is finished):** based on the results, should stage 2 of the knowledge base (the larger expansion) happen before launch or after? Re-run the eval after the expansion either way.

### Milestone 7: Frontend recommendations
The conditions form, the results display, the history view and the "did it work?" rating.
- **Done when:** the whole flow works in the browser, from entering conditions to seeing results to rating them later from history.

### Milestone 8: Seeded lure catalog
Erik curates a data file (JSON or CSV) of 30 to 50 popular bass lures, storing facts only: brand, model, type, technique, sizes and color names. A seed script loads it into `catalog_lures`, and the add-lure screen gets catalog search. Roughly 3 to 5 hours, with no scraping.
- **Done when:** the seed script can be re-run safely without creating duplicates; users can search the catalog and add a lure from it, or still add one by hand; catalog entries use the same fixed `type` and `technique` lists as `lures`.

### Milestone 9: Demo and polish
The app has been live since Milestone 1, so this milestone is about the first impression. Build the shared demo account (seed data: a realistic inventory plus past recommendations with ratings) and its nightly reset, the landing page with a pre-computed real recommendation, and a "Try the demo" button. Polish the UI and write the README (including an architecture diagram, the eval results table from Milestone 6, and a note about the free tier's slow first request).
- **Decide:** how the nightly reset runs (for example a scheduled GitHub Actions workflow, which could also run the keep-warm ping).
- **Done when:** a first-time visitor sees a real recommendation within 10 seconds of opening the URL, without signing up; the demo data resets every night; the live URL works for a brand-new user; secrets are only in environment variables; the README explains how to run the app locally and how it works.

### Milestone 10: Showcase
Write a short demo write-up and consider a demo video for LinkedIn. Do a full mock-interview walkthrough of the codebase, and write the resume bullets (see `docs/CAREER_CONTEXT.md`).
- **Done when:** Erik can give a 5-minute walkthrough of the app and a 15-minute deep dive into the architecture, and answer every question in the interview question bank.

## Stretch Goals (after the core app ships)
- **Lure catalog v2:** expand the seeded catalog using official data feeds, or responsible scraping where allowed. Research sources, build the importer, and clean and de-duplicate the data (for example "KVD 1.5" vs. "KVD 1.5 Squarebill"). Before writing any scraper, check each site's `robots.txt` and terms of service, and write an ADR on which sources are used and why. Follow the data source rules in Decisions.
- Auto-fill conditions from Open-Meteo using the user's location
- Use the "did it work?" ratings to improve retrieval or re-rank recommendations
- A mobile client that reuses the same API
- Photo upload for lures
