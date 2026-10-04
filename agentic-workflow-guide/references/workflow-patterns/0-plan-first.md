# Pattern 0: Plan-First (Meta-Pattern)

**Plan and get approval before non-trivial execution**

> Back to [overview.md](overview.md)

Use for multi-step, costly, hard-to-reverse, or ambiguous work. Skip for one-line or obviously local changes.

## VS Code Implementation

- Built-in `plan` agent: set `agent: plan` in a prompt file, or hand off from a custom planner agent with `handoffs` (see [handoffs-guide.md](../handoffs-guide.md)).
- Collect approval or missing inputs with `vscode/askQuestions` in one batch, not per phase.
- Track execution with the `todos` tool so progress survives long sessions.
- Planner agents should be read-only (`tools: ["read", "search", "web"]`) so planning cannot mutate files before approval.

## Plan Contents (minimum)

- Goal and done criteria (how completion is verified)
- Steps with dependencies; mark which are parallelizable
- High-impact operations needing approval (delete, push, external send, deploy) listed up front
- Stop-state: what is left and how to resume if execution halts

## Failure Modes

| Failure                             | Fix                                                       |
| ----------------------------------- | --------------------------------------------------------- |
| Executes before approval            | Planner without edit/execute tools; approval gate in body |
| Re-asks approval at every phase     | Ask once, listing every high-impact action in the plan    |
| Plan drifts from execution silently | Update the todo list / plan file when scope changes       |
