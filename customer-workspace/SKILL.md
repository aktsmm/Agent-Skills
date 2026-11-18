---
name: customer-workspace
description: "Set up dedicated customer workspaces and coordinate meeting notes, actions, and workstreams for ongoing customer accounts. Use for 顧客ワークスペースの作成, 顧客案件の棚卸し・引き継ぎ, 議事録と宿題・案件台帳の一括反映, or customer record maintenance without a matching workspace-local workflow. Not for general questions, standalone PoC workspaces, or single updates already covered by a local workflow."
argument-hint: "顧客名と作成先、または既存の顧客ワークスペースで行う作業（議事録・案件整理・引き継ぎ）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Customer Workspace

For routine intake, minutes, questions, or single-workstream updates, follow the workspace's established workflow when one applies; do not process the same input twice. Use this procedure for setup, cross-record coordination, and handoffs, or to maintain records when no local workflow covers the request.

## Choose a Mode First

Resolve the customer workspace from the request or active workspace; if ambiguous, confirm the target before writing. Generic workspace files alone do not identify a customer workspace.
Protect existing managed assets such as `.github/copilot-instructions.md`, `.github/skills/`, legacy prompt files, `workspace-summary.md`, `_customer/profile.md`, `_inbox/`, and `workstreams/`.
An aggregate operations workspace may contain a lightweight `Customers/{id}/` profile, task list, inbox, and meetings. Do not initialize a full customer workspace over those records; ask for a separate target if dedicated customer management is needed.

| Mode             | Use when                                      | First action                                                           |
| ---------------- | --------------------------------------------- | ---------------------------------------------------------------------- |
| Setup            | New setup requested, target clear, and no managed structure exists | Create the scaffold and capture routing facts.              |
| Operate          | A managed workspace receives new information  | Update the canonical record for the input.                             |
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

If PowerShell is unavailable, create the same folders, copy each complete `assets/workspace-skills/<name>/` into `.github/skills/<name>/` including bundled resources, and render `assets/copilot-instructions.md` and the required templates with the supplied routing facts. Do not create prompt files.

Automatic selection does not authorize setup. Run the initializer only for a requested setup with a clear target. It stops by default when managed assets exist; use `-Force` only for an explicitly approved replacement of generated skills and templates.
Setup creates four workspace-local operating skills, their resources, and routing instructions; it does not create prompt files.

## Setup Intake

Capture only routing facts: workspace scope, sharing boundary, own-team aliases, key roles, meeting cadence, and primary inputs. Leave detailed technical inventory to later inbox and meeting records.

## Canonical Records

| Need                               | Canonical record                    |
| ---------------------------------- | ----------------------------------- |
| Navigation and handoff             | `README.md`, `workspace-summary.md` |
| Raw updates and open questions     | `_inbox/`, `_questions/`            |
| Customer context                   | `_customer/profile.md`              |
| Meetings and follow-up             | `meeting-notes/`, `next-actions/`   |
| Ongoing scope and detailed history | `workstreams/`, `pj_{topic}/`       |
| Deliverables and reusable learning | `research-reports/`, `_knowledge/`  |

`Initialize-CustomerWorkspace.ps1` creates the managed scaffold and its templates. Create workstream folders, meeting notes, next actions, project threads, and material folders only when the operating workflow requires them.
Leave cross-customer activity reports and global task indexes in the owning operations workspace; link to them when needed instead of copying them into a customer record.

## Research Reports

Use `research-reports/` for generated Markdown deliverables; keep the workspace root for entry files and controls. Detailed placement and sanitization rules are in [Knowledge Ledger Rules](references/knowledge-ledger-rules.md).

## Knowledge Ledger

Use `_knowledge/` only for compact, reusable learnings when the user explicitly requests extraction or generalization. Apply [Knowledge Ledger Rules](references/knowledge-ledger-rules.md) before writing.

## Optional Material Folders

