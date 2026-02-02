# Script Dependencies

**This file is the SSOT (Single Source of Truth) for script dependencies.**

---

## Dependency Graph

```
classify_input.py
    ↓
reconstruct_analyzer.py ←──────────────────────────────┐
    ↓                                                  │
extract_images.py (parallel OK)                        │
    ↓                                                  │
[Localizer Agent] ───→ content_ja.json                 │
    ↓                                                  │
validate_content.py                                    │
    ↓                                                  │
create_from_template.py ←── analyze_template.py        │
    ↓                       └── diagnose_template.py   │
validate_pptx.py               └── clean_template.py   │
    ↓                                                  │
review_pptx.py                                         │
                                                       │
summarize_content.py ──────────────────────────────────┘
```

---

## Script Categories

### Input Processing

| Script                    | Input       | Output              | Dependencies              |
| ------------------------- | ----------- | ------------------- | ------------------------- |
| `classify_input.py`       | File/URL    | classification.json | None                      |
| `extract_images.py`       | PPTX or URL | images/{base}/      | None                      |
| `reconstruct_analyzer.py` | PPTX        | content.json        | extract_images (optional) |

### Template Processing

| Script                     | Input         | Output              | Dependencies           |
| -------------------------- | ------------- | ------------------- | ---------------------- |
| `analyze_template.py`      | Template PPTX | layouts.json        | None                   |
| `diagnose_template.py`     | Template PPTX | Diagnosis report    | None                   |
| `clean_template.py`        | Template PPTX | Cleaned PPTX        | diagnose (recommended) |
| `create_clean_template.py` | Source PPTX   | Clean template PPTX | None                   |

### Validation

| Script                | Input               | Output             | Dependencies |
| --------------------- | ------------------- | ------------------ | ------------ |
| `validate_content.py` | content.json        | Exit code (0/1/2)  | None         |
| `validate_pptx.py`    | PPTX + content.json | Exit code + report | content.json |
| `review_pptx.py`      | PPTX                | Content extraction | None         |

### Generation

| Script                    | Input                   | Output       | Dependencies     |
| ------------------------- | ----------------------- | ------------ | ---------------- |
| `create_from_template.py` | Template + content.json | PPTX         | analyze_template |
| `create_ja_pptx.py`       | content.json            | PPTX         | None             |
| `create_pptx.js`          | Diagram config          | Diagram PPTX | npm packages     |

### Utility

| Script                     | Input                   | Output               | Dependencies |
| -------------------------- | ----------------------- | -------------------- | ------------ |
| `merge_slides.py`          | Template + Diagram PPTX | Merged PPTX          | None         |
| `insert_diagram_slides.py` | PPTX + Diagram + config | Merged PPTX          | None         |
| `summarize_content.py`     | content.json            | content_summary.json | None         |
| `resume_workflow.py`       | State file              | Resumed workflow     | None         |
| `workflow_tracer.py`       | -                       | Trace log            | None         |

---

## Parallel Execution

Scripts that can run in parallel:

```powershell
# These can run simultaneously
Start-Job { python scripts/extract_images.py $input images/$base }
Start-Job { python scripts/analyze_template.py $template }

# Wait for both
Get-Job | Wait-Job
```

Use `extract_parallel.ps1` for automated parallel execution.

---

## Required Packages

### Python (requirements.txt)

```
python-pptx>=0.6.21
Pillow>=9.0.0
jsonschema>=4.0.0
requests>=2.28.0
```

### Node.js (package.json)

```json
{
  "dependencies": {
    "pptxgenjs": "^3.12.0"
  }
}
```

---

## Exit Codes

| Script                    | 0       | 1     | 2            |
| ------------------------- | ------- | ----- | ------------ |
| `validate_content.py`     | PASS    | FAIL  | WARN         |
| `validate_pptx.py`        | PASS    | FAIL  | WARN         |
| `create_from_template.py` | Success | Error | Empty slides |

---

## Python Environment Troubleshooting

### Problem: `pip install` fails

Errors like:
- `ModuleNotFoundError: No module named 'xxx'`
- `error: externally managed`
- `Failed to inspect Python interpreter from virtual environment`

### Solution: Use uv venv

```powershell
# 1. Remove broken .venv
Remove-Item ".venv" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Create new venv with uv
uv venv .venv

# 3. Activate
.\.venv\Scripts\Activate.ps1

# 4. Install packages
uv pip install python-pptx Pillow jsonschema requests
```

### Why uv?

- `pip install --system` fails with uv-managed Python
- `py -3.12` launcher may not be available
- `uv venv + uv pip` is the most reliable combination

### Problem: `BadZipFile` error

Template files (.pptx) may be Git LFS pointers, not actual files.

```powershell
# Pull LFS files
git lfs pull

# Verify file is valid (should show PK header, not "version https://git-lfs")
Get-Content "assets/template.pptx" -TotalCount 1
```

### Script Execution

Always specify venv Python explicitly:

```powershell
& "d:\project\.venv\Scripts\python.exe" create_from_template.py template.pptx content.json output.pptx
```

### Package Installation Priority

1. **VS Code tool `install_python_packages`** - Try first
2. **uv venv + uv pip** - Most reliable
3. **pip install** - Last resort (environment-dependent)

