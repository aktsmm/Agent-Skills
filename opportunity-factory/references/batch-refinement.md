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
discover/evaluate target set -> review pass 1 -> review pass 2 -> review pass 3 -> fix/guard -> learn
```

Each pass writes one artifact or one structured review row. Fixes happen after a pass identifies a safe `Fix now`, not after all possible opinions are exhausted.

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

- Stop a batch item when all `Fix now` items are closed and remaining issues are `Guard now` or `Block`.
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
