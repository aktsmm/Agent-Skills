# Handoffs Guide

Guided sequential workflows with human-in-the-loop control between agents.

## Table of Contents

- [What are Handoffs?](#what-are-handoffs) - Purpose and concept
- [When to Use](#when-to-use) - Effective scenarios
- [Configuration](#configuration) - YAML properties and examples
- [Workflow Examples](#workflow-examples) - Common patterns
- [Handoffs vs agent](#handoffs-vs-agent) - Comparison and selection
- [Best Practices](#best-practices) - Tips for effective handoffs
- [Troubleshooting](#troubleshooting) - Common issues

> **Spec source:** [Custom agents - Handoffs](https://code.visualstudio.com/docs/agent-customization/custom-agents#_handoffs) (verified 2026-10)

---

## What are Handoffs?

Handoffs enable **guided sequential workflows** that transition between agents with suggested next steps. After a chat response completes, **handoff buttons** appear that let users move to the next agent with relevant context and a pre-filled prompt.

### Key Characteristics

| Aspect              | Description                                    |
| ------------------- | ---------------------------------------------- |
| **User Control**    | Human approves each transition (button click)  |
| **Context Passing** | Conversation context + pre-filled prompt       |
| **Visibility**      | User can review/edit prompt before submitting  |
| **Auto-submit**     | Optional: `send: true` for automatic execution |

### Visual Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Plan Agent    │     │ Implementation   │     │  Review Agent   │
│                 │     │     Agent        │     │                 │
│  📋 Generate    │ ──► │  🔨 Execute      │ ──► │  ✅ Verify      │
│     plan        │     │     code changes │     │     quality     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   [Start Implementation]  [Start Review]          [Done]
        button                button
```

---

## When to Use

### ✅ Effective Scenarios

| Scenario                      | Example                             |
| ----------------------------- | ----------------------------------- |
| **Plan → Implement → Review** | TDD workflow, feature development   |
| **Research → Write**          | Gather info, then produce document  |
| **Analyze → Fix**             | Identify issues, then apply fixes   |
| **Write Tests → Implement**   | TDD: failing tests first, then code |
| **Draft → Edit → Publish**    | Content creation workflow           |

### ❌ When NOT to Use

| Scenario                   | Use Instead                 |
| -------------------------- | --------------------------- |
| Automated background tasks | `agent` (no human approval) |
| Parallel processing        | Parallelization pattern     |
| Context isolation needed   | `agent` (clean context)     |
| Simple single-step tasks   | Single agent                |

---

## Configuration

### YAML Syntax

```yaml
---
name: <agent-name>
description: <description>
tools: [...]
handoffs:
  - label: <button-text>
    agent: <target-agent-name>
    prompt: <pre-filled-prompt>
    send: <true|false>
    model: <Model Name (vendor)>
---
```

### Properties

| Property | Required | Type    | Description                                                                       |
| -------- | -------- | ------- | --------------------------------------------------------------------------------- |
| `label`  | ✅       | string  | Button text displayed to user                                                     |
| `agent`  | ✅       | string  | Target agent identifier (the target's `name`; file name if `name` is omitted)     |
| `prompt` | ❌       | string  | Pre-filled prompt for target agent                                                |
| `send`   | ❌       | boolean | Auto-submit prompt (default: `false`)                                             |
| `model`  | ❌       | string  | Model for the handoff, qualified as `Model Name (vendor)`, e.g. `GPT-5 (copilot)` |

### Complete Example

```yaml
---
name: Planner
description: Generate implementation plans for features
tools: ['search', 'web/fetch', 'read']
handoffs:
  - label: Start Implementation
    agent: implementer
    prompt: |
      Implement the plan outlined above.
      Follow the step-by-step instructions.
    send: false
  - label: Request Review
    agent: reviewer
    prompt: Review the plan for completeness.
    send: false
---

# Planner Agent

## Role

Generate detailed implementation plans for new features.

## Goals

- Analyze requirements
- Break down into actionable steps
- Define acceptance criteria

## Done Criteria

- [ ] Plan document created
- [ ] Steps are specific and actionable
- [ ] Acceptance criteria defined

## Workflow

1. Analyze the feature request
2. Research existing codebase patterns
3. Create step-by-step implementation plan
4. Define test cases and acceptance criteria
```

---

## Workflow Examples

### Example 1: TDD Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Test Writer    │ ──► │   Implementer    │ ──► │    Reviewer     │
│                 │     │                  │     │                 │
│ Write failing   │     │ Make tests pass  │     │ Check quality   │
│ tests first     │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

**test-writer.agent.md:**

```yaml
---
name: test-writer
description: Write failing tests first (TDD)
tools: ["read", "edit/editFiles", "execute/runInTerminal"]
handoffs:
  - label: Make Tests Pass
    agent: implementer
    prompt: Implement the code to make the failing tests pass.
    send: false
---
```

**implementer.agent.md:**

```yaml
---
name: implementer
description: Implement code to pass tests
tools: ["read", "edit/editFiles", "execute/runInTerminal"]
handoffs:
  - label: Request Code Review
    agent: reviewer
    prompt: Review the implementation for quality and best practices.
    send: false
---
```

### Example 2: Research → Document

```yaml
---
name: researcher
description: Research a topic thoroughly
tools: ["web/fetch", "search", "read"]
handoffs:
  - label: Write Document
    agent: writer
    prompt: |
      Based on the research above, write a comprehensive document.
      Include all key findings and recommendations.
    send: false
---
```

### Example 3: Multi-Path Handoffs

Single agent with multiple possible next steps:

```yaml
---
name: analyzer
description: Analyze issues and suggest next steps
tools: ["read", "search", "read/problems"]
handoffs:
  - label: Fix Issues
    agent: fixer
    prompt: Fix the issues identified above.
    send: false
  - label: Create PR
    agent: pr-creator
    prompt: Create a PR with the analysis summary.
    send: false
  - label: Get More Info
    agent: researcher
    prompt: Research the root cause of these issues.
    send: false
---
```

---

## Handoffs vs agent

| Feature          | Handoffs               | agent                                  |
| ---------------- | ---------------------- | -------------------------------------- |
| **Execution**    | User clicks button     | Automatic                              |
| **Context**      | Conversation + prompt  | Isolated (clean window)                |
| **User Control** | ✅ Human-in-the-loop   | ❌ Automatic                           |
| **Visibility**   | User sees/edits prompt | Results only                           |
| **Use Case**     | Phase transitions      | Context-heavy tasks                    |
| **Nesting**      | ✅ Sequential chain    | ⚠️ Off by default (setting, depth ≤ 5) |

### Decision Matrix

| Need                               | Use Handoffs | Use agent |
| ---------------------------------- | ------------ | --------- |
| Human approval between phases      | ✅           |           |
| Automatic execution                |              | ✅        |
| Context isolation                  |              | ✅        |
| Sequential workflow orchestration  | ✅           |           |
| Log/data analysis (large data)     |              | ✅        |
| Plan → Implement → Review workflow | ✅           |           |
| Research during implementation     |              | ✅        |

---

## Best Practices

### 1. Clear Prompt Context

❌ Bad:

```yaml
handoffs:
  - label: Next
    agent: implementer
    prompt: Continue.
```

✅ Good:

```yaml
handoffs:
  - label: Start Implementation
    agent: implementer
    prompt: |
      Implement the plan outlined above.
      Follow these steps:
      1. Create the new file structure
      2. Implement core logic
      3. Add tests for each function
```

### 2. Descriptive Labels

❌ Bad: `label: Next`, `label: Go`

✅ Good: `label: Start Implementation`, `label: Request Code Review`

### 3. Use `send: false` by Default

Let users review and modify prompts before submitting. Use `send: true` only for well-tested, predictable workflows.

### 4. Define Clear Phase Boundaries

Each agent should have distinct responsibility:

- **Planner**: Creates plan only, no implementation
- **Implementer**: Executes plan, no review
- **Reviewer**: Reviews only, no fixing

### 5. Include Context References

Reference what was done in current phase:

```yaml
prompt: |
  Review the implementation above.
  Focus on:
  - Adherence to the original plan
  - Code quality and best practices
  - Test coverage
```

---

## Troubleshooting

### Handoff Button Not Appearing

**Causes:**

1. `handoffs` not in YAML frontmatter
2. Target agent not discovered (wrong location or load error; check Chat view > right-click > Diagnostics)
3. Old VS Code version

**Solution:**

```powershell
code --version
Test-Path .github/agents/implementer.agent.md
```

### Wrong Agent Invoked

**Cause:** Agent name mismatch

**Solution:** Ensure `agent:` matches the target's `name` (or its file name when `name` is omitted):

```
File: .github/agents/implementer.agent.md (no name field)
Agent name in handoffs: agent: implementer  ✅
```

### Prompt Too Long

**Cause:** Large prompt causes UI issues

**Solution:** Keep prompts concise; reference previous output instead of duplicating:

```yaml
prompt: |
  Implement based on the plan above.
  See the requirements in the previous response.
```

---

## References

- [Custom Agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents#_handoffs)
- [Custom Agents Configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [agent Guide](agent-guide.md) - Alternative for context isolation
- [Workflow Patterns Overview](workflow-patterns/overview.md) - Pattern selection guide

---

## Context-Based Handoff (No agent tool)

Not all agent-to-agent communication uses `agent`. Some patterns use **chat context** for data passing.

### When to Use Context-Based Handoff

| Scenario                | Method          | Reason                                        |
| ----------------------- | --------------- | --------------------------------------------- |
| Router → Orchestrator   | Chat context    | Router makes decisions, doesn't spawn workers |
| Same-level coordination | Chat context    | Agents share conversation, not parent-child   |
| Decision passing        | JSON in context | Structured data without sub-agent overhead    |

### Implementation Pattern

```markdown
## Router Agent (Decision Maker)

- Makes routing decision
- Outputs RouterDecision JSON to chat context
- Does NOT use agent

## Orchestrator Agent (Executor)

- Receives RouterDecision from chat context (NOT as agent input)
- Uses agent for actual worker delegation
- Logs decision to .logs/ for traceability
```

### RouterDecision JSON Example

```json
{
  "flow": "full_ir",
  "normalized_question": "...",
  "manifest": { "applied": true, "name": "..." },
  "decision_reason": "...",
  "timestamp": "ISO8601"
}
```

### Key Distinction

| Handoff Type  | Tool Used    | Parent-Child? | Use Case                       |
| ------------- | ------------ | ------------- | ------------------------------ |
| agent         | agent / Task | Yes           | Worker delegation              |
| Context-based | None (chat)  | No            | Decision passing, coordination |
