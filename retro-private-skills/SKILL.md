---
name: "retro-private-skills"
description: "Reflect reusable learnings into a private Agent Skills repository with scoped safety gates and same-run private commit/push. Use when: skill retro, private skill authoring, skill repository fix, create or update SKILL.md."
argument-hint: "反映したい学び、対象 skill 名、private repo path、mode（safe-auto / review-only / dry-run）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# retro private skills

Reflect reusable learnings from a session, incident, diff, error, or prompt into the user's **private skill repository**. The default output is a focused change under the private repo's `.github/skills/<skill>/` tree. Do not convert these learnings into personal instructions, prompts, memories, agents, workspace files, or public sync output.

## When to Use

- User says: **private skill retro**, **private skill repo**, **skill repo authoring**, **private skill fix**, **retro private skills**, `/retro-private-skills`
- User provides Learnings / Evidence / Impact and wants them reflected into reusable Skill behavior
- User wants to create or update private repo `SKILL.md` / `references/*`
- A prior attempt wrote to `~/.copilot/instructions`, `copilot-instructions.md`, VS Code User Data prompts, or local `.copilot` skills, and the user wants the private repo Skill version instead

## Inputs

Accept one or more of: error log, Git diff, conversation summary, terminal history, target skill name, private repo path, or mode (`safe-auto`, `review-only`, `dry-run`, `プレビュー`). If none are present, stop with `入力不足` and ask for the missing input.

## Hard Scope Gate

Allowed write targets are limited to:

- `<private-repo>/.github/skills/<skill>/SKILL.md`
- `<private-repo>/.github/skills/<skill>/references/*`
- `<private-repo>/.github/skills/<skill>/scripts/*`
- `<private-repo>/.github/skills/<skill>/assets/*`

Never write to these targets for this workflow unless the user explicitly asks to improve that exact asset:

- `~/.copilot/instructions/**`
- `~/.copilot/copilot-instructions.md`
- `~/.copilot/skills/**`
- `~/.copilot/m-skills/**`
- VS Code User Data prompts or instructions
- workspace `.github/**`, `AGENTS.md`, or repository-specific instructions
- memories, public sync output or remote targets other than the verified private origin authorized by safe-auto

If the best target appears to be an instruction, prompt, memory, or agent, stop with `scope 不一致`. For this skill, `New Skill Proposal` means a proposed or created `.github/skills/<new-skill>/SKILL.md`, not an instruction file. Content written back to a skill must be self-contained and portable; do not depend on a workspace file, memory note, local absolute path, or environment-specific ledger remaining available.

## Intake Pre-Step (optional)

Intake is a separate, explicit pre-step for mirroring local Copilot skills. Skip it for a normal retro. When requested, follow [Private Skill Intake Workflow](references/intake-workflow.md); only that pre-step may write under `<private-repo>/copilot-skills/**`, while curated authoring remains under `.github/skills/<skill>/`.

## Private Repo Resolution

Resolve the private repo root in this order:

1. Explicit private repo path from the user
2. `SYNC_PUBLIC_SKILLS_PRIVATE_REPO` from Process/User/Machine environment; if `$env:` is empty, explicitly check `[Environment]::GetEnvironmentVariable(name, 'Process'/'User'/'Machine')` before declaring it unset
3. Parent repo inferred from `SYNC_PUBLIC_SKILLS_SCRIPT`
4. Current workspace only if it contains `.github/skills/` and is clearly the private skill repo

After resolution, verify that `.github/skills/` exists. If not, stop with `private repo 未解決`.

## Mode