Separate immutable originals, internal edits and shareable copies; use `_received/`, `_working/` and `_provided/` unless the user specifies another destination. Import accessible originals before relying on summaries. Renaming is not anonymization; restricted source content must stay out of recipient files, including hidden slides and notes. Apply [Customer Material Lifecycle](references/material-lifecycle.md) before moving or renaming files.

---

## Operate an Existing Workspace

| Input or request                          | Action                                                                                           |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Short chat, email, or unstructured update | Preserve it in `_inbox/` and classify it.                                                        |
| Meeting memo or Teams AI record           | Create or update one meeting note and extract questions/actions in the same operation.           |
| Clear update for one confirmed workstream | Update its README with the source link and state change.                                         |
| New, ambiguous, or multi-workstream input | Record it in `workstreams/_candidates.md` and ask for confirmation.                              |
| Time-bounded follow-up                    | Track it in `next-actions/`; use `ongoing/` only when no next-meeting date is known.             |
| Status review or handoff                  | Read `workspace-summary.md`, the portfolio, active actions, and open questions before reporting. |

Keep source records authoritative: summaries and workstreams link to meeting notes and inbox entries instead of duplicating them.

## Track Work

- A workstream README owns its current status, owner, actions, and timeline; the portfolio is its index. Create a workstream only after its name and scope are confirmed.
- When a customer follow-up continues an existing question or delivered answer, keep the original exchange visible and append the follow-up chronologically in the owning deliverable or thread. If later evidence resolves an existing `要確認`, append the resolution and evidence to that owning entry instead of creating a parallel source record. For month-bound `_questions` ledgers, append to the current month and reference the original entry instead of rewriting the prior month.
- Put customer-agreed homework, self-initiated proposals, and supplementary research in separate `next-actions/` folders. Task headers link back to their meeting source, while customer-shareable meeting tables exclude local task paths.
- Use only `candidate`, `not-started`, `in-progress`, `blocked`, `done`, or `dropped`. Before assigning `not-started` or `done`, inspect task-linked external work locations; workspace absence does not prove a deliverable is missing. When external progress and artifacts confirm completion, update the canonical action record and indexes in the same operation. Do not copy external artifacts unless the material lifecycle requires it. A `blocked` record names the current owner and its transition condition.
- Create `pj_{topic}/` only when the topic spans multiple meetings and meets the detailed project-thread split conditions.

## Meeting Notes Quality Gate

Before calling meeting notes done:

- Mark uncertain names, times, product names, prices, and support boundaries as `要確認`; record the available transcript range and keep uncorroborated AI follow-ups provisional rather than assigning confirmed owners, deadlines, or deliverables.
- Omit credentials and token-bearing image URLs from saved source text. After saving, ask for a Teams meeting/recap/recording URL if absent; record supplied links without asking again, and distinguish link capture from full-content verification.
- Extract open questions and work needing follow-up into `_questions/{YYYY-MM}.md` and `next-actions/` in the same operation.
- Keep local paths, internal links, internal speculation, and commercial terms out of customer-shareable content.
- Keep one working note. Use `*_internal.md` for a clearly internal meeting, on request, or when an internal section cannot safely contain sensitive material; not merely for unverified details.
- Where sharing is allowed, highlights contain only confirmed items and use one `双方 (両者で調整)` bucket. Keep requested WorkIQ context source-linked and separate from decisions. Apply [Meeting Minutes Rules](references/meeting-minutes-rules.md).

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

`assets/` contains scaffold sources, not live customer records. Generated workspace skills, instructions, and templates may evolve independently; back-port improvements only when explicitly requested.

- `assets/_templates/`: next-actions, knowledge ledger, attachments, and workspace templates
- `assets/workspace-skills/`: four self-contained operating skills, bundled workflows, licenses, and meeting templates
- `assets/copilot-instructions.md`: workspace routing rules and local skill catalog
- `scripts/Test-CustomerWorkspaceSetup.ps1`: isolated scaffold, resource, and existing-record protection checks
- `scripts/Test-ReceivedMaterialPlacement.ps1` - Read-only root audit for unclassified received-material candidates
