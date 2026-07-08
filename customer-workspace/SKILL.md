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

Use `research-reports/` for Markdown deliverables created by the agent or team, such as research notes, comparison memos, report drafts, and demo specification notes. Do not leave these generated artifacts at the workspace root; root should stay reserved for entry files and customer workspace controls.

## Knowledge Ledger

Use `_knowledge/` for compact, reusable learnings extracted from meetings, incidents, or research when the user explicitly asks for knowledge extraction, generalization, or lessons learned.

- Start with `_knowledge/general.md`; create category files only after entries accumulate enough to justify a split.
- Store short patterns, gotchas, decision criteria, and validation checklists. Long analysis belongs in `research-reports/`.
- Strip customer names, person names, ticket IDs, local paths, and unpublished/confidential specifics before writing reusable knowledge.
- Mark Microsoft product, pricing, support, or roadmap claims as needing official confirmation unless backed by a checked source URL.
- Link back to source meeting notes or reports; do not copy long transcripts.

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
- When screenshots or images are shared in a meeting context, save them as meeting artifacts with stable names and add an `attachments.md` manifest.
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

## Assets

> **Note**: `assets/` 配下の prompt / instruction / template は、新しい顧客ワークスペースを初期化するときの **コピー元** として使う scaffolding 用ファイル。ホスト workspace の `.github/prompts/` や `.github/copilot-instructions.md` とは独立に進化させてよい（同期は必須ではない）。ホスト側で機能追加した場合に scaffolding にも反映したいときは、明示的にこのフォルダへ back-port する。

- `assets/_templates/` - Template files
- `assets/_templates/next-actions-readme.md` - Per-MTG progress board template
- `assets/_templates/next-actions-task.md` - Single task file template (homework / proposal / research)
- `assets/_templates/knowledge-readme.md` - Reusable knowledge ledger rules and index
- `assets/_templates/knowledge-general.md` - Initial generic knowledge ledger
- `assets/_templates/attachments.md` - Meeting artifact manifest template
- `assets/inbox.prompt.md` - Inbox prompt
- `assets/convert-meeting-minutes.prompt.md` - Meeting notes prompt
- `assets/extract-questions.prompt.md` - Question extraction prompt
- `assets/copilot-instructions.md` - Auto-routing rules
- `scripts/Test-ReceivedMaterialPlacement.ps1` - Read-only root audit for unclassified received-material candidates
