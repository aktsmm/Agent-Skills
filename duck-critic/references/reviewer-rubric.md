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

## Evidence Rules

- Tie findings to the goal, acceptance criteria, or concrete evidence.
- If files were inspected, include file paths.
- If files were not inspected, do not invent file references.
- If the critic is uncertain, state what evidence would resolve the uncertainty.

## Reconciliation Rules

- Merge duplicate findings across reviewer lanes.
- Keep the most severe valid classification.
- Downgrade or reject findings that are style-only.
- Do not let fallback critics override frozen user requirements without explaining the tradeoff.