- Default: `safe-auto`
- `review-only`, `dry-run`, or `プレビュー`: propose target changes and stop before editing
- In `safe-auto`, edit directly when scope is clear, the safety gate passes, and the change is small or medium
- Confirm unclear scope, new privileges/destinations/visibility/defaults, destructive deletion or uncertain sensitive data. Otherwise use safe-auto without reapproval; read-only and holds take precedence.
- In `safe-auto`, create a focused local commit and push it in the same run. There is no ahead-count threshold: several PCs share this repo, so a local commit left behind means the next machine starts from a stale tree. Invoking this skill counts as the push approval. To keep a draft local instead, use `review-only` or `dry-run`.
- Fetch once and classify dirty/ahead paths in one batched command before editing. If the original checkout is clean and current, edit it directly; isolate only when unrelated dirty or divergence exists (prefer `git worktree add --detach` over a full clone). Verify private remote/allowed commits, integrate behind/divergence before push and revalidate. In `HEAD...refs/remotes/origin/<branch>`, left is ahead/right behind. After interruption, fetch/read back before retrying; never resend reflected commits.
- If Git repeats a `HEAD.lock` / `couldn't set HEAD` rename failure twice, answer `n` and stop retrying. Preserve uncommitted work; inspect HEAD, status, diffs, rebase metadata, and lock ownership. Restore index/worktree only when HEAD is unchanged and the half-applied tree is proven to match the fetched remote, then use a verified merge path that does not detach HEAD. Never `reset --hard`, force push, or delete locks blindly.
- Verify the push would send only local private-skill repo commits. Never run public sync, release, tag, force push, or push to a public repo without explicit user instruction.
- Treat dirty primary changes as authoring/intake material. Commit by owning skill; combine its related small edits and relevant formatting in one commit. Keep unrelated skills/paths separate and untouched.
- Do not run public, internal, or EMU sync from this skill. If distribution is needed, hand off the primary to `sync-public-skills` in the completion report.

## Routing Rules

1. Extract each item into `Learning / Evidence / Impact`.
2. Prioritize by `Impact x Recurrence` as P1/P2/P3.
3. Inspect existing private skills before creating anything.
4. Route to the most specific existing skill when one clearly owns the behavior.
4b. **Multi-target case**: when a learning is a cross-cutting principle that several skills must own independently to stay Self-Contained (for example: tool-platform constraints, push-threshold rules, gate items that each skill verifies locally), apply it to every affected skill as a 1-line gate. Each copy must be a tiny independent SSOT, not a hard reference to a primary; same wording across files is allowed when portability requires it. Do not copy the same long block — keep each insertion to one line of judgment.
4c. **Multi-learning case**: when one incident produces several independent learnings with different owning skills, split them and update each owning skill in the same retro turn. Do not force all learnings into the first plausible skill. Example: deck artifact folder design belongs to planning/workspace skills, while generation/editing mechanics belong to automation skills.
5. If no existing skill owns the behavior and the learning is reusable as a workflow, create a new private skill folder.
6. If the learning is workspace/customer/project-specific, abstract it before writing; if it cannot be safely abstracted, stop with `scope 不一致` and suggest a workspace-scoped record or workflow instead.

## Edit Rules

- Prefer improving existing text over appending duplicate guidance.
- Before writing a new rule, check whether the repository already implements the same decision in scripts, generated assets, or another skill. A rule that contradicts working code makes the next run "fix" assets that were already correct.
- A single negative observation is not a rule. Before writing "the feature is absent here", rule out authentication state, extension activation, and mode: a half-initialised client renders its surrounding UI while omitting the entries you were looking for. If you cannot rule them out, record the observation with its conditions rather than as an absolute.
- Compaction targets the minimum information the model needs to act; human readability is secondary.
- Use this refactor order: delete stale text -> merge/compact duplicates -> move long detail to `references/` -> add missing guidance.
- Keep `SKILL.md` lean; move detailed procedures, command examples, and examples to `references/*`.
- Treat `SKILL.md` as an entry point, not a general tutorial.
- Do not add generic or obvious process advice; prefer gotchas, verification checks, and failure-avoidance rules that change future behavior.
- Preserve non-obvious decision criteria, gotchas, done criteria, and failure-avoidance rules.
- Do not repeat the same `Learning / Evidence / Impact` in different wording.
- Do not store secrets, customer data, tenant-specific IDs, local absolute paths, tokens, or `/memories/**` content in the private skill repo.
- If a local absolute path is necessary as an example, replace it with a placeholder such as `<private-repo>`.
- Before any `git add` / `git commit` / `git push`, set the working directory to the private repo root explicitly (`Set-Location <private-repo>` or `git -C <private-repo>`). Do not rely on inherited cwd from a previous tool call. After `commit` / `push`, re-confirm `git status --short --branch` to detect cwd mismatches early.

