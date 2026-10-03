---
name: milestone-brief
description: Brief Erik at the start (kickoff) or end (wrap-up) of a project milestone, using the plan, ADRs and interview prep
argument-hint: "[milestone number] [kickoff | wrap-up]"
arguments: [number, mode]
disable-model-invocation: false
---

# Purpose
Revisit the plan's decisions right when they become concrete. A kickoff explains what Milestone $number involves and why, before any work starts. A wrap-up checks that the milestone is really finished and turns it into something Erik can explain.

## What to read
Read the Milestone $number section of docs/PROJECT_PLAN.md.
The requested mode is $mode. Follow the matching section below.

For both modes, also read:
- The sections of **Decisions** in `docs/PROJECT_PLAN.md` that the milestone refers to or depends on (for example "see Evaluation" or "the safeguards from Decisions"), plus the Database Schema and API Sketch entries it touches.
- Any ADRs in `docs/decisions/` related to the milestone.
- "Working with Erik" in `CLAUDE.md`, for which pieces Erik hand-writes and how Claude helps with them.

## Kickoff mode
Produce a brief with these parts, in this order:
1. **What this milestone builds:** two or three sentences in plain language.
2. **Decisions that apply:** each relevant decision in one line, plus what it looks like in code (for example "token version: a `ver` claim in the JWT, compared in `get_current_user`"). Only decisions this milestone actually uses.
3. **Still to decide:** the milestone's "Decide" items, each with a recommendation and the main tradeoff. Don't decide them; Erik does.
4. **Hand-written pieces:** which parts Erik writes, broken into the plan's steps, and any check-ins Claude must remember (for example "ask after auth steps 1 and 2").
5. **Done when:** the milestone's checklist, as written in the plan.
6. **Interview questions:** the questions in `docs/INTERVIEW_PREP.md` this milestone will let Erik answer (at most three).
7. **First step:** one concrete action to start with, such as a decision to make or a branch to create.

## Wrap-up mode
Also read the "Every milestone also includes" list at the top of the Milestones section, and `docs/INTERVIEW_PREP.md`. Then produce a checklist:
1. **Done when:** go through each item and mark it done, not done, or "can't verify." Check the evidence where possible (tests, files, `git log`, the live app) instead of assuming.
2. **Every milestone also includes:** ADRs written for significant decisions, walkthrough notes in `docs/walkthroughs/` for new flows, interview questions added, and the explain-back.
3. **Explain-back:** ask Erik to explain what was built, why it's built that way and what the alternatives were. Don't explain it for him. Afterwards, point out any gaps.
4. **Interview questions:** for this milestone's questions, update the key points to match what was actually built and suggest any implementation questions that only showed up in the code. Remind Erik to write "My answer" now that the piece exists.
5. **Plan updates:** anything that changed during the milestone and should be reflected in `docs/PROJECT_PLAN.md` or `CLAUDE.md`.
6. **Check-ins:** any check-in the plan attaches to the end of this milestone.
7. **Next:** the next milestone's number and title, and a reminder to run `/milestone-brief <next> kickoff`.

## Rules
- If any of the arguments are missing, or don't match a milestone in the plan or one of the two modes, ask what they should be before reading files or writing the brief.
- Keep it to about one screen. Link to the plan for details instead of repeating it.
- Use plain language, and explain any term Erik hasn't used yet.
- Don't write implementation code for the hand-written pieces. Describe what they do, not how to code them.
- Kickoff is read-only: don't create or edit files. In wrap-up, edits to `docs/INTERVIEW_PREP.md` follow its rule in `CLAUDE.md`; ask before changing any other file.
