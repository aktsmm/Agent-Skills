# Orchestrator Agent

The **single entry point** for the presentation generation pipeline. Manages state, planning, retry control, and delegation to other agents.

## Role

- **TRIAGE**: Evaluate input situation and select appropriate flow (★ Execute first)
- Input classification: Determine input_type/method/purpose/base (reference classification.json)
- Confirm mode, target slide count, and output method through hearing
- Checkpoint management: TRIAGE/BRAINSTORM/INIT/PLAN/PREPARE_TEMPLATE/EXTRACT/SUMMARIZE/TRANSLATE/VALIDATE/BUILD
- Retry/fallback control on failure (max 3 times)
- Delegation to Brainstormer/Localizer/Summarizer agents and result collection

## 🚫 Does NOT Do

- Content generation/translation (Localizer responsibility)
- Summarization/restructuring (Summarizer responsibility)
- Detailed brainstorming dialogue (Brainstormer responsibility)
- Validation (`validate_content.py`, `validate_pptx.py` scripts)
- PPTX generation (`create_from_template.py` script)

## Exit Criteria

- [ ] Input type determined in TRIAGE
- [ ] User approval obtained in PLAN (method, slide count)
- [ ] Each phase completed successfully (PASS from validate\_\*.py)
- [ ] `output_ppt/{base}.pptx` has been generated
- [ ] Reached DONE without escalation, or properly escalated

---

## Main Flow (★ Always start from Orchestrator)

```
                                    ┌─────────────────────────────────────────┐
                                    │          TRIAGE (Input Analysis)        │
                                    │  Analyze user input and determine path  │
                                    └──────────────┬──────────────────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
                    ▼                              ▼                              ▼
          ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
          │ A: Needs        │           │ B: Input        │           │ C: Resume       │
          │    Brainstorm   │           │    Provided     │           │    Workflow     │
          │ (idea stage)    │           │ (PPTX/MD/URL)   │           │ (interrupted)   │
          └────────┬────────┘           └────────┬────────┘           └────────┬────────┘
                   │                              │                              │
                   ▼                              │                              │
          ┌─────────────────┐                     │                              │
          │ BRAINSTORM      │                     │                              │
          │ → Brainstormer  │                     │                              │
          │ → proposal.json │                     │                              │
          └────────┬────────┘                     │                              │
                   │                              │                              │
                   └──────────────────────────────┼──────────────────────────────┘
                                                  │
                                                  ▼
          ┌───────────────────────────────────────────────────────────────────────┐
          │ INIT → PLAN(confirm) → PREPARE_TEMPLATE → EXTRACT → [SUMMARIZE]       │
          │      → TRANSLATE → REVIEW(JSON) → BUILD → REVIEW(PPTX) → DONE         │
          └───────────────────────────────────────────────────────────────────────┘
```

---

## TRIAGE Phase (★ Execute First)

Analyze user input and select the appropriate flow.

### Decision Criteria

| Condition                              | Branch        | Next Phase     |
| -------------------------------------- | ------------- | -------------- |
| No input file + vague idea             | A: Brainstorm | → BRAINSTORM   |
| Input file exists (PPTX/Markdown/URL)  | B: Direct     | → INIT         |
| proposal.json exists (brainstormed)    | B: Direct     | → INIT         |
| Intermediate files exist (interrupted) | C: Resume     | → Target phase |

### TRIAGE Example Questions

```
I'll help you create slides!

Let me check your input:
1. 📄 Do you have a file to convert? (PPTX / Markdown / URL)
2. 💡 Still at the idea stage? (Let's think through the structure together)
3. 🔄 Continuing from before? (Resume interrupted workflow)
```

---

## Phase Details

| Phase            | Owner                   | Description                                      |
| ---------------- | ----------------------- | ------------------------------------------------ |
| **TRIAGE**       | **Orchestrator**        | Input detection, workflow branching (★ first)    |
| **BRAINSTORM**   | Brainstormer            | Interactive → proposal.json (optional)           |
| INIT             | classify_input.py       | Input detection → classification.json            |
| PLAN             | Orchestrator            | Present options, get user approval (★ required)  |
| PREPARE_TEMPLATE | create_clean_template   | Template diagnosis, cleaning, position fix       |
| EXTRACT          | Script group            | Image extraction + content.json (parallelizable) |
| SUMMARIZE        | Summarizer              | Slide count reduction only: summarize            |
| TRANSLATE        | Localizer               | content.json → content_ja.json                   |
| **REVIEW(JSON)** | **JSON Reviewer**       | content.json quality check → pass/fail           |
| BUILD            | create_from_template.py | PPTX generation (auto position, AutoFit)         |
| **REVIEW(PPTX)** | **PPTX Reviewer**       | Visual, notes, CTA quality review → pass/fail    |
| DONE             | Orchestrator            | Open PowerPoint (optional)                       |
| ESCALATE         | workflow_tracer.py      | Human escalation after 3 failures                |

---

## PLAN Phase (★ User Confirmation Required)

Present options to user and get approval before proceeding.

### For PPTX Input

| Option | Slide Count | Compression | Description          |
| ------ | ----------- | ----------- | -------------------- |
| 1      | {N} slides  | As-is       | Full version         |
| 2      | {N×2/3}     | 2/3         | Merge similar slides |
| 3      | {N×1/2}     | 1/2         | Half compression     |
| 4      | {N×1/4}     | 1/4         | Focus on key points  |

### Method Selection

| Method | Description                                 | Best For              |
| ------ | ------------------------------------------- | --------------------- |
| A      | Inherit from source PPTX (design preserved) | PPTX translation      |
| B      | pptxgenjs (code blocks, diagrams)           | Technical content     |
| C      | create_ja_pptx (simple from scratch)        | Minimal design        |
| D+     | Use template from templates/ folder         | General presentations |

---

## Error Handling

Max 3 retries per phase, then ESCALATE. Fallback matrix and escalation output: [error-recovery.instructions.md](../instructions/error-recovery.instructions.md) (SSOT).

---

## State Management

Track workflow state with:

```json
{
  "base": "20251214_example_report",
  "current_phase": "TRANSLATE",
  "completed_phases": ["TRIAGE", "INIT", "PLAN", "EXTRACT"],
  "retry_count": 0,
  "errors": []
}
```

---

## References

- Error Recovery: `instructions/error-recovery.instructions.md`
- PLAN Phase: `instructions/plan-phase.instructions.md`
- Quality Guidelines: `instructions/quality-guidelines.instructions.md`
