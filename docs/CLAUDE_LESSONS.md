# Claude Lessons

A log of times Claude Code went wrong on this project: what happened, how it was caught, and what fixed it. Using AI tools well includes noticing when they drift and correcting them, so this log is part of the project's growth goals (see `docs/PROJECT_PLAN.md`, Growth Goal 3).

## Entry template

```
## YYYY-MM-DD: Short title
**What happened:**
**How it was caught:**
**Why it happened:**
**Fix:**
**Rule going forward:**
```

---

## 2026-10-02: Built a feature after only being asked about it

**What happened:** I asked Claude whether a flashcard-style practice page (a Claude artifact) would be a good alternative to copying interview answers into a notes app. Claude took the question as approval. In one go it wrote the page, published it, loaded my answers into it, and edited my notes file to link to it, without checking in first.

**How it was caught:** I noticed afterward that I had only asked a question and never said to build it. My own `CLAUDE.md` already says Claude should "suggest decisions with a recommendation; don't make them silently," so this broke an existing rule.

**Why it happened:** Claude leans toward taking action. A request phrased as "what about X?" can mean "evaluate X" or "do X," and Claude picked "do X." I also didn't interrupt while it was working, even though each step was visible.

**Fix:** I pointed out what happened and asked what it should teach me. Claude acknowledged the mistake and saved a memory, pinned for every session, to treat "what about X?" or "would X be good?" as a request for a recommendation and to wait for an explicit go-ahead before building. Claude then offered to keep, change or delete the page, leaving that decision to me.

**Rule going forward:**
- Questions get answers, not actions. If I want something built, I'll say "build it" or "do it."
- When I only want an evaluation, I'll say so ("don't build anything yet"). For bigger work I'll use plan mode, which stops Claude from editing files until I approve a plan.
- If Claude starts doing something I didn't ask for, I'll press Esc right away instead of letting it finish.
- If this happens again, I'll add an explicit rule to `CLAUDE.md`.
