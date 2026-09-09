# Deterministic Daily Activity Collection

Collect local evidence before an agent drafts a daily report. The collector is read-only and must not copy external files, mutate Git, or infer that every changed file was edited by the user.

## Contract

1. Store roots in `_datasources/daily-activity-sources.json`.
2. Use a half-open local-time window: target date `00:00:00` inclusive to next date `00:00:00` exclusive.
3. Recursively enumerate changed files and hidden or nested Git repositories, excluding dependency and generated directories.
4. Sort canonical paths and commit records before writing JSON.
5. Write `_reports/{YYYY-MM}/daily-ops/{YYYY-MM-DD}.json` atomically, including a complete summary when every count is zero.
6. Treat missing optional roots as `unavailable`; never reinterpret collection failure as zero activity.

## Adding A Root

Run `collect_daily_activity.py --explain-path <path>` first. If an existing parent root covers the requested path and collection kinds, do not add the child. Add a child only when it needs a kind or policy not provided by its parent.

Activity collection and customer synchronization are separate. The collector may identify candidates, but customer sync still requires its own dry run and mapping checks.

Daily evidence uses an explicit date and never advances sync state. If customer synchronization uses cursors, keep one cursor per canonical source root; a shared cursor can mark another root's unprocessed changes as seen.

## Acceptance

- Replaying the same stable date produces equivalent JSON after removing `collectedAt`.
- A file at the start boundary is included; a file at the end boundary is excluded.
- Hidden directories and nested repositories are found exactly once.
- Missing required roots fail the run; missing optional roots remain visible as unavailable.
- The collector does not alter source roots, repository state, or customer folders.
