# Interview Prep

Questions an interviewer might ask about this project, and the underlying skills. For each one, write the answer **in your own words** under "My answer", then practice saying it out loud. The key points are there to check your answer against, not to memorize.

---

## Git and GitHub

### How does `.gitignore` work? What happens if you add a file to it after it's already been committed?
**Key points:**
- Files are tracked, untracked or ignored. `.gitignore` patterns apply only to *untracked* files.
- Ignored files are skipped by `git add`, so they never get staged or committed, and therefore can never be pushed.
- Patterns: an exact path, `dir/` for a directory, `*` wildcards, and `!` to make an exception.
- If a file is already tracked, adding it to `.gitignore` does nothing. Use `git rm --cached <file>` to stop tracking it, and it will still be in the old history. That's why secrets belong in `.gitignore` before the first commit.
- The ignored file still exists on disk. It's hidden from Git, not backed up.

**My answer:**

### Walk me through your git workflow.
**Key points:**
- Four places code lives: working directory → staging area (`add`) → local repo (`commit`) → remote (`push`).
- The cycle: pull `main` → create a feature branch → make small commits → push → open a PR → review the diff → squash merge → update local `main` → delete the branch.
- `main` is protected: it needs a PR, even for admins, and force pushes are blocked.
- Conventional Commits, and short-lived branches to avoid merge conflicts.

**My answer:**

### What's the difference between commit, push and pull?
**Key points:**
- `add` and `commit` are local only. A commit is a snapshot saved in your local history.
- `push` uploads commits from the current branch. Uncommitted changes are never sent.
- `pull` = `fetch` (download) + `merge` into the current branch. Push and pull are the only commands that talk to the remote.

**My answer:**

### What is a squash merge, and what are the tradeoffs?
**Key points:**
- It combines all of a branch's commits into one new commit on `main`, giving a clean history with one commit per feature or PR.
- The tradeoff: the individual commit history of the branch is lost from `main`.
- The new commit has a different ID, so Git doesn't see the branch as merged. `git branch -d` warns, and `-D` is safe once the PR shows Merged.
- The alternatives are a merge commit (keeps every commit plus a merge commit) and rebase and merge (a linear history that keeps each commit).

**My answer:**

### Why go through PRs on a solo project?
**Key points:**
- Practice for team workflows, and a natural checkpoint to review changes before they reach `main`.
- AI-written code gets reviewed as a diff before merging instead of landing directly.
- Branch protection enforces it, so it doesn't depend on discipline alone.

**My answer:**

---

## Project design (answer these as each piece gets built)
- Why RAG instead of training a model?
- Why pgvector instead of a dedicated vector database like Pinecone?
- Why write your own JWT auth instead of using a library? How do you keep JWTs from being forged?
- What happens if the LLM recommends a lure the user doesn't own?
- Why store recommendation conditions and results as JSONB?
- How did you use AI tools on this project, and how did you catch it when they were wrong?
