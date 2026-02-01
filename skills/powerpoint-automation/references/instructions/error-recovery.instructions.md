# Error Recovery Strategy

**This file is the SSOT (Single Source of Truth) for error recovery rules.**

---

## Retry Policy

| Item           | Value                                       |
| -------------- | ------------------------------------------- |
| Max retries    | **3 times**                                 |
| Retry target   | Failures within same phase                  |
| Retry interval | Immediate (no human intervention)           |
| Retry unit     | Per phase (EXTRACT, TRANSLATE, BUILD, etc.) |

---

## Fallback Matrix

| Phase          | Failure Type         | Fallback To      | Action                           |
| -------------- | -------------------- | ---------------- | -------------------------------- |
| REVIEW(JSON)   | Schema violation     | EXTRACT          | Re-run `reconstruct_analyzer.py` |
| REVIEW(JSON)   | Empty slides         | EXTRACT          | Fix content.json                 |
| REVIEW(JSON)   | Image path missing   | EXTRACT          | Re-run `extract_images.py`       |
| REVIEW(JSON)   | Translation error    | TRANSLATE        | Re-run Localizer                 |
| REVIEW(PPTX)   | Slide count mismatch | BUILD            | Re-run `create_from_template.py` |
| REVIEW(PPTX)   | Layout issues        | PREPARE_TEMPLATE | Re-diagnose template             |
| BUILD          | Template load error  | PREPARE_TEMPLATE | Run `diagnose_template.py`       |
| **3 failures** | Any                  | **ESCALATE**     | Wait for human intervention      |

---

## Escalation Conditions

Move to **ESCALATE** phase and wait for human intervention when:

1. **3 consecutive failures in same phase**
2. **Unresolvable errors**
   - API rate limits
   - File corruption
   - Permission errors
3. **AI determines fix is difficult**
   - Structural problems
   - Source data quality issues

---

## Escalation Output

```json
{
  "status": "escalated",
  "phase": "REVIEW_JSON",
  "base_name": "20251214_example_report",
  "failure_count": 3,
  "failures": [
    { "attempt": 1, "error": "Empty slide at index 5", "timestamp": "..." },
    { "attempt": 2, "error": "Empty slide at index 5", "timestamp": "..." },
    { "attempt": 3, "error": "Empty slide at index 5", "timestamp": "..." }
  ],
  "reason": "Empty slides detected in slides[5], [8], [12]",
  "suggested_action": "Manual review of content.json required",
  "files": {
    "content": "output_manifest/xxx_content_ja.json",
    "trace": "output_manifest/xxx_trace.jsonl"
  },
  "escalated_at": "2025-12-14T10:30:00+09:00"
}
```

---

## Workflow Resume

```powershell
# After escalation, resume after manual fix
python scripts/resume_workflow.py 20251214_example_report --from REVIEW_JSON

# Force resume from specific phase (reset retry count)
python scripts/resume_workflow.py 20251214_example_report --from EXTRACT --reset-retry
```

---

## Review Pass/Fail Criteria

| Verdict | Condition             | Action                 |
| ------- | --------------------- | ---------------------- |
| ✅ PASS | 0 errors, 0 warnings  | Proceed to next phase  |
| ⚠️ WARN | 0 errors, 1+ warnings | User confirm, continue |
| ❌ FAIL | 1+ errors             | Send back (max 3×)     |
