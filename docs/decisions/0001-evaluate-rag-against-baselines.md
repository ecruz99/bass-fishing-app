# ADR 0001: Evaluate RAG against baselines

- **Status:** Accepted
- **Date:** 2026-10-02
- **Issue:** #8

## Context
Recommendations use RAG: retrieve knowledge base entries relevant to the conditions, then have Claude pick lures from the user's inventory. Two questions undermine that design if they can't be answered with data:

1. **Does the knowledge base help at all?** Claude already knows a lot about bass fishing.
2. **Why retrieve instead of sending the whole knowledge base?** Stage 1 is 50 to 150 entries (roughly 20k tokens), which fits in a single prompt.

The only planned quality signal was the users' "did it work?" rating, which will be too sparse to measure anything with few users.

## Decision
Build an eval harness and compare four variants:

- **A.** No knowledge base (baseline)
- **B.** The whole knowledge base in the prompt
- **C.** Vector top-k retrieval
- **D.** Filter by condition tags, then rank by vector similarity

Erik writes 30 to 50 scenarios, each with good and bad picks by lure type, and runs them against a fixed test inventory. About a third of the scenarios are held out while the knowledge base is written. Code scores picks and retrieval recall@5, and Erik reviews a sample of the reasoning. Each scenario runs about 3 times per variant. Results are published in the README. The full design is in the Evaluation section of `docs/PROJECT_PLAN.md`.

## Alternatives considered
- **No eval; rely on user ratings.** Rejected: too little data, and it can't compare designs.
- **A lighter eval (15 to 20 scenarios, picks only).** Rejected: too few cases to trust differences between variants, and it can't tell retrieval misses from generation misses.
- **Scoring every output by hand, or with an LLM judge.** Rejected for now. Hand-scoring 200+ outputs per run is too slow, and an LLM judge would need its own validation. Structured output lets code score the picks; a hand-reviewed sample covers the reasoning.
- **Running the eval after launch.** Rejected: the RAG claim would go live without evidence.

## Consequences
- A new Milestone 6 (Evaluation) is added after the pipeline, and later milestones shift by one.
- Scenarios are written in Milestone 4, before the knowledge base entries.
- Knowledge base entries need condition tags (for variant D) and source fields.
- Variant A may score as well as C. If it does, the knowledge base should focus on what Claude doesn't know, such as Erik's own patterns and local knowledge, rather than general advice.
- Variant B stops being viable as the knowledge base grows. The eval shows where that crossover happens, which answers "why retrieve?"
