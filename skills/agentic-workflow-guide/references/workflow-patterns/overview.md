# Workflow Patterns

Six fundamental patterns for agent workflows, plus IR Architecture and Connected Agents.

## Quick Reference

| Pattern                  | When to Use                       |
| ------------------------ | --------------------------------- |
| **Plan-First**           | Meta-pattern: Always start here   |
| **Prompt Chaining**      | Sequential tasks with validation  |
| **Routing**              | Processing varies by input type   |
| **Parallelization**      | Independent tasks run together    |
| **Orchestrator-Workers** | Dynamic task decomposition        |
| **Evaluator-Optimizer**  | Repeat until quality criteria met |
| **Connected Agents**     | Shared context collaboration      |

## Pattern Selection Flowchart

```
What's the nature of the task?
│
├─ Sequential processing needed (clear step ordering)
│   └─→ Prompt Chaining
│
├─ Multiple independent tasks (no mutual impact)
│   └─→ Parallelization
│
├─ Dynamic number of tasks (not predetermined)
│   └─→ Orchestrator-Workers
│
├─ Repeat until quality criteria met
│   └─→ Evaluator-Optimizer
│
└─ Processing varies significantly by input
    └─→ Routing
```

## Pattern Details

| #   | Pattern              | File                                                                   |
| --- | -------------------- | ---------------------------------------------------------------------- |
| 0   | Plan-First           | [0-plan-first.md](0-plan-first.md)                                     |
| 1   | Prompt Chaining      | [1-prompt-chaining.md](1-prompt-chaining.md)                           |
| 2   | Routing              | [2-routing.md](2-routing.md)                                           |
| 3   | Parallelization      | [3-parallelization.md](3-parallelization.md)                           |
| 4   | Orchestrator-Workers | [4-orchestrator-workers.md](4-orchestrator-workers.md)                 |
| 5   | Evaluator-Optimizer  | [5-evaluator-optimizer.md](5-evaluator-optimizer.md)                   |
| 6   | Connected Agents     | [6-connected-agents.md](6-connected-agents.md)                         |
| -   | IR Architecture      | [ir-architecture.md](ir-architecture.md) (Advanced transformation)    |
| -   | Combining Patterns   | [combining-patterns.md](combining-patterns.md) (Real-world workflows) |

## References

- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Workflows and Agents - LangChain](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [vscode-ai-toolkit Patterns](https://github.com/microsoft/vscode-ai-toolkit)
