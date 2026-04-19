---
name: agentic-workflow-guide
description: "Design, review, and debug agent workflows, and decide when a request should use a prompt, instruction, skill, agent, or hook before escalating to multi-agent design. Use for any .agent.md file work, workflow architecture, orchestration planning, or when agent workflows may be overkill. Triggers on 'agent workflow', 'create agent', 'ワークフロー設計', 'orchestrator'."
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Agentic Workflow Guide

Design, review, and improve agent workflows based on proven principles.

## Primitive First

Do not start with multi-agent by default.

| Need | Best Fit |
| ---- | -------- |
| Single focused slash task | **Prompt** |
| Always-on or file-scoped guidance | **Instruction** |
| Reusable workflow with bundled scripts, references, or templates | **Skill** |
| Persona, tool restrictions, delegation, or handoffs | **Agent** |
| Deterministic enforcement or lifecycle automation | **Hook** |

If the ask does not require an **Agent**, stop and create the simpler primitive.

→ **[references/customization-decision.md](references/customization-decision.md)** for the selection guide

## When to Use

| Action     | Triggers                                                                     |
| ---------- | ---------------------------------------------------------------------------- |
| **Create** | New `.agent.md`, workflow architecture, scaffolding                          |
| **Review** | Orchestrator not delegating, design principle check, context overflow        |
| **Update** | Adding Handoffs, improving delegation, tool configuration                    |
| **Debug**  | Agent not found, subagent not working, picker visibility, access control     |
| **Decide** | Determining whether multi-agent is justified or a simpler primitive is enough |

## Core Principles

→ **[references/design-principles.md](references/design-principles.md)**

| Tier          | Principles                                              |
| ------------- | ------------------------------------------------------- |
| **Essential** | SSOT, SRP, Simplicity First, Fail Fast, Feedback Loop   |
| **Quality**   | Transparency, Gate/Checkpoint, DRY, Observability       |
| **Scale**     | Human-in-the-Loop, Loose Coupling, Graceful Degradation |

