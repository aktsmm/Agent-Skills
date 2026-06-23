---
name: "retro-private-skills"
description: "Reflect reusable learnings into the private skill repository under .github/skills only, with safe-auto local commit and conditional push when the private repo is 3+ commits ahead. Use when: private skill retro, private skill repo authoring, private skill fix, create/update private SKILL.md, or converting the retro-private-skills prompt into Scout skill behavior."
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
- memories, public sync output, remote push targets

If the best target appears to be an instruction, prompt, memory, or agent, stop with `scope 不一致`. For this skill, `New Skill Proposal` means a proposed or created `.github/skills/<new-skill>/SKILL.md`, not an instruction file. Content written back to a skill must be self-contained and portable; do not depend on a workspace file, memory note, local absolute path, or environment-specific ledger remaining available.

## Intake Pre-Step (optional)

Intake は `~/.copilot/skills` と `~/.copilot/m-skills` を private repo の `copilot-skills/{skills,m-skills}/` へ機械的にミラーする前段。retro 育成本体とは別操作で、ユーザーが明示的に「取り込む / intake / 最新化」を求めたときだけ走る。retro 単発の既定は育成のみで、intake は実行しない（未育成の生コピー混入を防ぐ）。

- intake あり育成あり: 「`.copilot` から取り込んで育てて」-> intake -> 通常の retro 育成
- intake のみ: 「取り込むだけ」-> intake を実行し育成はスキップ
- 既定 (retro 単発): intake skip、育成のみ

実行は private repo の `scripts/Sync-CopilotSkillsToPrivateRepo.ps1`。出自別に `copilot-skills/skills/` と `copilot-skills/m-skills/` へ分離コピーし、README を自動生成する。

この pre-step に限り、機械的ミラー先として `<private-repo>/copilot-skills/**` への書き込みを許可する。育成（authoring）部分は引き続き Hard Scope Gate（`.github/skills/<skill>/`）に従う。intake は copilot-skills へ、育成は .github/skills へ、で書き込み先を混在させない。

Intake 対象と同名の curated private skill が `<private-repo>/.github/skills/<skill>/` に存在する場合は、`copilot-skills/**` へのミラー前に停止する。curated skill と raw mirror の同名併存は、意図的に扱う場合だけユーザー確認後に別方針を決める。

## Private Repo Resolution

Resolve the private repo root in this order:

1. Explicit private repo path from the user
2. `SYNC_PUBLIC_SKILLS_PRIVATE_REPO` from Process/User environment
3. Parent repo inferred from `SYNC_PUBLIC_SKILLS_SCRIPT`
4. Current workspace only if it contains `.github/skills/` and is clearly the private skill repo

After resolution, verify that `.github/skills/` exists. If not, stop with `private repo 未解決`.

## Mode

- Default: `safe-auto`
- `review-only`, `dry-run`, or `プレビュー`: propose target changes and stop before editing
- In `safe-auto`, edit directly when scope is clear, the safety gate passes, and the change is small or medium
- Ask for confirmation only for broad rewrites, deletion, ambiguous private/public boundaries, or possible secret/customer/private data handling
- In `safe-auto`, create a focused local commit by default. If the private repo is 3 or more commits ahead of origin after the commit, push without an additional explicit user instruction. If it is 1-2 commits ahead, do not push.
- Before any automatic push, verify the remote is the private repo, the working tree is clean, and the push would send only local private-skill repo commits. Never run public sync, release, tag, force push, or push to a public repo without explicit user instruction.
- Treat dirty primary skill changes as authoring or intake material. In safe-auto, stage and commit only the target skill changes, and leave unrelated dirty paths untouched.
- Do not run public, internal, or EMU sync from this skill. If distribution is needed, hand off the primary to `sync-public-skills` in the completion report.

## Routing Rules

1. Extract each item into `Learning / Evidence / Impact`.
2. Prioritize by `Impact x Recurrence` as P1/P2/P3.
3. Inspect existing private skills before creating anything.
4. Route to the most specific existing skill when one clearly owns the behavior.
5. If no existing skill owns the behavior and the learning is reusable as a workflow, create a new private skill folder.
6. If the learning is workspace/customer/project-specific, abstract it before writing; if it cannot be safely abstracted, stop with `scope 不一致` and suggest a workspace-scoped record or workflow instead.

## Edit Rules

- Prefer improving existing text over appending duplicate guidance.
- Compaction targets the minimum information the model needs to act; human readability is secondary.
- Use this refactor order: delete stale text -> merge/compact duplicates -> move long detail to `references/` -> add missing guidance.
- Keep `SKILL.md` lean; move detailed procedures, command examples, and examples to `references/*`.
- Treat `SKILL.md` as an entry point, not a general tutorial.
- Do not add generic or obvious process advice; prefer gotchas, verification checks, and failure-avoidance rules that change future behavior.
- Preserve non-obvious decision criteria, gotchas, done criteria, and failure-avoidance rules.
- Do not repeat the same `Learning / Evidence / Impact` in different wording.
- Do not store secrets, customer data, tenant-specific IDs, local absolute paths, tokens, or `/memories/**` content in the private skill repo.
- If a local absolute path is necessary as an example, replace it with a placeholder such as `<private-repo>`.

## Procedure

### 1. Resolve and Inspect

- Resolve private repo root.
- Verify `.github/skills/` exists.
- Check `git status --short --branch` plus ahead/behind, and classify dirty paths by skill. Do not stage dirty paths outside the target skill.
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
- For heavily changed existing skills, re-check frontmatter instead of assuming old metadata still routes correctly.
- Add `references/` only when detail would bloat `SKILL.md`.
- In `safe-auto`, make a local commit by default when the scope is clear and all changed paths are intended. Then push only when the private repo is 3+ commits ahead of origin and the automatic-push checks pass.

### 4. Bloat Check

After editing, check for duplicate rules, repeated definitions, and long examples. Compact, delete, or move detail to `references/` before reporting done.

### 5. Validate

Before final response:

- Check changed paths are all under `<private-repo>/.github/skills/`.
- Check no forbidden target was changed.
- Check `SKILL.md` frontmatter name matches folder name for new or heavily changed skills.
- Check description includes both what the skill does and when to use it, with trigger phrases users actually say.
- Check required optional metadata is intentional: `argument-hint`, `user-invocable`, `license`, and `metadata.author` when the repo convention uses them.
- Check no obvious secret, customer data, tenant ID, or local absolute path was added.
- Commit by default in `safe-auto`; commit only intended private skill repo changes. Push only when the private repo is 3+ commits ahead of origin and the remote/clean-tree checks pass.

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
