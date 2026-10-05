---
name: sync-main
description: Clean up after a PR is squash merged on GitHub. Switches to main, pulls, and deletes the merged local branch, after checking it's safe.
argument-hint: "[branch] (optional, defaults to the current branch)"
arguments: [branch]
disable-model-invocation: true
---

# Purpose
This skill runs the cleanup commands needed after a PR is squash merged into main on GitHub. Erik calls it himself when it's time; Claude never runs it on its own.

The branch to clean up is $branch. If that's empty, use the current branch. If the current branch is `main` and no branch was given, stop and ask Erik which branch to clean up.

## Safety checks
Run every check before changing anything. If any check fails, stop immediately, tell Erik which check failed and why, and run no other step.

1. **No uncommitted changes.** `git status --porcelain` must print nothing. Uncommitted work would either block the switch to main or be carried onto main.
2. **The PR is merged on GitHub.** `gh pr view <branch> --json state,headRefOid` must show `"state": "MERGED"`. If there's no PR for the branch, that's a failure too.
3. **Nothing local is unmerged.** The local branch's latest commit (`git rev-parse <branch>`) must equal the PR's `headRefOid`, the last commit GitHub merged. If they differ, the branch has commits that were never merged, and deleting it would lose them.

If Erik is already on main and named a branch, tell him he's already on main and ask whether to continue. If he says yes, skip the switch step and run the rest.

## Steps
1. `git switch main`: leave the branch, since git can't delete the branch you're on.
2. `git pull --ff-only`: bring local main up to date with the squash commit. `--ff-only` refuses to create a merge commit, so if local main has somehow diverged from GitHub, it fails loudly instead of hiding the problem.
3. `git branch -D <branch>`: delete the local branch. A squash merge creates a new commit on main, so git doesn't see the branch's own commits as merged and `-d` refuses. `-D` forces it, which is safe only because safety checks 2 and 3 passed.
4. `git fetch --prune`: remove local references to remote branches that no longer exist on GitHub (like `origin/<branch>` after it's deleted there).

If any step fails, stop and show Erik the error. Don't try to fix it.

## Report
Prove the final state instead of assuming it. Run these and show their output:
- `git status -sb`: on main and in sync with `origin/main`
- `git log --oneline -1`: the newest commit on main, which should be the squash commit
- `git branch -a`: the branch is gone locally. If `remotes/origin/<branch>` is still listed, tell Erik the branch still exists on GitHub and he should delete it there.

## Rules
- Never push, force-push, or delete anything on GitHub. This skill only changes local state.
- Never delete `main`.
- Never stash, reset or discard changes to get past a failed check.
