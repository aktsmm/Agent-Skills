# Output Format

Lead with Findings. If there are no confirmed findings, state that clearly first.

## Findings

| #   | Severity | Confidence | Target | Structural Signal | Reachability | Impact | Defensive Verification | Minimal Fix |
| --- | -------- | ---------- | ------ | ----------------- | ------------ | ------ | ---------------------- | ----------- |

## Structure Map Summary

| Item      | Value                                                                |
| --------- | -------------------------------------------------------------------- |
| Source    | existing artifact / newly generated / quick extraction / unavailable |
| Artifact  | saved path, or none                                                  |
| Scope     | reviewed paths and boundaries                                        |
| Method    | tools, scripts, or manual extraction used                            |
| Limits    | unparsed or approximate areas                                        |
| Redaction | redacted secret values, or none applicable                           |

## Hypotheses

| #   | Hypothesis | Missing Evidence | Next Check |
| --- | ---------- | ---------------- | ---------- |

## Code to Inspect

| Priority | Path / Symbol | Why |
| -------- | ------------- | --- |

## Recommended Fix Plan

1. Fix clear, reachable, high-impact issues first.
2. Add safety guards such as size limits, timeouts, input validation, path normalization, auth checks, and log redaction.
3. Split high-complexity code only where it reduces risk or enables tests.
4. Verify the Source -> Sink path is blocked or constrained after the fix.

## Verification Summary

- Checks run: command/tool/read-only review performed, or not run with reason
- Remaining risk: unresolved items, or none
- External references: URLs used, or none
