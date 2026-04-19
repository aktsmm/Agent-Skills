# Skill Structure Gallery

Use this gallery when `/create-skill` needs concrete structure ideas, not just abstract rules.

Do not cargo-cult entire files. Copy the smallest pattern that removes ambiguity.

## Pattern 1: Signal Detection Matrix

Inspired by skills that review content against known tells.

Use when:

- The skill scans for repeated signals, smells, or rule violations
- Each detection should map cleanly to a recommended action
- A long prose list would hide the difference between "detect" and "fix"

Recommended shape:

| Category | Signal | Action |
| -------- | ------ | ------ |
| Tone     | Repeated filler opener | Remove or replace with concrete statement |
| Structure | Three identical sentence starts | Vary subject or sentence form |

Why it works:

- Compresses many heuristics into a searchable table
- Keeps detection logic and remediation aligned
- Makes reviews more consistent across languages or formats

Avoid when:

- There are fewer than 5 rules
- The output is procedural rather than evaluative

## Pattern 2: Mode Selection Table

Inspired by skills that support multiple execution modes or setup paths.

Use when:

- The user must choose between 2 or more viable modes
- Trade-offs matter more than linear steps
- Setup differs by environment, browser, provider, or transport

Recommended shape:

| Mode | Best For | Pros | Cons |
| ---- | -------- | ---- | ---- |
| Managed mode | First-time setup | Simpler defaults | Less control |
| Attached mode | Existing environment reuse | Reuses login/session | More prerequisites |

Why it works:

- Surfaces the decision before the workflow branches
- Prevents hidden assumptions about the default path
- Gives `/create-skill` a compact way to encode trade-offs

Avoid when:

- There is a single recommended path with no real branching

## Pattern 3: Output Pair and Variant Naming

Inspired by skills that produce both editable and publishable artifacts.

Use when:

- One task creates multiple deliverables that must stay aligned
- The user needs both source and rendered output
- Language or format variants must coexist without overwrite risk

Recommended shape:

```text
name.ext           # editable or source artifact
name-rendered.ext  # publishable artifact
name-ja.ext        # language variant
name-en.ext        # language variant
```

Add a short rule block:

- Keep editable and publishable outputs as a pair
- Prefer parallel filenames over overwriting one artifact
- Name variants predictably so downstream docs can link them safely

Why it works:

- Makes the deliverable contract explicit
- Reduces drift between source and rendered assets
- Gives reviews a simple naming baseline

Avoid when:

- The task only creates one disposable output

## Pattern 4: Quality Gates and Score Bands

Inspired by skills that need objective retry or escalation rules.

Use when:

- The workflow has review/retry loops
- "Good enough" must be defined before execution
- The agent should know when to proceed, retry, simplify, or ask

Recommended shape:

| Score | Action |
| ----- | ------ |
| 90-100 | Proceed |
| 70-89 | Fix and retry |
| 50-69 | Simplify |
| 0-49 | Ask user |

Why it works:

- Turns vague quality judgment into a stop condition
- Prevents endless refinement loops
- Helps `/create-skill` encode escalation behavior in one table

Avoid when:

- Quality is binary and easy to verify with a checklist alone

## Pattern 5: Architecture Sketch and Naming Taxonomy

Inspired by skills that transform files through several stages.

Use when:

- The skill moves data across multiple steps or folders
- Naming rules are part of the workflow contract
- The user needs to understand where ambiguous items land

Recommended shape:

```text
Input
  -> Normalize
  -> Classify
  -> Rename
  -> Output
  -> Fallback / quarantine branch
```

Then pair it with a naming block:

```text
YYYY-MM-DD-type-subject.ext
```

And, if needed, a taxonomy table:

| Code | Meaning | Trigger |
| ---- | ------- | ------- |
| doc  | Formal document | invoice, contract |
| img  | Screenshot/image | png, jpg |
```

Why it works:

- Explains the pipeline faster than long prose
- Makes edge cases visible, especially fallback paths
- Gives naming conventions a place near the workflow they support

Avoid when:

- The task is a simple one-shot transformation

## Quick Selection Guide

| If the skill needs... | Start with... |
| --------------------- | ------------- |
| Repeated review signals | Signal Detection Matrix |
| A user-facing branch choice | Mode Selection Table |
| Multiple coordinated deliverables | Output Pair and Variant Naming |
| Retry thresholds or escalation | Quality Gates and Score Bands |
| A multi-stage file/data pipeline | Architecture Sketch and Naming Taxonomy |

Use one or two patterns first. If the structure starts looking like a dashboard, the skill is probably over-designed.