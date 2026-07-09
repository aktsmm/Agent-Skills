---
name: customer-workspace
description: Customer workspace initialization skill. Provides inbox (information accumulation), meeting minutes management, and auto-classification rules. Use for "setup customer workspace" or "add inbox feature" requests. Triggers on customer workspace, 顧客ワークスペース, inbox 追加, 議事録管理, 顧客フォルダ作成.
argument-hint: "作りたい顧客ワークスペース名、必要機能、管理対象"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Customer Workspace Skill

Initialize customer-specific workspaces with information accumulation, meeting notes management, and handoff-ready summaries.

## When to Use

- **Customer workspace**, **inbox**, **meeting notes**, **workspace summary**, **handoff**
- Setting up per-customer workspaces
- Adding inbox or meeting minutes management
- Creating handoff-ready workspace summaries with source file paths
- Implementing auto-classification rules for customer information

## Features

| Feature               | Description                                          |
| --------------------- | ---------------------------------------------------- |
| **Inbox**             | Paste chat/email for auto-classification             |
| **Meeting Notes**     | Convert Teams AI notes to template format            |
| **Questions**         | Extract questions/actions from meeting log           |
| **Auto-Routing**      | Route input based on pattern detection               |
| **Customer Profile**  | Centralized customer information                     |
| **Workspace Summary** | Handoff summary with related file paths              |
| **Next Actions**      | Per-MTG homework workspace with traceable tasks       |
| **Knowledge Ledger**  | Reusable generic learnings extracted on request       |
| **Research Reports**  | Store generated research/report Markdown away from root |
| **Material Split**    | Optional split for customer originals, working copies, and customer-facing files |

---

## Quick Start

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

If PowerShell is unavailable, manually create the same folders, copy the prompt/template files from `assets/`, and create `README.md` plus `workspace-summary.md` from the workspace root templates.

## Setup Intake

Keep setup questions lightweight. Capture only facts that change routing, sharing, or follow-up behavior; leave detailed technical inventory to inbox and later notes.

- Workspace purpose and scope: customer-wide, project-specific, proposal, PoC, or ongoing support.
- Sharing boundary: customer-shareable, internal-only, or mixed. This controls what can appear in meeting notes.
- Own team names and aliases: used to split action items into own-team vs customer follow-up.
- Key contacts and roles: decision maker, technical owner, coordinator, or other routing-relevant roles.
- Meeting cadence and next date when known: used to create `next-actions/to-YYYY-MM-DD/`.
- Primary information sources: meetings, chat, email, shared files, received materials, or service portals.

## Generated Structure

```
{workspace}/
├── README.md                    ← Start here / workspace overview
├── workspace-summary.md         ← Handoff-ready summary
├── .github/
│   ├── copilot-instructions.md    ← Auto-routing rules
│   └── prompts/                   ← Inbox, meeting notes, questions
├── _inbox/{YYYY-MM}.md            ← Inbox files
├── _questions/{YYYY-MM}.md        ← Accumulated questions (optional)
├── _knowledge/                    ← Reusable generic learnings (opt-in extraction)
│   ├── README.md                   ← Rules, taxonomy, and safety gates
│   └── general.md                  ← Initial ledger; split later only when useful
├── _customer/profile.md           ← Customer profile
├── _templates/                    ← Templates
├── research-reports/              ← Generated research/report Markdown
├── meeting-notes/                 ← Meeting minutes (one file per MTG)
└── next-actions/                  ← Per-MTG homework workspace
    ├── to-YYYY-MM-DD/             ← Tasks for the next MTG
    │   ├── README.md               ← Progress board
    │   ├── homework/               ← Customer-agreed homework
    │   ├── proposals/              ← Self-initiated proposal prep
    │   └── research/               ← Supplementary research/validation
    └── ongoing/                    ← Continuing items without a deadline
```

## Research Reports

Use `research-reports/` for generated Markdown deliverables; keep the workspace root for entry files and controls. Detailed placement and sanitization rules are in [Knowledge Ledger Rules](references/knowledge-ledger-rules.md).

## Knowledge Ledger

Use `_knowledge/` only for compact, reusable learnings when the user explicitly requests extraction or generalization. Apply [Knowledge Ledger Rules](references/knowledge-ledger-rules.md) before writing.

## Optional Material Folders

When customer-shared files accumulate, split them by lifecycle: `_received/` for immutable originals, `_working/` for internal edits, and `_provided/` for customer-safe copies. Apply [Customer Material Lifecycle](references/material-lifecycle.md) before moving or renaming files.

---

## Auto-Routing Patterns

