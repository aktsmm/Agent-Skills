# Knowledge Ledger

This folder stores reusable, generalized learnings extracted from meetings, incidents, and research when explicitly requested.

## Use This For

- Short patterns, gotchas, decision criteria, and validation checklists.
- Learnings that can help future work in the same customer workspace.
- Pointers to longer reports in `research-reports/`.

## Do Not Use This For

- Raw meeting logs or pasted chat. Use `_inbox/`.
- Open questions or homework. Use `_questions/` and `next-actions/`.
- Long research notes or detailed design reports. Use `research-reports/`.
- Customer names, person names, ticket IDs, local absolute paths, secrets, or unpublished/confidential specifics.

## Starting Structure

- `general.md`: default ledger for early entries.

Create category files only when `general.md` becomes hard to scan. Prefer broad names such as `operations.md`, `architecture.md`, `engagement.md`, or `product-notes.md`; avoid project-specific labels.

## Entry Shape

```markdown
## YYYY-MM-DD Short Title

- tags: #example #topic
- source: meeting-notes/YYYY-MM-DD_topic.md
- confidence: meeting-derived / verified / deprecated
- official confirmation: required / done / not-applicable

### Learning

One concise reusable lesson.

### Evidence

Where it came from and why it mattered.

### Applies When

When to reuse this lesson.

### Caveats

Limits, checks, or confirmation needed.
```