## Procedure

### 1. Resolve and Inspect

- Resolve private repo root.
- Verify `.github/skills/` exists.
- Fetch before checking status/ahead/behind. Classify dirty and queued paths, isolate unrelated dirty only when present, integrate behind/divergence in the clean execution checkout, and never stage unrelated paths. Batch preflight, scope and push-gate checks into single commands and avoid re-verifying state already read this run.
- Treat an isolated checkout of the verified private remote as the execution repo for path/clean checks. If approved dirty input is copied there, report the original copy as retained, not newly pending work; compare against the confirmed commit before suggesting another intake.
- List candidate skills and read the most likely `SKILL.md` files. For large repos or thorough audits, delegate this inventory step to a sub-agent so scope is settled before extracting learnings.
- If a `skill-creator-plus` skill exists in the private repo, follow its structure and review guidance for new or heavily changed skills.

### 2. Decide Target

Choose exactly one:

- **Update existing skill**: the learning changes how an existing workflow should behave.
- **Add reference to existing skill**: the detail is useful but too long for `SKILL.md`.
- **Create new private skill**: the learning forms a distinct reusable workflow and no existing skill owns it.
- **Stop**: the input is not actionable or belongs outside private `.github/skills/`.

### 3. Apply

- Edit only under `<private-repo>/.github/skills/<skill>/`.
- Keep the diff focused and small.
- For new skills, create at minimum `SKILL.md` with frontmatter: `name`, `description`, `argument-hint`, `user-invocable`, `license`, and `metadata.author` when the repo convention uses them.
- Add `references/` only when detail would bloat `SKILL.md`.
- Verify table/formatter drift; group relevant formatting with the owning skill's small change. Separate unrelated normalization; never blanket-stage or split one bounded improvement into repeated pushes.
- In `safe-auto`, make a focused local commit when the scope is clear and all changed paths are intended, then push it in the same run after the automatic-push checks pass.

### 4. Bloat Check

After editing, check for duplicate rules, repeated definitions, and long examples. Compact, delete, or move detail to `references/` before reporting done.

### 5. Validate

Before final response:

- Check changed paths are all under `<private-repo>/.github/skills/`.
- Check no forbidden target was changed.
- Parse YAML frontmatter for every changed `SKILL.md`, even one-line edits. Check `name` against the folder, `description` triggers and `argument-hint` against the current use case, and `user-invocable`, `license`, and `metadata.author` against repo conventions; metadata lint alone cannot detect a stale hint.
- Check no obvious secret, customer data, tenant ID, or local absolute path was added. Scan added lines or the staged target content; do not scan unchanged diff context, which can trigger false positives on pre-existing terms.
- Commit/push intended private skill changes in safe-auto after remote/scope checks. Done means the execution checkout is clean with ahead/behind `0/0`; original unrelated dirty is preserved and reported, not a completion blocker.
- List up to three read-only candidates: dirty -> Retro; pending private commits -> ahead-range review; committed public-safe gap -> separately requested sync. Honor holds/visibility; never expand operations or offer private/internal/denied content for public sync.

## Output

Use this compact report:

```markdown
# Retro: [Title]
- Target: <private-repo>/.github/skills/<skill>/...
- Learnings: <what changed behavior>
- Changes: <files changed>
- Commit: <hash or none>
- Gate: pass / stop reason
```

Stop reasons: `入力不足` / `private repo 未解決` / `scope 不一致` / `Safety Gate 失敗` / `actionable な知見なし` / `新規 skill 候補` / `review-only`.

