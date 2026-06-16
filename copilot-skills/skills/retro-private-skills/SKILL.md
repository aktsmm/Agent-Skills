---
name: "retro-private-skills"
description: "Reflect reusable learnings into the private skill repository under .github/skills only. Use when: private skill retro, private skill repo authoring, private skill fix, create/update private SKILL.md, or converting the retro-private-skills prompt into Scout skill behavior."
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

If the best target appears to be an instruction, prompt, memory, or agent, stop with `scope 不一致`. For this skill, `New Skill Proposal` means a proposed or created `.github/skills/<new-skill>/SKILL.md`, not an instruction file.

## Intake Pre-Step (optional)

Intake は `~/.copilot/skills` と `~/.copilot/m-skills` を private repo の `copilot-skills/{skills,m-skills}/` へ機械的にミラーする前段。retro 育成本体とは別操作で、ユーザーが明示的に「取り込む / intake / 最新化」を求めたときだけ走る。retro 単発の既定は育成のみで、intake は実行しない（未育成の生コピー混入を防ぐ）。

- intake あり育成あり: 「`.copilot` から取り込んで育てて」-> intake -> 通常の retro 育成
- intake のみ: 「取り込むだけ」-> intake を実行し育成はスキップ
- 既定 (retro 単発): intake skip、育成のみ

実行は private repo の `scripts/Sync-CopilotSkillsToPrivateRepo.ps1`（旧 `sync-copilot-skills` skill から移設）。出自別に `copilot-skills/skills/` と `copilot-skills/m-skills/` へ分離コピーし、README を自動生成する。

この pre-step に限り、機械的ミラー先として `<private-repo>/copilot-skills/**` への書き込みを許可する。育成（authoring）部分は引き続き Hard Scope Gate（`.github/skills/<skill>/`）に従う。intake は copilot-skills へ、育成は .github/skills へ、で書き込み先を混在させない。

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

## Routing Rules

1. Extract each item into `Learning / Evidence / Impact`.
2. Prioritize by `Impact x Recurrence` as P1/P2/P3.
3. Inspect existing private skills before creating anything.
4. Route to the most specific existing skill when one clearly owns the behavior.
5. If no existing skill owns the behavior and the learning is reusable as a workflow, create a new private skill folder.
6. If the learning is workspace/customer/project-specific, abstract it before writing; if it cannot be safely abstracted, stop and hand off to a workspace retro instead.

## Edit Rules

- Prefer improving existing text over appending duplicate guidance.
- Compaction targets the minimum information the model needs to act; human readability is secondary.
- Use this refactor order: delete stale text -> merge/compact duplicates -> move long detail to `references/` -> add missing guidance.
- Keep `SKILL.md` lean; move detailed procedures, command examples, and examples to `references/*`.
- Treat `SKILL.md` as an entry point, not a general tutorial.
- Preserve non-obvious decision criteria, gotchas, done criteria, and failure-avoidance rules.
- Do not repeat the same `Learning / Evidence / Impact` in different wording.
- Do not store secrets, customer data, tenant-specific IDs, local absolute paths, tokens, or `/memories/**` content in the private skill repo.
- If a local absolute path is necessary as an example, replace it with a placeholder such as `<private-repo>`.

## Procedure

### 1. Resolve and Inspect

- Resolve private repo root.
- Verify `.github/skills/` exists.
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
- In `safe-auto`, optionally make a local commit when the scope is clear. Never push.

### 4. Bloat Check

After editing, check for duplicate rules, repeated definitions, and long examples. Compact, delete, or move detail to `references/` before reporting done.

### 5. Validate

Before final response:

- Check changed paths are all under `<private-repo>/.github/skills/`.
- Check no forbidden target was changed.
- Check `SKILL.md` frontmatter name matches folder name for new skills.
- Check description includes both what the skill does and when to use it.
- Check no obvious secret, customer data, tenant ID, or local absolute path was added.
- If making a commit, commit only intended private skill repo changes and never push.

## Output

Use this compact report:

```markdown
# Retro: [Title]
- Target: <private-repo>/.github/skills/<skill>/...
- Learnings: <what changed behavior>
- Changes: <files changed>
- Gate: pass / stop reason
```

Stop reasons: `入力不足` / `private repo 未解決` / `scope 不一致` / `Safety Gate 失敗` / `actionable な知見なし` / `新規 skill 候補` / `review-only`.
