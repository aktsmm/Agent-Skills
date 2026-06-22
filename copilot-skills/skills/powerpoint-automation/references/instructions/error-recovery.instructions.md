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
| BUILD          | Slide paste fails (all) | BUILD         | Switch to `Slides.InsertFromFile` (clipboard-independent) |
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

---

## Template Corruption Recovery

### Symptoms

- `BadZipFile: Bad magic number for central directory`
- `zipfile.BadZipFile: File is not a zip file`
- PPTX header is not `PK` (hex: `50-4B`)
- PPTX header is `D0-CF-11-E0` even though the extension is `.pptx` (legacy/OLE body)
- PowerPoint opens the file but python-pptx reports `PackageNotFoundError`
- PowerPoint shows a coauthoring/競合の解決 dialog after automation

### Diagnosis

```powershell
# Check file header (should show 80-75 = PK)
[System.IO.File]::ReadAllBytes("template.pptx")[0..3] -join '-'
```

### Causes

| Cause            | Description                 |
| ---------------- | --------------------------- |
| OneDrive sync    | File incomplete during sync |
| Git autocrlf     | Binary treated as text      |
| Partial download | Network interruption        |
| COM save mode    | PowerPoint saved a `.pptx` path as legacy/OLE body |
| Open read-only deck | Read-only review still held a OneDrive/PowerPoint lock |

### Recovery: Normalize Before Package Edits

For OneDrive or template-master work, verify and normalize the file before using python-pptx or ZIP-level edits.

```python
from pathlib import Path
from zipfile import is_zipfile

p = Path("template.pptx")
if not is_zipfile(p):
    raise RuntimeError("Not an OpenXML PPTX package; normalize with PowerPoint SaveAs(..., 24) or restore a known-good copy first.")
```

Rules:

- Keep a known-good OpenXML copy before iterative COM work.
- After any PowerPoint open/save/review cycle, re-check `is_zipfile(path)`; COM/OneDrive can change the file body back to legacy/OLE.
- If the file is open in PowerPoint, close the matching presentation by basename before rename/move/delete. A read-only window can still block filesystem operations.
- If a conflict dialog appears, resolve/close it first. Do not continue automation against a deck in a modal dialog state.
- Prefer local temp copies for destructive template rewrites; replace the OneDrive file only after the temp copy opens and validates.
- If validation passes before user review but fails afterward, assume the review/open cycle changed the file state; restore from the last validated temp artifact before attempting more package edits.

### Recovery: Use Your Own Template

If bundled template is corrupted, use any PPTX as template:

```powershell
# Analyze user's PPTX → auto-generates layouts.json
python scripts/analyze_template.py "user_presentation.pptx"

# Use as template
python scripts/create_from_template.py "user_presentation.pptx" `
    "output_manifest/content.json" "output_ppt/result.pptx" `
    --config "output_manifest/user_presentation_layouts.json"
```

### Recovery: Scratch Build (no template at all)

When no usable template exists (corrupted bundled template, ad-hoc LT deck, simple
slides), build directly with `python-pptx` using the blank layout:

```python
from pptx import Presentation
from pptx.util import Inches
prs = Presentation()
prs.slide_width = Inches(13.33)   # 16:9
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[6])  # 6 = blank
# Build everything with add_textbox / add_shape
```

Use this only when template-based generation is infeasible. Output is not bound
to layout XML, so master/layout consistency must be enforced in code.

## PPTX File Lock During Rebuild

When iterating on a deck the user is reviewing in PowerPoint, `python-pptx.save()`
fails with `PermissionError`. Close only the target presentation, then rebuild:

```python
import win32com.client as w
app = w.GetActiveObject("PowerPoint.Application")
for p in list(app.Presentations):
    if "target-deck-name" in p.Name:
        p.Close()
# Now python-pptx can save
```

Do not call `app.Quit()`; leave PowerPoint running so the user can reopen the
rebuilt file with `Start-Process`.

## COM Slide Insertion: Prefer InsertFromFile

`Slide.Copy()` + `Slides.Paste()` relies on the system clipboard and can fail for
**every** slide where the clipboard is blocked (e.g. Global Secure Access).
Symptoms: each insert retries then skips, leaving a template-only deck.

- Default to `Slides.InsertFromFile(path, index, start, end)` — clipboard-independent.
  Insert happens *after* `index`, so pass `insertPos - 1`.
- Read the source from a **local temp copy** (`[IO.File]::ReadAllBytes` then write to
  `$env:TEMP`), not the COM-opened presentation. Avoids OneDrive hydration stalls and
  file-lock contention in one step.
- Never `Stop-Process POWERPNT` while a build is running. Killing a live COM instance
  makes the in-flight automation fail with RPC error `0x800706BE`.

> 📖 **Full template requirements:** See [template.instructions.md](template.instructions.md) > Template Preparation
