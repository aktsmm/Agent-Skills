# Batch Refinement

Use this when the user asks to refine many items repeatedly, such as `/Refine-Product-100 all`, `all do for this skill`, or "review three times".

## Intake

Capture these before running:

| Field          | Meaning                                                     |
| -------------- | ----------------------------------------------------------- |
| `targetSet`    | `all`, `changed`, `top-N`, folder, file list, product area  |
| `batchSize`    | how many items one worker pass should handle                |
| `passCount`    | usually 3 for rubber-duck review loops                      |
| `stateBackend` | JSON for small/manual work, SQLite for large/resumable work |
| `doneCriteria` | what must be true before an item leaves the batch           |

## Three-Pass Rubber-Duck Loop

Run each item through distinct passes. Do not repeat the same review in different words.

| Pass | Persona            | Main question                                                       | Output                                         |
| ---- | ------------------ | ------------------------------------------------------------------- | ---------------------------------------------- |
| 1    | User/operator      | Can someone use this without hidden context?                        | missing setup, unclear next action, friction   |
| 2    | Runtime/scheduler  | Can this run repeatedly without corrupting state or wasting budget? | idempotency, limits, locks, persistence issues |
| 3    | Next AI maintainer | Can another agent resume, validate, and improve it safely?          | guard gaps, schema drift, unclear contracts    |

## Queue Pattern

Recommended task kinds for batch refinement:

```text
discover/evaluate target set -> review pass 1 -> review pass 2 -> review pass 3 -> repair -> independent re-review -> learn
```

Each pass writes one artifact or one structured review row. A pass with no blocking issue writes `## required fixes` as `none`. A pass with findings assigns stable finding IDs and creates one `repair` child task for a fixed subset. The repair records machine-comparable acceptance checks, then must pass independent re-review before the finding can close. Follow `references/rubber-duck-review.md` for parent iteration accounting, different-family checks, and recovery.

## State Backend Choice

Use JSON when:

- fewer than about 30 items
- one agent or one human runs the loop
- history can be summarized in artifacts

Use SQLite when:

- 100+ items, repeated passes, or long-running scheduled workers are expected
- dedupe, resume, claim locks, or aggregate queries matter
- multiple workers may process tasks over time

See `references/sqlite-state-store.md` for the optional schema.

## Stop Conditions

- Stop a batch item when independent re-review confirms all blocking finding IDs resolved and remaining issues are `Guard now` or `Block`. A repair worker's own claim that fixes are closed is not completion.
- Stop the batch when the next action requires approval, missing credentials, external publishing, or product-specific capability confirmation.
- Stop repeating review passes when two consecutive passes produce no new actionable finding.

## Output Shape

```markdown
## Batch Refinement Summary

- Target set:
- Passes completed:
- Items fixed:
- Items guarded:
- Items blocked:
- State backend:
- Next batch:
```
