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

### Workstream Portfolio

- When a workspace has multiple confirmed workstreams, link `workstreams/README.md` from the summary.
- Keep each workstream's current status, owner, actions, and timeline in its own README; the summary is an index and priority view, not a second status ledger.
- Keep unconfirmed workstream ideas in `workstreams/_candidates.md` until the user confirms the name and scope.

### Bring-Along vs Reference-Only

- Separate files to carry into the new workspace from files kept only for reference.
- Use this split when preparing a portable customer workspace package.

### Material-Heavy Workspaces

- Follow [Customer Material Lifecycle](material-lifecycle.md) for folder layout. In summaries, link the ledger README or index file rather than only a deep file path while the material set is still growing.

## Writing Rules

- Don't write only generic labels such as `日報`, `準備メモ`, or `タスク`.
- Point to the actual file path that contains the information.
- Keep the summary short and use linked source files as the drill-down path.
- If a summary mentions a task, meeting, or report, include the file that backs it up.

## Minimal Template

```markdown
## 関連ファイルパス

- workspace-summary.md
  - 起点メモ。最初に読むファイル
- \_customer/profile.md
  - 顧客の基本情報。正本
- meeting-notes/2026-05-20_regular.md
  - 直近会議の要点と宿題
- next-actions/README.md
  - 未完了アクションの確認先
```
