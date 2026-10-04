# Pattern 3: Parallelization

**Execute independent tasks simultaneously**

> Back to [overview.md](overview.md)

Use for independent tasks (sectioning) or several independent judgments on the same input (voting).

## VS Code Copilot: Parallel Subagent Calls

An orchestrator with the `agent` tool set (`agent/runSubagent`) can issue several subagent calls in one turn; they run concurrently and all results return before the orchestrator continues. Each subagent has its own context window, but **not** its own file system, terminal, or COM session.

### Safety Requirements

Before parallelizing, verify **all three conditions**:

| Condition              | Check                                         | Example                      |
| ---------------------- | --------------------------------------------- | ---------------------------- |
| **No file conflict**   | Each agent writes to different output files   | A→file1.json, B→file2.json   |
| **No COM conflict**    | At most one agent uses COM (e.g., PowerPoint) | Only Build agent opens .pptx |
| **No data dependency** | Agents don't read each other's outputs        | A doesn't need B's result    |

### Implementation Pattern

```text
# Orchestrator body: issue all three subagent calls in the same turn
runSubagent(agentName: "Review",          description: "Review: MCP verification",  prompt: "...")
runSubagent(agentName: "Build PPTX",      description: "Build: slide insertion",    prompt: "...")
runSubagent(agentName: "Notes Generator", description: "Notes: speaker notes",      prompt: "...")
# Then verify every output (Gate below) before the next step.
```

### Dependency Table Template

Use this table in the Orchestrator's Step definition to document parallelization safety:

```markdown
| Agent           | Input               | Output               | COM | Conflict |
| --------------- | ------------------- | -------------------- | --- | -------- |
| Review          | region_info.json    | region_reviewed.json | No  | None     |
| Build PPTX      | classification.json | output.pptx          | Yes | None     |
| Notes Generator | classification.json | notes.json           | No  | None     |
```

### Gate Pattern (Wait for All)

After parallel execution, use a Gate to verify all agents completed:

```
Gate: All parallel agents completed
  - [ ] Agent A output exists and is valid
  - [ ] Agent B output exists and is valid
  - [ ] Agent C output exists and is valid
  → PASS: proceed to next step
  → FAIL: identify which agent failed, retry only that one
```

Wall-clock time drops from `sum(A, B, C)` toward `max(A, B, C)`; measure before claiming a speedup.

### Anti-Patterns

| ❌ Anti-Pattern                                       | ✅ Correct Approach                  |
| ----------------------------------------------------- | ------------------------------------ |
| Two agents writing to same file                       | Separate output files per agent      |
| Two agents using COM simultaneously                   | Only one COM agent in parallel group |
| Agent B reads Agent A's output                        | Sequential execution, not parallel   |
| Parallel agents using `execute/runInTerminal` at once | Stagger or isolate terminal usage    |
