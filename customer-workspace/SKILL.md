---
name: customer-workspace
description: "Set up and operate customer workspaces: route customer updates, record meetings, track questions and actions, manage workstreams, and prepare handoffs. Use when creating or maintaining a customer workspace, processing meeting notes or updates, reviewing next actions, or preparing a handoff. Triggers: customer workspace, 顧客ワークスペース, inbox 追加, 議事録管理, 案件更新, 宿題管理, 引き継ぎ."
argument-hint: "Customer workspace name or an existing-workspace task (meeting, update, follow-up, handoff)"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Customer Workspace

Set up or operate customer workspaces without confusing setup artifacts with live records.

## When to Use

- Creating a per-customer workspace.
- Operating an existing workspace: inbox updates, meeting notes, questions, actions, workstreams, or handoffs.
- Adding customer-information routing or meeting-note workflows.
- Reviewing the current owner, next action, and source records before a handoff.

## Choose a Mode First

Inspect the workspace before choosing an action. Treat it as existing when it contains any managed record such as `.github/copilot-instructions.md`, `.github/prompts/`, `workspace-summary.md`, `_customer/profile.md`, `_inbox/`, or `workstreams/`.

| Mode | Use when | First action |
| ---- | -------- | ------------ |
| Setup | No managed structure exists | Create the scaffold and capture routing facts. |
| Operate | A managed workspace receives new information | Update the canonical record for the input. |
| Review / Handoff | Status, ownership, or continuity is requested | Read current indexes first and report sources, owner, and next action. |

- Do not rerun the initializer or use `-Force` in an existing workspace unless overwriting generated assets is explicitly requested.
- Existing records are authoritative. Add only explicitly requested missing assets; never replace live notes, tasks, or workstream records with templates.

---

## Setup a New Workspace

```powershell
# Basic
.\scripts\Initialize-CustomerWorkspace.ps1 -CustomerName "Contoso Inc"

# Full options
.\scripts\Initialize-CustomerWorkspace.ps1 `
  -CustomerName "Contoso Inc" `
  -ContractType "Ongoing support" `
  -ContractPeriod "2025/04 - 2028/03" `
  -KeyContacts "John Doe (Infra Lead)"
```

If PowerShell is unavailable, manually create the same folders and copy only the required prompt and template files from `assets/`.

Use setup only when the managed structure is absent. The initializer stops by default when managed assets exist; use `-Force` only for an explicitly approved replacement of generated prompts and templates.

## Setup Intake

Capture only routing facts: workspace scope, sharing boundary, own-team aliases, key roles, meeting cadence, and primary inputs. Leave detailed technical inventory to later inbox and meeting records.

## Canonical Records

| Need | Canonical record |
| ---- | ---------------- |
| Navigation and handoff | `README.md`, `workspace-summary.md` |
| Raw updates and open questions | `_inbox/`, `_questions/` |
| Customer context | `_customer/profile.md` |
| Meetings and follow-up | `meeting-notes/`, `next-actions/` |
| Ongoing scope and detailed history | `workstreams/`, `pj_{topic}/` |
| Deliverables and reusable learning | `research-reports/`, `_knowledge/` |

`Initialize-CustomerWorkspace.ps1` creates the managed scaffold and its templates. Create workstream folders, meeting notes, next actions, project threads, and material folders only when the operating workflow requires them.

## Research Reports

Use `research-reports/` for generated Markdown deliverables; keep the workspace root for entry files and controls. Detailed placement and sanitization rules are in [Knowledge Ledger Rules](references/knowledge-ledger-rules.md).

## Knowledge Ledger

Use `_knowledge/` only for compact, reusable learnings when the user explicitly requests extraction or generalization. Apply [Knowledge Ledger Rules](references/knowledge-ledger-rules.md) before writing.

## Optional Material Folders

When customer-shared files accumulate or are directly supplied in scope, split them by lifecycle: `_received/` for immutable originals, `_working/` for internal edits, and `_provided/` for customer-safe copies. Attempt to import accessible originals before relying only on a summary. Apply [Customer Material Lifecycle](references/material-lifecycle.md) before moving or renaming files.

