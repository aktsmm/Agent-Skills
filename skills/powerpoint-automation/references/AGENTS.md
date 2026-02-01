# AGENTS

Agent definitions for PPTX automation pipeline.

## Design Principles

| Principle             | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| **SSOT**              | Each rule defined in one place only; others reference it   |
| **Agent vs Script**   | AI judgment needed → Agent; deterministic → Script         |
| **IR Separation**     | Agents communicate via JSON (content.json) loosely coupled |
| **Fail Fast**         | Early error detection; escalate after 3 retries            |
| **Human in the Loop** | User confirmation required for important decisions         |

> 📖 See [common.instructions.md](instructions/common.instructions.md) for details.

---

## Documentation SSOT Map

| Topic                     | Source (SSOT)                                          |
| ------------------------- | ------------------------------------------------------ |
| PLAN Phase Confirmation   | `instructions/plan-phase.instructions.md`              |
| Naming & Bullet Rules     | `instructions/common.instructions.md`                  |
| Quality Guidelines        | `instructions/quality-guidelines.instructions.md`      |
| Tools & Workflow          | `instructions/tools-reference.instructions.md`         |
| IR Schema                 | `schemas/content.schema.json`                          |
| **Error Recovery**        | **`instructions/error-recovery.instructions.md`**      |
| **Script Dependencies**   | **`instructions/script-dependencies.instructions.md`** |
| **Speaker Notes Quality** | **`instructions/quality-guidelines.instructions.md`**  |
| **content_with_image**    | **`instructions/template-advanced.instructions.md`**   |

---

## Agent List

| Agent             | Manifest                        | Role                                         |
| ----------------- | ------------------------------- | -------------------------------------------- |
| **Brainstormer**  | `agents/brainstormer.agent.md`  | Interactive ideation → proposal.json         |
| Orchestrator      | `agents/orchestrator.agent.md`  | State management, planning, retry control    |
| Localizer         | `agents/localizer.agent.md`     | Translation only (AI judgment)               |
| Summarizer        | `agents/summarizer.agent.md`    | Summarization & restructuring (AI judgment)  |
| **JSON Reviewer** | `agents/json-reviewer.agent.md` | content.json review (translation, structure) |
| **PPTX Reviewer** | `agents/pptx-reviewer.agent.md` | PPTX review (visual, notes, CTA quality)     |

> ⚠️ `reviewer.agent.md` was renamed and split into `json-reviewer.agent.md`.

## Script List

| Script                     | Purpose                            | Auto-Fix Features                  |
| -------------------------- | ---------------------------------- | ---------------------------------- |
| `classify_input.py`        | Input classification               | -                                  |
| `validate_content.py`      | IR schema validation               | -                                  |
| `validate_pptx.py`         | PPTX validation                    | -                                  |
| `review_pptx.py`           | PPTX content extraction for review | -                                  |
| `create_from_template.py`  | PPTX generation                    | AutoFit disable, position adjust   |
| `create_clean_template.py` | Clean template from source PPTX    | Vertical text fix, decoration trim |
| `diagnose_template.py`     | Template quality diagnosis         | -                                  |
| `clean_template.py`        | Template cleaning                  | Background removal, ref fix        |
| `analyze_template.py`      | Layout analysis → layouts.json     | -                                  |
| `merge_slides.py`          | Merge diagram slides into template | -                                  |
| `insert_diagram_slides.py` | Insert diagram slides at position  | Scaling, layout selection          |
| `workflow_tracer.py`       | Trace log output                   | -                                  |

> 📖 See [script-dependencies.instructions.md](instructions/script-dependencies.instructions.md) for dependencies.

---

## Standard Workflow

### Main Flow (★ Always start from Orchestrator)

```
                                    ┌─────────────────────────────────────────┐
                                    │     TRIAGE (Orchestrator decides)       │
                                    └──────────────┬──────────────────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
                    ▼                              ▼                              ▼
          ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
          │ A: Needs        │           │ B: Input        │           │ C: Resume       │
          │    Brainstorm   │           │    Provided     │           │    Workflow     │
          │ → BRAINSTORM    │           │ → INIT          │           │ → Target Phase  │
          └────────┬────────┘           └────────┬────────┘           └────────┬────────┘
                   │                              │                              │
                   ▼                              │                              │
          proposal.json                           │                              │
                   │                              │                              │
                   └──────────────────────────────┴──────────────────────────────┘
                                                  │
                                                  ▼
          ┌───────────────────────────────────────────────────────────────────────┐
          │ INIT → PLAN(confirm) → PREPARE_TEMPLATE → EXTRACT → [SUMMARIZE]       │
          │      → TRANSLATE → REVIEW(JSON) → BUILD → REVIEW(PPTX) → DONE         │
          │                                     │                    │            │
          │                    └────(FAIL → fix, max 3×)─────────────┘            │
          │                                     ↓                                 │
          │                                ESCALATE (>3 failures)                 │
          └───────────────────────────────────────────────────────────────────────┘
```

### Phase Details

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

### Auto-Fixes in PREPARE_TEMPLATE

| Detection             | Fix Action | Related Issue       |
| --------------------- | ---------- | ------------------- |
| Off-slide shapes      | Remove     | #41 Vertical text   |
| Left-edge decorations | Remove     | #35 Title offset    |
| Narrow placeholders   | Widen      | #39 Title line wrap |

### Auto-Fixes in BUILD

| Detection                | Fix Action    | Related Issue             |
| ------------------------ | ------------- | ------------------------- |
| AutoFit text spacing     | Disable       | #42 Japanese text spacing |
| Title position (Section) | Fix at 35%    | #43 Position issues       |
| Subtitle position        | Title + 0.15" | #37 Too far apart         |

> 📖 See [error-recovery.instructions.md](instructions/error-recovery.instructions.md) for recovery details.

---

## Common I/O Contract

| Type         | Path                            |
| ------------ | ------------------------------- |
| User Input   | `input/`                        |
| Intermediate | `output_manifest/{base}_*.json` |
| Images       | `images/{base}/`                |
| Final Output | `output_ppt/{base}.pptx`        |

**Base naming convention**: `{YYYYMMDD}_{keyword}_{purpose}`

---

## Method Selection

| Use Case               | Recommended Method                      | Rating     |
| ---------------------- | --------------------------------------- | ---------- |
| **EN PPTX → Japanese** | reconstruct + create_from_template      | ⭐⭐⭐⭐⭐ |
| **With Template**      | analyze_template + create_from_template | ⭐⭐⭐⭐⭐ |
| From scratch           | create_ja_pptx.py                       | ⭐⭐⭐⭐   |
| Code-heavy content     | pptxgenjs                               | ⭐⭐⭐⭐   |

---

## Operational Rules

- Follow instructions documents within this skill
- Direct editing of templates/PPTX is prohibited
- Run `analyze_template.py` when using new templates

---

## Troubleshooting

Common issues and solutions:

- **Template load error**: Run `diagnose_template.py` to diagnose template
- **Image overlap**: Add `content_with_image` mapping to `layouts.json`
- **Text overflow**: Detect with `validate_pptx.py`, reduce item count
- **Translation quality**: Auto-checked by JSON Reviewer, escalate after 3 retries
