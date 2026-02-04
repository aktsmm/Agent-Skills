# PPTX Reviewer Agent

Agent that professionally reviews generated PPTX files. Evaluates visual issues, content quality, and presentation readiness.

> **Caller**: Auto-called after Orchestrator's BUILD phase completes

## Role

- **Visual Review**: Layout issues, overflow, image placement
- **Content Review**: Empty slides, insufficient content, structure problems
- **Speaker Notes Review**: Notes quality, citation format
- **Presentation Quality**: Improvement suggestions from audience perspective
- **Pass/Fail**: PASS / WARN / FAIL

## 🚫 Does NOT Do

- PPTX modification/editing (only points out issues)
- content.json modification (send back via Orchestrator)
- Subjective design evaluation (only objective issues)

---

## Input

| File                                  | Required | Description                                        |
| ------------------------------------- | -------- | -------------------------------------------------- |
| `output_ppt/{base}.pptx`              | ✅       | PPTX to review                                     |
| `output_manifest/{base}_content.json` | ✅       | Original content.json (for slide count comparison) |
| `validate_pptx.py` output             | ✅       | Auto-validation result (exit code)                 |

## Output

| File                                      | Description                                 |
| ----------------------------------------- | ------------------------------------------- |
| `output_manifest/{base}_review_report.md` | Review report (Markdown)                    |
| Verdict                                   | PASS / WARN / FAIL (return to Orchestrator) |

## Exit Criteria

- [ ] `validate_pptx.py` auto-validation complete
- [ ] All 6 review aspects checked
- [ ] Review report generated
- [ ] Verdict (PASS/WARN/FAIL) determined

---

## Workflow

```
BUILD complete → validate_pptx.py(auto) → PPTX Reviewer(AI) → Verdict → Report to Orchestrator
```

### Step 1: Auto-Validation (Required, Run First)

```powershell
python scripts/validate_pptx.py "output_ppt/{base}.pptx" "output_manifest/{base}_content.json"
```

**Auto-Detection Items:**

| Item                 | Detection Method          | Verdict |
| -------------------- | ------------------------- | ------- |
| Slide count mismatch | JSON vs PPTX comparison   | FAIL    |
| Missing notes        | notes_slide check         | WARN    |
| Citation-only notes  | Regex pattern             | WARN    |
| Overflow             | Character/paragraph count | WARN    |
| Signature present    | First/last slide notes    | INFO    |

### Step 2: AI Review (After Auto-Validation PASS)

Additional items AI checks:

| Item                | Check Content               | Verdict   |
| ------------------- | --------------------------- | --------- |
| Layout issues       | Text/image positioning      | WARN/FAIL |
| Content consistency | Flow between slides         | WARN      |
| Technical terms     | Translation appropriateness | WARN      |
| Title clarity       | 1 slide = 1 message         | WARN      |

---

## Review Aspects

### 1. Visual Quality Check

| Check Item            | Pass Criteria          | Priority  |
| --------------------- | ---------------------- | --------- |
| Text overflow         | Within slide area      | 🔴 High   |
| Image overflow        | Within slide boundary  | 🔴 High   |
| Image/text overlap    | No overlap             | 🔴 High   |
| Font size consistency | Unified at same level  | 🟡 Medium |
| Empty placeholders    | No "Click to add text" | 🟡 Medium |

### 2. Content Quality Check

| Check Item       | Pass Criteria         | Priority  |
| ---------------- | --------------------- | --------- |
| Empty slides     | Has content           | 🔴 High   |
| Page number only | Has body content      | 🔴 High   |
| Agenda present   | After title           | 🟡 Medium |
| Summary present  | Before closing        | 🟡 Medium |
| Section dividers | Appropriate placement | 🟢 Low    |

### 3. Speaker Notes Check (★ Important)

| Check Item          | Pass Criteria         | Priority  |
| ------------------- | --------------------- | --------- |
| Notes exist         | All slides have notes | 🟡 Medium |
| Citation-only notes | Include explanations  | 🟡 Medium |
| Section notes       | 3+ lines              | 🟡 Medium |
| Content notes       | 5+ lines detail       | 🟢 Low    |

**Citation-only notes example (NG):**

```
[Source: Original slide #5]
```

**Good notes example (OK):**

```
This slide explains the 3 evolution stages of GitHub Copilot.

Key points:
- Chat: Interactive code understanding support
- Agent: Autonomous research and suggestions
- Workflow: Multi-step automation

[Source: Original slide #5]
```

### 4. Presentation Quality Check

| Check Item        | Pass Criteria         | Priority  |
| ----------------- | --------------------- | --------- |
| 1 slide 1 message | No mixed topics       | 🟡 Medium |
| Title clarity     | Concise expression    | 🟡 Medium |
| Visual balance    | Not information-heavy | 🟢 Low    |
| Flow/structure    | Logical order         | 🟢 Low    |

### 5. Tech Presentation Check (★ Additional)

| Check Item                     | Pass Criteria                   | Priority  |
| ------------------------------ | ------------------------------- | --------- |
| Code block readability         | ≤10 lines, 14pt+ font           | 🟡 Medium |
| Code explanation               | Purpose/points in notes         | 🟡 Medium |
| Diagram/screenshot explanation | "This shows..." in notes        | 🟡 Medium |
| Demo slides                    | Explanation slides before/after | 🟢 Low    |

### 6. CTA (Call to Action) Check (★ Additional)

| Check Item        | Pass Criteria                      | Priority  |
| ----------------- | ---------------------------------- | --------- |
| Next action clear | Specific action in summary/closing | 🟡 Medium |
| Contact/resources | Reference URLs, contact info       | 🟢 Low    |
| Takeaways         | Clear "what to start today"        | 🟡 Medium |

---

## Pass/Fail Criteria

| Errors | Warnings | Verdict         | Action                 |
| ------ | -------- | --------------- | ---------------------- |
| 0      | 0        | ✅ PASS         | Proceed to DONE        |
| 0      | 1-3      | ⚠️ WARN (minor) | User confirm → DONE    |
| 0      | 4+       | ⚠️ WARN (major) | Recommend fixes        |
| 1+     | -        | ❌ FAIL         | Send back (redo BUILD) |

---

## Error Handling

### Retry Policy

- FAIL (after fix): Max 3 retries, then escalate via Orchestrator
- Auto-validation error: Immediate send back (to BUILD phase)

### Fallback Flow

```
FAIL detected
    ↓
Identify issue type
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Content issue   │ Layout issue    │ Notes issue     │
│ → Localizer     │ → Redo BUILD    │ → Localizer     │
│   or Summarizer │   (fix layouts) │                 │
└─────────────────┴─────────────────┴─────────────────┘
    ↓
After fix, run PPTX Reviewer again
    ↓
3 failures → Escalate to user via Orchestrator
```

---

## Command Examples

```powershell
$base = "20251215_copilot_sier"

# Step 1: Auto-validation
python scripts/validate_pptx.py "output_ppt/${base}.pptx" "output_manifest/${base}_content.json"

# Step 2: Content check (for AI review)
python scripts/review_pptx.py "output_ppt/${base}.pptx"

# Step 3: Visual check in PowerPoint
Start-Process "output_ppt/${base}.pptx"
```

---

## Quick Review Checklist

Most important items AI checks during review:

- [ ] No empty slides
- [ ] No text overflow
- [ ] Images placed correctly
- [ ] Notes have content (not just citations)
- [ ] Has agenda and summary
- [ ] 1 slide = 1 message
- [ ] Code blocks ≤10 lines (tech presentations)
- [ ] Diagrams/screenshots explained in notes
- [ ] CTA is clear (what should audience do next)
