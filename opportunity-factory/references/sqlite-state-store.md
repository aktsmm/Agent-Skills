# SQLite State Store

SQLite is an optional state backend for large, repeated, or scheduled Opportunity Factory runs. JSON remains the default for small/manual work.

## Use SQLite When

- The factory tracks 100+ items or candidates.
- Rubber-duck review runs multiple passes per item.
- Multiple scheduled workers need claim/retry behavior.
- Resume, dedupe, aggregate reporting, or historical audit queries matter.

## Avoid SQLite When

- A user is doing a small supervised run.
- The platform cannot persist local database files safely.
- Repository policy forbids generated binary state files.
- A hosted platform already provides durable state, locks, and queryable logs.

## Schema

Use `assets/templates/factory-state.sqlite.sql` as the minimal schema. It models:

- `runs`: top-level factory executions
- `items`: opportunities or products being refined
- `tasks`: queue entries
- `claims`: worker locks and retries
- `reviews`: pass-indexed rubber-duck findings
- `critic_log`: durable repair/re-review receipt, finding resolution, validation result, and independence evidence
- `repair_attempts`: parent-task reservation and finalization for bounded repair/re-review accounting
- `artifacts`: durable outputs
- `outcomes`: observed/estimated/assumed metrics
- `pipeline_log`: append-only audit events

## Initialize

Use `scripts/init_factory_sqlite.py` when a selected state store should be a SQLite database.

```text
python scripts/init_factory_sqlite.py --db-path <state-dir>/factory-state.sqlite --domain <domain> --audience <audience> --apply
```

Omit `--apply` for dry-run. Existing databases are not overwritten unless `--force` is provided.

## Rules

- Keep worker writes artifact-first when possible; let commander/reducer import rows.
- Use one writer or transactional writes for state mutation.
- Store `repair` child tasks with `parent_task_id`, finding IDs, input hash, and acceptance checks. Commander inserts `repair_attempts.status=reserved` before dispatch, then finalizes the same row as validation pass/fail or `repair-start-failed`; use it to compute the parent task's remaining repair budget. Store validation and re-review receipts in `critic_log`, including repair task ID, role/layer, immutable adapter receipt source/reference/hash, and constrained independence/next-state values; do not treat a worker's repair output as completion before the independent receipt exists.
- Keep secrets and personal data out of the database.
- Do not commit SQLite database files unless repository policy explicitly allows it.
- Prefer SQL schema in the skill; create actual `.sqlite` files only in the user's selected state store.

## Smoke Test

The validator should execute the schema with Python stdlib `sqlite3` against an in-memory database. This proves the schema parses without creating a persistent database.