---

## Operate an Existing Workspace

| Input or request | Action |
| ---------------- | ------ |
| Short chat, email, or unstructured update | Preserve it in `_inbox/` and classify it. |
| Meeting memo or Teams AI record | Create or update one meeting note and extract questions/actions in the same operation. |
| Clear update for one confirmed workstream | Update its README with the source link and state change. |
| New, ambiguous, or multi-workstream input | Record it in `workstreams/_candidates.md` and ask for confirmation. |
| Time-bounded follow-up | Track it in `next-actions/`; use `ongoing/` only when no next-meeting date is known. |
| Status review or handoff | Read `workspace-summary.md`, the portfolio, active actions, and open questions before reporting. |

Keep source records authoritative: summaries and workstreams link to meeting notes and inbox entries instead of duplicating them.

## Track Work

- A workstream README owns its current status, owner, actions, and timeline; the portfolio is its index. Create a workstream only after its name and scope are confirmed.
- Put customer-agreed homework, self-initiated proposals, and supplementary research in separate `next-actions/` folders. Task headers link back to their meeting source, while customer-shareable meeting tables exclude local task paths.
- Use only `candidate`, `not-started`, `in-progress`, `blocked`, `done`, or `dropped`. Before assigning `not-started` or `done`, inspect task-linked external work locations; workspace absence does not prove a deliverable is missing. When external progress and artifacts confirm completion, update the canonical action record and indexes in the same operation. Do not copy external artifacts unless the material lifecycle requires it. A `blocked` record names the current owner and its transition condition.
- Create `pj_{topic}/` only when the topic spans multiple meetings and meets the detailed project-thread split conditions.

## Meeting Notes Quality Gate

Before calling meeting notes done:

- Mark uncertain names, times, product names, prices, and support boundaries as `要確認`; verify ambiguous AI-generated follow-ups against the source before assigning owner, deadline, or deliverable.
- Extract open questions and work needing follow-up into `_questions/{YYYY-MM}.md` and `next-actions/` in the same operation.
- Keep local paths, internal links, internal speculation, and commercial terms out of customer-shareable content.
- Default to one working meeting note. Do not create `*_internal.md` solely for unverified technical details; separate only on explicit request or when sensitive material cannot remain in a clearly marked internal section.
- Customer highlights contain only confirmed items and split cross-side coordination into one `双方 (両者で調整)` bucket. Apply [Meeting Minutes Rules](references/meeting-minutes-rules.md) for details.

---

## Done Criteria

- Setup: the managed scaffold exists and routing facts are captured.
- Operate: the canonical record, related question/action ledger, and relevant index reflect the input without duplicate source content.
- Review / Handoff: the report identifies authoritative sources, current owner, next action, and unresolved questions.

## Key References

- [Inbox Rules](references/inbox-rules.md)
- [Meeting Minutes Rules](references/meeting-minutes-rules.md)
- [Workspace Summary Rules](references/workspace-summary-rules.md)
- [Workstream Portfolio Rules](references/workstream-portfolio-rules.md)
- [Knowledge Ledger Rules](references/knowledge-ledger-rules.md)
- [Customer Material Lifecycle](references/material-lifecycle.md)
- [Project Thread Rules](references/project-threads.md)

## Assets

> **Note**: `assets/` 配下の prompt / instruction / template は、新しい顧客ワークスペースを初期化するときの **コピー元** として使う scaffolding 用ファイル。ホスト workspace の `.github/prompts/` や `.github/copilot-instructions.md` とは独立に進化させてよい（同期は必須ではない）。ホスト側で機能追加した場合に scaffolding にも反映したいときは、明示的にこのフォルダへ back-port する。

- `assets/_templates/`: next-actions, knowledge ledger, attachments, and workspace templates
- `assets/*.prompt.md`: inbox, meeting-note conversion, and question extraction prompts
- `assets/copilot-instructions.md`: generated workspace auto-routing rules
- `scripts/Test-ReceivedMaterialPlacement.ps1` - Read-only root audit for unclassified received-material candidates
