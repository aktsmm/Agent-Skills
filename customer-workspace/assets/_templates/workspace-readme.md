# {{CUSTOMER_NAME}} Workspace

## Start Here

- Read `workspace-summary.md` for the current handoff snapshot.
- Update `_customer/profile.md` when core customer information changes.
- Add raw notes to `_inbox/{{YEAR_MONTH}}.md` and extract actions into `_questions/{{YEAR_MONTH}}.md`.

## Workspace Guide

- `README.md`: this overview and entry point
- `workspace-summary.md`: handoff-ready summary and source-of-truth map
- `.github/prompts/`: prompts for inbox, meeting notes, and question extraction
- `_templates/`: reusable document templates
- `_knowledge/`: opt-in ledger for reusable generic learnings, patterns, and gotchas
- `research-reports/`: generated research notes, comparison memos, report drafts, and demo specification notes
- Optional material folders: `_received/`, `_working/`, `_provided/` for customer originals, internal edits, and customer-facing copies

## First Checks

- Confirm workspace purpose and scope: customer-wide, project-specific, proposal, PoC, or ongoing support.
- Confirm sharing boundary: customer-shareable, internal-only, or mixed.
- Confirm current engagement or support type, contacts, and priorities.
- Fill own-team names and aliases in `_customer/profile.md` before converting action-heavy meeting notes.
- Confirm meeting cadence and next date if `next-actions/` will be used.
- Confirm primary information sources: meetings, chat, email, shared files, received materials, or service portals.
- Use `_knowledge/` only for compact reusable learnings; keep raw notes in `_inbox/` and long analyses in `research-reports/`.
- Confirm where active working files live versus reference-only materials.
- Keep generated research/report Markdown in `research-reports/` instead of the workspace root.
- If customer-shared files are part of the work, keep lifecycle split first (`_received/` / `_working/` / `_provided/`) and then choose `overall-architecture/` or `mtg-YYYY-MM-DD-name/` as the second axis.
- Record any immediate open actions in the current month question log.
