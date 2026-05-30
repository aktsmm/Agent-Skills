# Workspace Summary Rules

> This file describes reusable rules for customer workspace summaries and handoff notes.
> Overview is in [SKILL.md](../SKILL.md).

## When to Use

- Creating a new customer workspace and leaving a starting summary
- Preparing a handoff note for another person
- Writing a workspace summary that should work as a navigation entry point

## Required Sections

### Related File Paths

- Include a `関連ファイルパス` or equivalent section.
- Use workspace-relative paths.
- Add one short line for each file's role.

### Source of Truth

- Mark the latest authoritative file as `正本` or `確認先` when applicable.
- Don't force readers to infer which file is current.

### Bring-Along vs Reference-Only

- Separate files to carry into the new workspace from files kept only for reference.
- Use this split when preparing a portable customer workspace package.

### Material-Heavy Workspaces

- If customer-shared files such as diagrams, decks, schedules, or comparison tables are part of the ongoing work, split folders by lifecycle first: `_received/`, `_working/`, `_provided/`.
- Within those folders, use `overall-architecture/` for cross-meeting baseline material and `mtg-YYYY-MM-DD-name/` only for truly meeting-scoped material.
- In summaries, link the ledger README or index file rather than only a deep file path when the material set is still growing.

## Writing Rules

- Don't write only generic labels such as `日報`, `準備メモ`, or `タスク`.
- Point to the actual file path that contains the information.
- Keep the summary short and use linked source files as the drill-down path.
- If a summary mentions a task, meeting, or report, include the file that backs it up.

## Minimal Template

```markdown
## 関連ファイルパス

- Customers/contoso/workspace-summary.md
  - 起点メモ。最初に読むファイル
- Customers/contoso/profile.md
  - 顧客の基本情報。正本
- Customers/contoso/\_meetings/2026-05-20.md
  - 直近会議の要点と宿題
- Tasks/active.md
  - 全体タスクの確認先。必要なら顧客該当箇所を抜粋
```
