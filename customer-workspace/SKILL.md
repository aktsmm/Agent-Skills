---
name: customer-workspace
description: Customer workspace initialization skill. Provides inbox (information accumulation), meeting minutes management, and auto-classification rules. Use for "setup customer workspace" or "add inbox feature" requests.
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
| **Next Actions**      | Per-MTG homework workspace with bidirectional links  |
| **Material Split**    | Optional split for customer originals, working copies, and customer-facing files |

---

## Quick Start

```powershell
# Basic
.\scripts\Initialize-CustomerWorkspace.ps1 -CustomerName "Contoso Inc"

# Full options
.\scripts\Initialize-CustomerWorkspace.ps1 `
  -CustomerName "Contoso Inc" `
  -ContractType "MACC" `
  -ContractPeriod "2025/04 - 2028/03" `
  -KeyContacts "John Doe (Infra Lead)"
```

If PowerShell is unavailable, manually create the same folders, copy the prompt/template files from `assets/`, and create `README.md` plus `workspace-summary.md` from the workspace root templates.

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
├── _customer/profile.md           ← Customer profile
├── _templates/                    ← Templates
├── meeting-notes/                 ← Meeting minutes (one file per MTG)
└── next-actions/                  ← Per-MTG homework workspace
    ├── to-YYYY-MM-DD/             ← Tasks for the next MTG
    │   ├── README.md               ← Progress board
    │   ├── homework/               ← Customer-agreed homework
    │   ├── proposals/              ← Self-initiated proposal prep
    │   └── research/               ← Supplementary research/validation
    └── ongoing/                    ← Continuing items without a deadline
```

## Optional Material Folders

When customer-shared diagrams, decks, tables, or schedules start to accumulate, split by lifecycle first and scope second.

```text
_received/                       ← customer originals only
  overall-architecture/          ← cross-meeting baseline material
  mtg-YYYY-MM-DD-name/           ← meeting-specific material

_working/                        ← internal edited / annotated / draft copies
  overall-architecture/
  mtg-YYYY-MM-DD-name/

_provided/                       ← customer-facing copies, send-out decks, projection versions
  overall-architecture/
  mtg-YYYY-MM-DD-name/
```

- Use `_received/` for customer originals and avoid editing files in place.
- Use `_working/` for annotated copies, extracted pages, redlines, and draft comparisons.
- Use `_provided/` only for versions safe to show or send to the customer.
- Use `overall-architecture/` when the material stays relevant across multiple meetings.
- Use `mtg-YYYY-MM-DD-name/` only when the material is truly scoped to one meeting.
- When a user says files were placed at the workspace root, inspect all root files first; treat PDFs, decks, spreadsheets, documents, images, and diagrams as possible received materials.
- Rename received originals with a date-prefixed stable name before classification. Leave only unclassified items in `_received/incoming/`.
- Check actual file signatures as well as extensions. For example, a `.pptx` file with an OLE/legacy Office signature should be handled as `.ppt`, and COM may be needed for content inspection.
- Review PDFs by all pages and decks by all slides before updating working summaries; do not summarize only the first pages or the first matching file.
- Read-only root audits can use `scripts/Test-ReceivedMaterialPlacement.ps1` from this skill.

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
- **Bidirectional links**:
  - In meeting notes, every decision/homework row links to the corresponding `next-actions/to-YYYY-MM-DD/.../xxx.md`.
  - In each task file, the header records `出どころ:` pointing back to the meeting note (or `自主提案` / `自主検証`).
- **Progress states**: `not-started` / `in-progress` / `blocked` / `done` / `dropped`. Only the state table lives in `to-YYYY-MM-DD/README.md`; details stay in each task file.
- **Why split by type**: mixing `proposals` into homework breaks the link to meeting notes and turns self-initiated ideas into apparent customer commitments.
- Full rules and templates: see `Next Actions Workspace` section in [assets/copilot-instructions.md](assets/copilot-instructions.md).

---

## Done Criteria

- [ ] Workspace folder created
- [ ] `README.md` exists at workspace root
- [ ] `workspace-summary.md` exists at workspace root
- [ ] `_inbox/{YYYY-MM}.md` exists
- [ ] `_questions/{YYYY-MM}.md` exists
- [ ] `_customer/profile.md` configured
- [ ] Auto-routing rules working

## Key References

- [Inbox Rules](references/inbox-rules.md)
- [Meeting Minutes Rules](references/meeting-minutes-rules.md)
- [Workspace Summary Rules](references/workspace-summary-rules.md)

## Assets

> **Note**: `assets/` 配下の prompt / instruction / template は、新しい顧客ワークスペースを初期化するときの **コピー元** として使う scaffolding 用ファイル。ホスト workspace の `.github/prompts/` や `.github/copilot-instructions.md` とは独立に進化させてよい（同期は必須ではない）。ホスト側で機能追加した場合に scaffolding にも反映したいときは、明示的にこのフォルダへ back-port する。

- `assets/_templates/` - Template files
- `assets/_templates/next-actions-readme.md` - Per-MTG progress board template
- `assets/_templates/next-actions-task.md` - Single task file template (homework / proposal / research)
- `assets/inbox.prompt.md` - Inbox prompt
- `assets/convert-meeting-minutes.prompt.md` - Meeting notes prompt
- `assets/extract-questions.prompt.md` - Question extraction prompt
- `assets/copilot-instructions.md` - Auto-routing rules
- `scripts/Test-ReceivedMaterialPlacement.ps1` - Read-only root audit for unclassified received-material candidates