| Pattern                      | Action            |
| ---------------------------- | ----------------- |
| "Generated by AI"            | → Meeting notes   |
| Meeting memo with agenda / tasks / next meeting | → Meeting notes + Questions |
| Name + datetime + short text | → Inbox           |
| Contains `From:` `Date:`     | → Inbox           |
| Bullet points / short memo   | → Inbox           |
| Question format              | → Normal response |

## Default Tags

`#network` `#cost` `#contract` `#proposal` `#ai` `#container` `#meeting` `#support` `#organization` `#deadline` `#internal`

## Next Actions (per-MTG homework workspace)

Carve homework, proposal prep, and supplementary research out of meeting notes into a date-scoped `next-actions/to-YYYY-MM-DD/` folder.

- **Folders**: `homework/` (customer-agreed), `proposals/` (self-initiated), `research/` (supplementary)
- **Traceability**:
  - Keep meeting-note decision and homework tables copy-friendly: content, owner, due date, and status only. Do not put local `next-actions/...` paths in rows intended for sharing.
  - Track local work links in `next-actions/to-YYYY-MM-DD/README.md` and each task file instead.
  - In each task file, the header records `出どころ:` pointing back to the meeting note (or `自主提案` / `自主検証`).
- **Progress states**: `not-started` / `in-progress` / `blocked` / `done` / `dropped`. Only the state table lives in `to-YYYY-MM-DD/README.md`; details stay in each task file.
- **Why split by type**: mixing `proposals` into homework turns self-initiated ideas into apparent customer commitments.
- Full rules and templates: see `Next Actions Workspace` section in [assets/copilot-instructions.md](assets/copilot-instructions.md).

## Meeting Notes Quality Gate

Before calling meeting notes done:

- Mark uncertain names, times, product names, model names, prices, or support boundaries as `要確認` instead of overclaiming.
- Speech-to-text transcripts especially mishear short technical acronyms, time codes, and engagement names (e.g. `2H` heard from `EDE 時間`, `Entra ID` from `エントラ ID`). If a short token looks off in context, verify with the user or keep it as `要確認`.
- AI-generated follow-up tasks (Teams AI / Otter etc.) tend to be too literal or too generic. Cross-check with the body transcript and refine owner, deadline, and concrete deliverable. Do not leave ambiguous phrasing as-is.
- Extract open questions and action items into `_questions/{YYYY-MM}.md`; create `next-actions/` tasks only for work that needs follow-up outside the meeting note.
- Ensure shareable meeting-note tables contain no local file paths or internal-only work links.
- Keep internal speculation in an internal memo or clearly marked internal section.
- When the note will be shared with the customer, produce a copy-paste highlight block (`## お客様共有用ハイライト (コピペ用)`) with 3-5 confirmed bullets + next actions split into `お客様側 / 自社側 / 双方 (両者で調整)`. Cross-side coordination (schedule, joint review) goes in `双方` only — do not duplicate. See [references/meeting-minutes-rules.md](references/meeting-minutes-rules.md).

---

## Done Criteria

- [ ] Workspace folder created
- [ ] `README.md` exists at workspace root
- [ ] `workspace-summary.md` exists at workspace root
- [ ] `_inbox/{YYYY-MM}.md` exists
- [ ] `_questions/{YYYY-MM}.md` exists
- [ ] `_knowledge/README.md` and `_knowledge/general.md` exist
- [ ] `_customer/profile.md` configured
- [ ] `research-reports/` exists for generated Markdown deliverables
- [ ] Auto-routing rules working

## Key References

- [Inbox Rules](references/inbox-rules.md)
- [Meeting Minutes Rules](references/meeting-minutes-rules.md)
- [Workspace Summary Rules](references/workspace-summary-rules.md)
- [Knowledge Ledger Rules](references/knowledge-ledger-rules.md)
- [Customer Material Lifecycle](references/material-lifecycle.md)

## Assets

> **Note**: `assets/` 配下の prompt / instruction / template は、新しい顧客ワークスペースを初期化するときの **コピー元** として使う scaffolding 用ファイル。ホスト workspace の `.github/prompts/` や `.github/copilot-instructions.md` とは独立に進化させてよい（同期は必須ではない）。ホスト側で機能追加した場合に scaffolding にも反映したいときは、明示的にこのフォルダへ back-port する。

- `assets/_templates/`: next-actions, knowledge ledger, attachments, and workspace templates
- `assets/*.prompt.md`: inbox, meeting-note conversion, and question extraction prompts
- `assets/copilot-instructions.md`: generated workspace auto-routing rules
- `scripts/Test-ReceivedMaterialPlacement.ps1` - Read-only root audit for unclassified received-material candidates
