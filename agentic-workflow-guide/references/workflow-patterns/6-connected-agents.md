# Pattern 6: Connected Agents

**Multiple specialized agents collaborate and share context**

> Back to [overview.md](overview.md)

> Naming: this is the generic shared-context (blackboard) pattern. It is **not** the Microsoft Foundry "Connected Agents" feature.
>
> Foundry Connected Agents is a main agent calling sub-agents as tools (closer to [Orchestrator-Workers](4-orchestrator-workers.md)), documented under Foundry (classic): [Connected Agents (classic)](https://learn.microsoft.com/ja-jp/azure/foundry-classic/agents/how-to/connected-agents).

Use when specialized agents must build on each other's decisions across steps or sessions. Do not use when agents work independently ([Parallelization](3-parallelization.md)) or when one orchestrator can hold the state ([Orchestrator-Workers](4-orchestrator-workers.md)).

## VS Code Implementation

- The shared context is a file in the workspace (e.g. `tmp/project-context.json` or a Markdown state file), not chat history; subagents run in an isolated context and see only what their prompt or the file gives them.
- Every agent reads the file at start and writes its decision / artifact path at end. Instruct this in each agent body.
- Default to turn-taking (handoffs or sequential subagent calls). Subagents share one file system, so parallel writers to the same context file race.
- Keep current state and history in separate regions; extract current state by boundary, not keyword search (see [ir-architecture.md](ir-architecture.md#current-state-in-append-only-documents)).

## Coordination Strategies

| Strategy            | Trade-off                                         |
| ------------------- | ------------------------------------------------- |
| Sequential          | No conflicts; slowest. Default choice             |
| Parallel with merge | Fast; needs per-agent output files then one merge |
| Leader-follower     | Clear control; leader becomes the bottleneck      |

## Context Format Example

```json
{
  "project_context": {
    "goal": "Build a web scraper",
    "constraints": ["Must handle rate limiting", "Store in database"],
    "decisions": [
      {
        "agent": "research",
        "timestamp": "2024-01-15T10:00:00Z",
        "decision": "Use Python with BeautifulSoup",
        "rationale": "Simple, well-documented, handles HTML parsing"
      }
    ],
    "artifacts": [
      {
        "type": "design_doc",
        "created_by": "design_agent",
        "path": "docs/architecture.md"
      }
    ],
    "state": "implementation_in_progress"
  }
}
```

## Failure Modes

| Failure                                 | Mitigation                                                      |
| --------------------------------------- | --------------------------------------------------------------- |
| Two agents overwrite the context file   | Turn-taking, or per-agent output files merged by one owner      |
| Old decision revived as current         | Separate current-state region from append-only history          |
| Context file grows until agents skim it | Prune or archive superseded decisions; keep current state short |
| Cannot tell who changed what            | Each write records `agent`, `timestamp`, and artifact path      |
| Agent claims an update it never wrote   | Next agent verifies the file changed before using it            |
