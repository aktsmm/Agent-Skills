# Design Principles

Rationale for agent-workflow design. Textbook definitions (SRP, DRY, KISS, idempotency, etc.) are assumed knowledge; each section keeps only the agent-workflow-specific rule and non-obvious gotchas. Review questions live in [review-checklist.md](review-checklist.md).

## Table of Contents

- [Tier 1: Core Principles](#tier-1-core-principles-essential) - SSOT, SRP, Simplicity First, Fail Fast, Iterative, Feedback Loop
- [Tier 2: Quality Principles](#tier-2-quality-principles-recommended) - Transparency, Gate/Checkpoint, DRY, ISP, Idempotency, Observability, Reasoning
- [IR Architecture](#intermediate-representation-ir-architecture) - Two-stage pattern (reference)
- [Tier 3: Scale Principles](#tier-3-scale-principles-advanced) - Human-in-the-Loop, KISS, Loose Coupling, Graceful Degradation
- [ACI Design](#aci-design-agent-computer-interface) - Tool design guidelines
- [File Organization](#file-organization-principles) - Instructions organization, naming conventions
- [SSOT Implementation Patterns](#ssot-implementation-patterns) - Reference format, View vs Master

---

## Tier 1: Core Principles (Essential)

### 1. SSOT (Single Source of Truth)

Centralize context, configuration, and state; agents must not each keep their own copy of shared settings.

**Multi-Agent Propagation Rule:** In Orchestrator-Workers patterns, a rule written only in the central document (e.g., `AGENTS.md`) is often ignored by workers. Reference or include it in each worker `.agent.md` (output paths in particular). When adding a shared rule, update the central doc + each `.agent.md` + scripts + instructions together.

### 2. SRP (Single Responsibility Principle)

1 agent = 1 responsibility. Split an agent that handles "search + analysis + reporting" by role.

### 3. Simplicity First

Try a single prompt or agent first; add agents only when evaluation shows the simpler setup falls short.

> "Start with simple prompts, optimize them with comprehensive evaluation, and add multi-step agentic systems only when simpler solutions fall short." — Anthropic

### 4. Fail Fast

Validate at each step and stop on issues (Gates/Checkpoints) instead of continuing to the end.

**Contract Binding Liveness:**

Paths, schema fields, CLI flags, IDs, and state keys referenced by policies, orchestrators, validators, and tests are executable contracts. A rename or deletion is incomplete until every live binding is updated.

- Before deleting or renaming an artifact, search policy/config, runtime code, tests, and generated-current-state definitions for references.
- Add a deterministic liveness check at the workflow entry or CI boundary; tests alone are insufficient if operators may not run them before production.
- Compare canonical path spelling against the source of truth. Git path case remains significant even on case-insensitive filesystems and can turn history/readback into a silent `not found`.
- Structural faults such as unmapped inputs, missing artifacts, and case mismatches must fail before freshness or scheduling filters. Ordinary pending work must remain allowed.

### 5. Iterative Refinement

MVP → verify → improve, one task at a time. Related pattern: Evaluator-Optimizer.

### 6. Feedback Loop

Evaluate each step against environment ground truth (tool results, tests) and re-execute if needed; avoid one-way flows.

> "During execution, it's crucial for the agents to gain 'ground truth' from the environment at each step to assess its progress." — Anthropic

---

## Tier 2: Quality Principles (Recommended)

### 7. Transparency

Show the plan and step progress (e.g., a todo list: VS Code `todos`, Claude Code `TodoWrite`). Anthropic: "Prioritize transparency by explicitly showing the agent's planning steps."

### 8. Gate/Checkpoint

Define pass criteria and failure handling for each step; do not proceed until they are met.

### 9. DRY (Don't Repeat Yourself)

Share common processing as prompt templates or skills instead of copy-pasting the same prompt into each agent. See [SSOT Implementation Patterns](#ssot-implementation-patterns).

### 10. ISP (Interface Segregation Principle)

Pass each agent only task-relevant information; excess context is noise. See [context-engineering.md](context-engineering.md).

### 11. Idempotency

Retries must not duplicate side effects: check current state first and use unique IDs.

**Queue Hygiene for Issue/PR Automation:**

For workflows that create or resume work through Issues, labels, and PRs, retry safety depends on treating those queue artifacts as workflow state.

- Before creating new work, check whether an equivalent Issue or PR is already open.
- If a blocker label such as `needs-human-review` can become stale, only auto-clear it under explicit safe conditions, for example when no open PR remains and the rerun was manual or triggered by a fresh failure.
- If the latest evaluation says there is no actionable work, auto-close stale request Issues so the queue does not look blocked forever.

### 12. Observability

Record key decisions (Issue comments, files, a `Time | Decision | Rationale` log) and report progress on long tasks.

**Idle State Visibility:**

If `0 new items` is a valid and healthy result, surface that state separately from `latest published artifact date`.
Otherwise, users may misread a normal no-op run as a stale deployment or failed automation.

**Elapsed Time Tracking:** For multi-step workflows, record `startedAt` / `completedAt` / `elapsedMinutes` in a status file (e.g., `manifest/status.json`) to detect regressions and bottlenecks across runs.

### 13. Reasoning Before Conclusions

Structure prompts so the agent analyzes and compares options before deciding, with space to reason before the final output. This makes decisions auditable.

```markdown
Before selecting a workflow pattern:

1. Analyze the task characteristics
2. List applicable patterns with pros/cons
3. Recommend the best fit based on your analysis
```

---

## Intermediate Representation (IR) Architecture

→ **[workflow-patterns/ir-architecture.md](workflow-patterns/ir-architecture.md)** (SSOT)

For complex workflows, use a two-stage architecture with an intermediate representation.
Core principle: **Same IR → Same Output.** No creativity in transformation phase.

---

## Tier 3: Scale Principles (Advanced)

| Principle                | Agent-workflow rule                                                                                        |
| ------------------------ | ---------------------------------------------------------------------------------------------------------- |
| **Human-in-the-Loop**    | Confirm before high-risk or irreversible operations (production deploy, mass deletion, external send)      |
| **KISS**                 | Use the sufficient number of agents and the simplest coordination that works                               |
| **Loose Coupling**       | Standardize agent inputs/outputs so each agent can be changed and tested independently                     |
| **Graceful Degradation** | Provide fallbacks or skippable steps so a partial failure doesn't stop everything; report what was skipped |

---

## ACI Design (Agent-Computer Interface)

**Anthropic's Recommendation:**

> "Think about how much effort goes into human-computer interfaces (HCI), and plan to invest just as much effort in creating good agent-computer interfaces (ACI)."

### Core Principles

| Principle                  | Description                                            |
| -------------------------- | ------------------------------------------------------ |
| **Minimal Overlap**        | Each tool has a distinct, non-overlapping purpose      |
| **Self-Contained**         | Tools are robust to errors and handle edge cases       |
| **Clear Intent**           | Tool name and description unambiguously convey purpose |
| **Model-Friendly Formats** | Output formats are easy for LLMs to parse and use      |

### Tool Design Guidelines

1. **Clear Description** - Clarify tool purpose and usage
2. **Edge Cases** - Document boundary conditions
3. **Input Format** - Specify expected input format
4. **Error Handling** - Define behavior on failure
5. **Testing** - Actually use it and iterate
6. **Example Usage** - Include usage examples in description
7. **Poka-yoke** - Design to prevent mistakes (e.g., use absolute paths)
8. **Display Surface Fit** - Match output structure to where users will read it, such as cards/fields for chat embeds instead of dense text

### Format Selection

Choose formats that minimize cognitive load for LLMs:

| Good Format                               | Avoid                                  |
| ----------------------------------------- | -------------------------------------- |
| Markdown code blocks                      | JSON with escaped strings              |
| Absolute file paths                       | Relative paths (context-dependent)     |
| Structured sections                       | Free-form text with implicit rules     |
| Clear delimiters (XML tags)               | Ambiguous separators                   |
| Native UI payloads for the target surface | One dense text block for every channel |

### Anthropic's Tool Format Recommendations

> "Give the model enough tokens to 'think' before it writes itself into a corner. Keep the format close to what the model has seen naturally occurring in text on the internet."

**Do:**

- Use formats the model has seen in training (Markdown, code, XML)
- Allow space for reasoning before final output
- Use descriptive parameter names

**Don't:**

- Require accurate counting (e.g., line numbers in diffs)
- Force heavy escaping (e.g., code inside JSON strings)
- Create ambiguous decision points between similar tools

### Tool Set Design

| Symptom                       | Problem                        | Solution                         |
| ----------------------------- | ------------------------------ | -------------------------------- |
| User unsure which tool to use | Overlapping functionality      | Consolidate or clearly delineate |
| Frequent tool misuse          | Unclear descriptions           | Improve docs, add examples       |
| Verbose tool outputs          | Wasted context tokens          | Return summaries, not raw data   |
| Error-prone inputs            | Complex parameter requirements | Simplify, use defaults           |

### Testing Checklist

```markdown
- [ ] Can a junior developer understand how to use this tool from its description?
- [ ] Does running multiple test inputs produce expected outputs?
- [ ] Are error messages actionable?
- [ ] Is the output format consistent and parseable?
- [ ] Has the output been checked in the final reading surface or a faithful dry-run payload?
- [ ] Does the tool handle edge cases gracefully?
```

---

## File Organization Principles

- Once `.github/instructions/` becomes hard to scan, group files into domain folders (e.g., `azure/`, `git/`, `code/`) and keep at most one cross-cutting file. Confirm the host actually discovers subfolders (Chat Diagnostics) before moving files.
- File names are lowercase kebab-case, descriptive, and carry the type suffix: `.instructions.md`, `.prompt.md`, `.agent.md`, `SKILL.md`. Avoid generic names such as `notes.md`, `conventions.md`, `agent1.agent.md`, `test.prompt.md`.
- Agent and prompt names are role- or action-oriented (`code-reviewer.agent.md`, `summarize-pr.prompt.md`).
- Prompt files are not loaded by Agent Host sessions; prefer skills for new reusable slash-invoked workflows (see [customization-decision.md](customization-decision.md)).

---

## References

- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Writing tools for AI agents - Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)

---

## SSOT Implementation Patterns

### SSOT Reference Pattern

When referencing shared definitions across multiple files, use this standard format, replacing `<file>` with a relative Markdown link to the SSOT file:

```markdown
> **SSOT**: See <file> section "Section Name" for details
```

The referenced heading MUST exist in the target file, and the target MUST hold the definition itself. A pointer to a section that only forwards elsewhere leaves the rule undefined while every checker still reports the link as valid.

Anti-pattern: the same logic (e.g., holiday check, validation rules) duplicated in 3+ files drifts over time. Define it once and reference it, e.g. a step that says `> **SSOT**: See copilot-instructions.md section "Holiday Rules"` and then only applies the rule.

### View vs Master Separation

For task/project management workflows, separate display views from data masters:

| File Type                  | Role                    | Update Frequency   | Content         |
| -------------------------- | ----------------------- | ------------------ | --------------- |
| **View (Dashboard)**       | Today's top 3 actions   | Daily (morning)    | Links to Master |
| **Master (active.md)**     | All task details (SSOT) | On change          | Full task specs |
| **Archive (completed.md)** | Completion history      | On task completion | Archived tasks  |

> ⚠️ **Anti-pattern**: Putting task tables in both View and Master creates dual maintenance burden.

**Correct Structure:**

```
DASHBOARD.md (View)
├── Today's Focus: TOP 3 actions (links only)
├── This Week: Schedule view
└── Recent Completions: Last 5 items

Tasks/active.md (Master - SSOT)
├── Full task details
├── All metadata
└── History
```

### Activity Log Collection Strategy

When collecting activity logs from integrated tools (M365, Slack, etc.), use multiple query types for comprehensive coverage:

| Query Type   | Purpose                    | Detection Target                 |
| ------------ | -------------------------- | -------------------------------- |
| **My Posts** | What I shared in channels  | Knowledge sharing, contributions |
| **Mentions** | Messages that mentioned me | Requests, thanks, dependencies   |
| **Files**    | Files I shared/edited      | Deliverables, documentation      |

> ⚠️ **Single query anti-pattern**: Using only one query type causes detection gaps.

**Example queries:**

1. `What did I post in channels today?` → Own contributions
2. `What messages mentioned me today?` → Inbound requests
3. `What files did I share today?` → Artifacts created
