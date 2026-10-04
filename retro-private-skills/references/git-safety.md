# Git Safety Procedure

Detailed Git handling for `safe-auto`. The inline gate in `SKILL.md` stays authoritative.

## Mode Rules

- Fetch once and classify dirty/ahead paths in one batched command before editing. If the original checkout is clean and current, edit it directly; isolate only when unrelated dirty or divergence exists (prefer `git worktree add --detach` over a full clone). Verify private remote/allowed commits, integrate behind/divergence before push and revalidate. In `HEAD...refs/remotes/origin/<branch>`, left is ahead/right behind. After interruption, fetch/read back before retrying; never resend reflected commits.
- If Git repeats a `HEAD.lock` / `couldn't set HEAD` rename failure twice, answer `n` and stop retrying. Preserve uncommitted work; inspect HEAD, status, diffs, rebase metadata, and lock ownership. Restore index/worktree only when HEAD is unchanged and the half-applied tree is proven to match the fetched remote, then use a verified merge path that does not detach HEAD. Never `reset --hard`, force push, or delete locks blindly.
- Verify the push would send only local private-skill repo commits. Never run public sync, release, tag, force push, or push to a public repo without explicit user instruction.
- Treat dirty primary changes as authoring/intake material. Commit by owning skill; combine its related small edits and relevant formatting in one commit. Keep unrelated skills/paths separate and untouched.
- Before any `git add` / `git commit` / `git push`, set the working directory to the private repo root explicitly (`Set-Location <private-repo>` or `git -C <private-repo>`). Do not rely on inherited cwd from a previous tool call. After `commit` / `push`, re-confirm `git status --short --branch` to detect cwd mismatches early.

## Resolve and Inspect

- Run the Mode Rules fetch/classify/isolate/integrate sequence once and never stage unrelated paths. Batch preflight, scope and push-gate checks into single commands and avoid re-verifying state already read this run.
- Treat an isolated checkout of the verified private remote as the execution repo for path/clean checks. If approved dirty input is copied there, report the original copy as retained, not newly pending work; compare against the confirmed commit before suggesting another intake.
