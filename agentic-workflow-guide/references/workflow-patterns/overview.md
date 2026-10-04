# Workflow Patterns

Selector only. Each file keeps the VS Code / Copilot implementation notes, stop conditions, and failure modes; the generic pattern theory is in the Anthropic article below.

Pick the simplest pattern that fits; combine only when one pattern cannot express the flow.

| Pattern              | Choose when                                                        | File                                                   |
| -------------------- | ------------------------------------------------------------------ | ------------------------------------------------------ |
| Plan-First (meta)    | Multi-step, costly, or ambiguous work before any execution         | [0-plan-first.md](0-plan-first.md)                     |
| Prompt Chaining      | Fixed step order; each output feeds the next and needs a gate      | [1-prompt-chaining.md](1-prompt-chaining.md)           |
| Routing              | Processing differs clearly by input category                       | [2-routing.md](2-routing.md)                           |
| Parallelization      | Independent tasks with no shared files, COM, or data dependency    | [3-parallelization.md](3-parallelization.md)           |
| Orchestrator-Workers | Subtask count is only known at runtime; delegated evidence matters | [4-orchestrator-workers.md](4-orchestrator-workers.md) |
| Evaluator-Optimizer  | Explicit quality criteria; iterate with a retry cap                | [5-evaluator-optimizer.md](5-evaluator-optimizer.md)   |
| Connected Agents     | Agents build on a shared, persisted context (blackboard)           | [6-connected-agents.md](6-connected-agents.md)         |
| IR Architecture      | Deterministic transformation; append-only current-state extraction | [ir-architecture.md](ir-architecture.md)               |
| Combining Patterns   | Real workflows that need more than one of the above                | [combining-patterns.md](combining-patterns.md)         |

## References

- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Workflows and Agents - LangChain](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [vscode-ai-toolkit Patterns](https://github.com/microsoft/vscode-ai-toolkit)
