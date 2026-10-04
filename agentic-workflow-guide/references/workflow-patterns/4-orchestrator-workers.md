# Pattern 4: Orchestrator-Workers

**Dynamically decompose tasks → Dispatch to workers**

> Back to [overview.md](overview.md)

Use when the number of subtasks is only known at runtime and results must be synthesized. If the subtasks are fixed, use [Prompt Chaining](1-prompt-chaining.md) or [Parallelization](3-parallelization.md) instead.

## Delegated Evidence Contract

Do not treat `0 results` as proof that a worker ran successfully. Every delegated data-collection step should return:

```json
{
  "execution_state": "executed|not_run|blocked",
  "status": "success|partial|failed",
  "result_count": 0,
  "prerequisite_state": "ready|missing|unknown",
  "evidence_at": "ISO-8601 timestamp",
  "executed_by": "worker-name",
  "failure_reason": ""
}
```

- `result_count=0` is valid only when the worker executed and its prerequisite was ready.
- A missing tool, unmet prerequisite, timeout, or unavailable worker is `not_run` / `blocked`, never an empty success.
- The synthesizer preserves partial and failed states instead of collapsing them into a clean result.

## VS Code Copilot: Agent Definition

Workers are subagents called through the `agent` tool set (`agent/runSubagent`). Orchestrators tend to skip delegation and do the work inline unless the body makes delegation the required path.

```yaml
---
name: Code Review Orchestrator
description: Review changed files by delegating one subagent per file
tools: ["agent", "search", "read"]
agents: ["Review Worker", "General Assistant"]
---

## Workflow

1. Identify files to review (search).
2. For each file, call #tool:agent/runSubagent with:
   - Prompt: "Review {filepath}. Return: {bugs: [], style: [], security: []}"
3. Aggregate subagent results only; do not read file bodies directly.
4. Generate the final report.
```

- State delegation as a rule ("call a subagent for each file; do not review directly"), not an option ("you can use sub-agents if needed").
- Specify the worker's return format in every subagent prompt so synthesis is mechanical.
- `agents` limits callable workers (`[]` = none, `*` = all); when set, keep `agent` in `tools`. Hide worker-only agents from the picker with `user-invocable: false` (`infer` is deprecated).
- A worker calling itself or other workers requires `chat.subagents.allowInvocationsFromSubagents`; otherwise keep nesting at one level.

## General Assistant (Fallback Worker)

Add a General Assistant worker for greetings, quick clarifications, and requests outside every specialist's scope, so the orchestrator never answers "I can't help" and never builds a full plan for a one-line request. It is a fallback, not a shortcut: work that has a specialist goes to the specialist.

## Parallel Workers (with Pattern 3)

Dispatch independent workers in the same turn only after the safety table and gate in [3-parallelization.md](3-parallelization.md) pass; retry only the worker that failed.

### Splitting for Parallelization

When one agent does both AI reasoning and mechanical execution, split them so the reasoning part can run in parallel:

```
Before: Enrich Agent = AI notes generation + PowerPoint writing   → T(AI) + T(write)
After:  Notes Generator (parallel with others) → Enrich (write only) → max(T(AI), T(others)) + T(write)
```

Split only when the two responsibilities use different tools (e.g. MCP vs COM), share no state, and one of them is the bottleneck.

## Map-Reduce Synthesis for Cross-Item Coherence

When a review/audit orchestrator must check **cross-item coherence** (across chapters, files, sections), re-reading every item's full text in the orchestrator inflates context and pulls it back into "reviewing directly".

- Each worker returns `findings` **plus** a compact extract (terms / definitions / key claims / assumptions) — not the raw body.
- The orchestrator reduces over the extract index only to detect cross-item conflicts (definition drift, term/naming inconsistency, broken forward/back references, one item's premise contradicting another). The body is never passed to the reduce step.
- Attribute each conflict to the findings of **both** items involved.

This keeps Context Discipline and delegation discipline intact: per-item judgment stays in workers (map), and only compact extracts cross into the orchestrator (reduce).

## Dynamic Worker Creation (New Task Detection)

When a task matches no existing worker, the orchestrator must not silently create a new `.agent.md`. New workers add files, tokens, and maintenance; one-off tasks belong to the General Assistant.

```markdown
## Dynamic Worker Rules

When a task matches no existing worker:

1. Stop; do not create a worker automatically.
2. Propose via #tool:vscode/askQuestions:
   - Task type detected, proposed worker name, responsibilities
   - Option A: create a new '{type} Worker' subagent
   - Option B: handle with General Assistant
3. Wait for an explicit choice, then follow it.
```

Failure mode to prevent: the orchestrator silently creates `DatabaseWorker`, `SecurityWorker`, `PerformanceWorker`, and the user only learns of it from cost and latency.
