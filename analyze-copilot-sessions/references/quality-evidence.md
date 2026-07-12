# Quality Evidence

Logs measure activity, not correctness. Bind quality through an analysis
manifest and external persisted artifacts.

## Levels

| Level            | Requirement                                                      | Interpretation                |
| ---------------- | ---------------------------------------------------------------- | ----------------------------- |
| `VERIFIED`       | Independent evaluation artifact plus declared gate paths         | Strongest available evidence  |
| `GATE_SUPPORTED` | Persisted test, validator, completion, or final-gate artifacts   | Workflow quality passed       |
| `PROXY_ONLY`     | Explicit proxy such as manual acceptance, without persisted gate | Not an accuracy claim         |
| `UNMEASURED`     | No external evidence                                             | Excluded from quality ranking |

`VERIFIED` requires at least one gate path. A missing, unknown, or failed gate
does not pass. Fix counts and low error rates are context only.

## Analysis Manifest

Paths are relative to the manifest location unless absolute paths are supplied.
Prefer relative paths for portability.

```json
{
  "schema_version": 1,
  "runs": [
    {
      "label": "model-a-high",
      "metrics_path": "metrics/model-a.json",
      "workload": {
        "task_kind": "detailed-review",
        "unit_name": "question",
        "unit_count": 30,
        "revision": "content-sha256",
        "workflow_version": "v2",
        "rubric_version": "2026-07"
      },
      "quality_evidence": {
        "level": "GATE_SUPPORTED",
        "gate_paths": ["evidence/completion.json", "evidence/validator.json"],
        "adjudicated_residual_defects": 0,
        "notes": ["All declared final gates passed."]
      }
    }
  ]
}
```

## Gate Status

The adapter recognizes top-level `final_verdict`, `verdict`, `status`, or
`overall_status`, and nested `result`. Only explicit `PASS` or `FAIL` is
decisive. Unknown status is counted as a failed/unknown gate.

## Detailed Review Adapter

For a formal review, bind the run metrics to current completion and validator
artifacts. Evidence validation can be an additional gate. Use the reviewed
question count as `unit_count`; never infer correctness from the number of fixes.

When comparing a rerun to an older run, use the same content revision if the
goal is a model A/B. If the CSV or rubric changed, preserve the distinct revision
and allow comparability to fall to MEDIUM or LOW.