> See [design-principles.md > Simplicity First](references/design-principles.md#3-simplicity-first) for Anthropic's key recommendation.

## Workflow Patterns

→ **[references/workflow-patterns/overview.md](references/workflow-patterns/overview.md)**

| Pattern                  | When to Use                       |
| ------------------------ | --------------------------------- |
| **Prompt Chaining**      | Sequential tasks with validation  |
| **Routing**              | Processing varies by input type   |
| **Parallelization**      | Independent tasks run together    |
| **Orchestrator-Workers** | Dynamic task decomposition        |
| **Evaluator-Optimizer**  | Repeat until quality criteria met |

**Stop Conditions (MANDATORY):** Define success/failure criteria and exit conditions for every loop.

## Design Workflow

0. **Extract from Conversation** - Generalize repeated behavior, tool preferences, and workflow shape before asking questions
1. **Primitive + Scope** - Choose prompt / instruction / skill / agent / hook, and decide workspace vs profile
2. **Clarify Only the Gaps** - Ask only for the missing ambiguity that materially changes behavior
3. **Escalation Check** - Confirm why agent or multi-agent is needed
4. **Pattern Selection** - Ask user to confirm the chosen pattern when it changes complexity materially
5. **Design Diagram** - Visualize with Mermaid when it clarifies roles or handoffs
6. **Principle Check** - Validate against review checklist
7. **Implement & Iterate** - Draft → identify weak spots → refine → propose adjacent customizations

## When to Escalate

→ **[references/splitting-criteria.md](references/splitting-criteria.md)**

| Level  | Configuration         | Escalation Triggers                      |
| ------ | --------------------- | ---------------------------------------- |
| **L0** | Single Prompt         | Retry 3+, unstable output                |
| **L1** | Prompt + Instructions | Steps > 5, "missed/overlooked" errors    |
| **L2** | Single Agent          | Multiple responsibilities, context > 70% |
| **L3** | Multi-Agent           | Independent subtasks needed              |

**Rule:** Prefer the lowest level that solves the problem cleanly.

**Quick Check:** Prompt > 50 lines? Steps > 5? SRP violation? Context > 70%? → Consider splitting.

## Review Checklist

→ **[references/review-checklist.md](references/review-checklist.md)**

- [ ] Single responsibility per agent? (SRP)
- [ ] Errors detected immediately? (Fail Fast)
- [ ] Small iterative steps? (Iterative)
- [ ] Results verifiable at each step? (Feedback Loop)

## Key References

| Topic              | Reference                                                              |
| ------------------ | ---------------------------------------------------------------------- |
| Primitive Decision | [references/customization-decision.md](references/customization-decision.md) |
| Built-in Patterns  | [references/builtin-customization-patterns.md](references/builtin-customization-patterns.md) |
| Prompt Template    | [references/prompt-template.md](references/prompt-template.md)         |
| agent              | [references/agent-guide.md](references/agent-guide.md)                 |
| Agent Template     | [references/agent-template.md](references/agent-template.md)           |
| Hooks              | [references/hooks-guide.md](references/hooks-guide.md)                 |
| **Agent Placement**| [references/vscode-agent-placement.md](references/vscode-agent-placement.md) |
| Context Management | [references/context-engineering.md](references/context-engineering.md) |
| **Handoffs**       | [references/handoffs-guide.md](references/handoffs-guide.md)           |
| Scaffold Tool      | [references/scaffold-usage.md](references/scaffold-usage.md)           |
| **Deep Agent**     | [references/deep-agent-patterns.md](references/deep-agent-patterns.md) |
| Agent Evaluation   | [references/agent-evaluation.md](references/agent-evaluation.md)       |

## agent Quick Fix

**Problem:** Orchestrator says "I'll delegate" but does work directly.

**Solution:** Use MUST/MANDATORY language. See [agent-guide.md](references/agent-guide.md).

```yaml
## MANDATORY: Sub-agent Delegation
You MUST use agent for each file. Do NOT read files directly.
```

## Tools Reference

→ **[references/agent-template.md](references/agent-template.md#available-tools)**

| Purpose   | VS Code Copilot          | Claude Code |
| --------- | ------------------------ | ----------- |
| Shell     | `execute/runInTerminal`  | `Bash`      |
| Read      | `read/readFile`          | `Read`      |
| Edit      | `edit/editFiles`         | `Write`     |
| Subagent  | `agent`                  | `Task`      |
| Web fetch | `web/fetch`              | (MCP)       |

## External References

### Official Documentation

- [Chat in IDE - GitHub Docs](https://docs.github.com/en/copilot/how-tos/chat-with-copilot/chat-in-ide)
- [Custom Agents - VS Code Docs](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Custom Agents - GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [Custom Agents Configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

### Design Principles

- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Effective Context Engineering - Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Writing Tools for Agents - Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Context windows - Anthropic](https://platform.claude.com/docs/en/docs/build-with-claude/context-windows)

### Instructions & Context

- [Adding repository custom instructions - GitHub Docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)

### Community Resources

- [agent (旧 runSubagent) 検証記事 - Zenn](https://zenn.dev/openjny/articles/2619050ec7f167)
- [subagent-driven-development - obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development)
- [awesome-copilot agents - GitHub](https://github.com/github/awesome-copilot/tree/main/agents)

### Prompt Engineering

- https://platform.openai.com/docs/guides/prompt-engineering
- https://code.claude.com/docs/en/best-practices
- https://www.promptingguide.ai/
- https://www.ibm.com/think/prompt-engineering

## Done Criteria

- [ ] Primitive and scope selected intentionally
- [ ] Workflow pattern selected and confirmed with user
- [ ] `.agent.md` file created with clear Role/Workflow/Done Criteria
- [ ] Design principles checklist passed
- [ ] Agent registered in AGENTS.md (if applicable)
