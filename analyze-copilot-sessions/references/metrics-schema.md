# Metrics Schema

## Extractor Output

`extract_session_metrics.py` emits one aggregate document with `sessions[]`.
It never emits prompt, response, tool arguments, or source paths.

Each session contains:

| Field               | Meaning                                                             |
| ------------------- | ------------------------------------------------------------------- |
| `session_id`        | Debug session UUID or directory basename                            |
| `primary_model`     | Most frequently called orchestrator model and reasoning effort      |
| `measurement_scope` | Included event boundary; must match for high-confidence comparison  |
| `workload`          | Task class, revision, workflow/rubric version, unit and fingerprint |
| `usage[]`           | Aggregate by agent role, model and reasoning effort                 |
| `timing`            | Observed session and summed active LLM seconds                      |
| `cost`              | AIU total, per-unit value and coverage                              |
| `operations`        | LLM/tool calls and errors                                           |
| `warnings[]`        | Schema damage, duplicate, encoding and missing-field counts         |

`cost.total_aiu` is `null` when any included LLM call lacks
`copilotUsageNanoAiu`. Missing data is not zero usage.

## Analyzer Output

`analyze_session_metrics.py` accepts one or more normalized runs.

- One run: `analysis_mode` is `single-session`; `sessions[]` contains the model,
  workload, usage roles, cost/time/error metrics, data quality, and quality
  evidence. `comparison` is `null`.
- Two or more runs: `analysis_mode` is `multi-session-comparison`; the same
  session summaries are returned with `comparison` containing confidence,
  winners, Pareto frontier, grouped statistics, outliers, and optional weights.

## Existing Metrics Adapter

The analyzer also accepts a single-run metrics object with these fields:

- `primary_model.model`, `primary_model.reasoning_effort`
- `question_count` or `workload.unit_count`
- `timing.review_elapsed_seconds`, `session_observed_seconds`, or `active_llm_seconds`
- `cost.total_aiu`, `total_nano_aiu`, `aiu_per_question`, or `aiu_per_unit`
- `operations.llm_calls`, `llm_errors`, `tool_calls`, `tool_errors`

Detailed Review run-metrics schema v1 is accepted through this adapter. The
Skill does not import or modify its collector.

## Workload Fingerprint

The extractor hashes the following normalized fields:

- `task_kind`
- `revision`
- `workflow_version`
- `rubric_version`
- `unit_name`
- `unit_count`
- `measurement_scope`

Use a stable content hash or commit/revision identifier when available. Do not
put customer data, prompt text, or an absolute path in fingerprint fields.

## Time Fields

- `session_observed_seconds`: first orchestrator LLM request to last observed orchestrator response.
- `active_llm_seconds`: sum of included LLM request durations; parallel calls can make it exceed wall time.
- `review_elapsed_seconds`: external workflow start to completion when provided by an existing metrics artifact.

The analyzer prefers external workflow elapsed time, then observed time, then
active LLM time for the elapsed winner. It reports active LLM separately.

Timestamp cutoffs cannot remove an event whose operation started before the
cutoff but was appended to the log afterward. For reproducibility, treat AIU,
LLM calls, and LLM duration as the primary boundary checks; report small tool
call differences as cutoff-boundary drift.

## Live Session Snapshots

An active debug session directory is mutable. Log compaction or replacement can
remove earlier events, so later extractions can report fewer calls, lower AIU,
or a shorter `session_observed_seconds` without reversing prior usage.

- Persist timestamped metrics snapshots outside the debug directory when
  monitoring a long-running session.
- For a conservative cumulative lower bound, group `usage[]` by
  `(role, model, reasoning_effort)`, take each bucket's maximum `nano_aiu`
  across snapshots, then sum those maxima.
- Do not add every positive bucket delta to a previous total. A compacted bucket
  can rise while remaining below its earlier maximum, which would double count
  retained usage.
- If any call lacks `copilotUsageNanoAiu`, state the missing-call count and
  describe the result as a lower bound. The extractor cannot reconstruct usage
  removed before the first saved snapshot.

For wall time, prefer explicit workflow timestamps or session-store
`created_at`/`updated_at`. Use the latest log modification time only as evidence
of recent activity.

`total_aiu` is local telemetry derived from `copilotUsageNanoAiu / 1e9`, not an
authoritative billing ledger. It may reproduce GitHub AI Credits under current
model and cache pricing, but any conversion must be dated, validated for every
observed pricing category, and labeled as an estimate. Use the GitHub billing
usage report for the authoritative credit total.
