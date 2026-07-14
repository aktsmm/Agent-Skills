# Reviewer Rubric

The critic should report only issues that matter to the requested outcome.

## Severity

### Blocking

Use `Blocking` when the issue is likely to prevent success or create unacceptable risk.

Examples:

- Requested behavior will not work.
- A security or privacy boundary is violated.
- Data loss, data corruption, or incorrect permissions are plausible.
- Runtime/deployment success is assumed from build success alone.
- Tests cannot prove the acceptance criteria.
- The plan depends on an unverified external constraint that changes the finish line.

### Non-blocking

Use `Non-blocking` when the issue should be fixed for quality or robustness but does not currently block the requested outcome.

Examples:

- Edge case is missing but outside the core happy path.
- Error handling is weak but not catastrophic.
- Verification is thin but has a workable primary check.
- The design is maintainable now but may become costly later.

### Suggestion

Use `Suggestion` for lower-priority improvements with real impact.

Examples:

- A small simplification would reduce future confusion.
- A focused test would improve confidence.
- A clearer adapter boundary would make cross-harness use easier.

### Ignore

Ignore these unless they affect the outcome:

- Pure formatting preferences.
- Naming taste.
- Comment grammar.
- Generic best practices without task-specific impact.
- Refactors that do not reduce meaningful risk.
- Pre-existing issues unrelated to the current task. Surfacing them distracts the producer and causes scope creep. Only raise them if the current change is built on top of them or makes them materially worse.

## Evidence Rules

- Tie findings to the goal, acceptance criteria, or concrete evidence.
- If files were inspected, include file paths.
- If files were not inspected, do not invent file references.
- If the critic is uncertain, state what evidence would resolve the uncertainty.
- Only report findings the critic is confident are real issues. Speculative "might be a problem" notes without concrete evidence should be omitted or downgraded to a Suggestion that names the open question.
- Treat an explicit user statement about an action they performed as user-provided evidence and label that provenance; do not reject it only because the current harness log omits the action.
- A search miss proves only that evidence was not found in the searched scope. Report that scope and check referenced workspaces, private artifacts, or user-provided evidence before classifying a claim as contradicted or nonexistent.
- For multiple trials or collectors, preserve the run, method, unit, and marked symptom window; do not present cross-run values as one continuous experiment or as directly comparable metrics.
- Require a candidate cause to align with symptom onset and duration. A later or isolated spike cannot explain an earlier, sustained failure without additional evidence.
- Treat collection overhead as a confounder. Require a smoke test, baseline, or equivalent evidence before trusting measurements from a new collector.

## Output Discipline

- Return per-issue findings only. Do not include an overall go/no-go recommendation, an action plan, or instructions on what the producer should do next — that decision belongs to the producer.
- If no blocking issues are found, say so explicitly (e.g. `PASS — no blocking issues`). Do not manufacture nits to look thorough; a clean PASS in zero or one round is a valid outcome.

## Reconciliation Rules

- Merge duplicate findings across reviewer lanes.
- Keep the most severe valid classification.
- Downgrade or reject findings that are style-only.
- Do not let fallback critics override frozen user requirements without explaining the tradeoff.
