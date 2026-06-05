---
name: sync-copilot-skills
description: "Sync installed Copilot/Clawpilot SKILL.md folders from the user's .copilot directory into the private skill repository. Use when sending local .copilot skills to the private repo, bulk-syncing skills, or refreshing private repo skill copies."
argument-hint: "同期対象の skill 名、省略時は全同期"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Sync Copilot Skills

Sync locally installed Skill folders from the user's `.copilot` directory into the private skill repository under `.github/skills/`.

## When to Use

- **sync skills**, **private repo sync**, **.copilot SKILL**, **ローカル skill 同期**
- Sending local `.copilot` skills to the private skill repo
- Bulk-refreshing private repo copies of local skills
- Creating/updating private Skill assets from installed local skills

## Default Behavior

- Sync all Skill folders by default.
- Source roots:
  - `%USERPROFILE%\.copilot\skills`
  - `%USERPROFILE%\.copilot\m-skills`
- Destination root: `<private-repo>\.github\skills`
- Resolve `<private-repo>` from `SYNC_PUBLIC_SKILLS_PRIVATE_REPO` first, then from `SYNC_PUBLIC_SKILLS_SCRIPT`.
- Exclude this sync skill itself: `sync-copilot-skills`.
- Copy each source skill folder recursively, including `SKILL.md`, `references`, `scripts`, and `assets` when present.
- Do not push to remote. Leave changes local for review or commit.

## Procedure

1. Run `scripts\Sync-CopilotSkillsToPrivateRepo.ps1` from this skill folder.
2. If the user specified skill names, pass them with `-SkillName`.
3. Otherwise, run without `-SkillName` to sync every local skill except this skill.
4. Inspect `git status --short` in the private repo.
5. Report changed destination paths and note that remote push was not performed.

## Commands

```powershell
# Sync all local skills to the private repo
.\scripts\Sync-CopilotSkillsToPrivateRepo.ps1

# Sync selected skills only
.\scripts\Sync-CopilotSkillsToPrivateRepo.ps1 -SkillName project-workspace,receipt-ocr

# Preview planned operations
.\scripts\Sync-CopilotSkillsToPrivateRepo.ps1 -DryRun
```

## Safety Rules

- Never sync `sync-copilot-skills` itself.
- Do not write outside `<private-repo>\.github\skills`.
- Do not edit `~\.copilot` during sync; it is read-only source.
- Do not delete private repo skills that no longer exist locally unless the user explicitly asks for cleanup.
- Treat sync as backup/staging, not shared promotion. Do not make every synced skill a default recommendation or public/shared source without observed use.
- Do not push automatically.
- If private repo resolution fails, stop with `private repo 未解決`.

## Reporting

- Report the private repo path first.
- Mention how many skills were synced and which were skipped.
- Keep the response concise in Japanese.
