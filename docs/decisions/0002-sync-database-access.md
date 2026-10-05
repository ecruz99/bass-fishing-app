# ADR 0002: Sync database access with SQLAlchemy and psycopg 3

- **Status:** Accepted
- **Date:** 2026-10-05
- **Issue:** none

## Context
Every repository function, the session dependency and every test depend on one early choice: sync or async database access. FastAPI supports both:

- **Async (`async def`):** while a request waits on I/O, the same thread serves other requests. That needs an async driver and async SQLAlchemy sessions.
- **Sync (`def`):** FastAPI runs each request in a thread pool (about 40 threads by default), so a slow request blocks only its own thread.

The slowest request in the app is a recommendation, which waits a few seconds on Voyage and Claude. Expected traffic is a demo and a handful of real users. Recommendations are capped by per-user quotas, per-IP rate limits and the demo limits. Erik also has to be able to explain every line.

## Decision
Use **sync SQLAlchemy 2.x with the psycopg 3 driver**. Endpoints are plain `def` functions, each request gets one session from the `get_db` dependency, and repositories receive that session. The engine uses `pool_pre_ping` because Neon closes idle connections.

## Alternatives considered
- **Async SQLAlchemy with asyncpg:** best concurrency, but more complexity:
  - async test setup (`pytest-asyncio`)
  - lazy-loaded relationships raise `MissingGreenlet` instead of loading
  - a forgotten `await` causes confusing bugs

  The thread pool already covers the expected load, so the complexity buys nothing measurable. Rejected.
- **Async SQLAlchemy with psycopg 3 in async mode:** the same tradeoffs as asyncpg, with one driver for both modes. Rejected for the same reason. Keeping psycopg 3 for sync access preserves this as the migration path.
- **SQLModel:** combines Pydantic and SQLAlchemy models in one class, which conflicts with the plan's rule that Pydantic schemas stay separate from database models. Rejected.

## Consequences
- **Simpler code and tests:** repositories, services and tests are ordinary functions, and relationships can lazy-load.
- **A known ceiling:** about 40 requests can run at once, each blocked on I/O. Filling it would take about 40 recommendations at the same moment, well above what the limits allow. Render logs and the stored latency metrics would show if this ever becomes a problem.
- **Switching later is a refactor, not a rewrite:** psycopg 3 also supports async, so no driver change. But every repository function, the session dependency and the tests would change, so revisit before the codebase grows if the limits ever need to rise by an order of magnitude.
- **Sync API clients:** the Anthropic and Voyage calls use those SDKs' sync clients, to match the sync endpoints.
