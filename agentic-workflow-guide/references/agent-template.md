# Agent Template

Standard structure and specification for `.agent.md` files.

## YAML Front Matter

Required fields for agent definition files:

```yaml
---
name: <agent-name> # Required: Identifier for @mention
description: <description> # Required: One-line role description
model: <model-name> # Optional: LLM model to use
tools: [...] # Optional: Tool whitelist
handoffs: [...] # Optional: Agent transitions
---
```

### Tools Field Behavior

| Specification | Behavior                                   |
| ------------- | ------------------------------------------ |
| **Omitted**   | All tools available (recommended for most) |
| `tools: []`   | No tools available                         |
| Tool names    | Only listed tools available (whitelist)    |

> **Note**: MCP server tools become available at runtime automatically. Unknown tool names cause errors.

## Agent Body Structure

Each agent should include these sections:

| Section                | Required    | Description                                           |
| ---------------------- | ----------- | ----------------------------------------------------- |
| **Role**               | ✅          | Single sentence defining responsibility               |
| **Goals**              | ✅          | List of objectives to achieve                         |
| **Done Criteria**      | ✅          | Verifiable completion conditions (**one place only**) |
| **Permissions**        | ✅          | What's allowed and forbidden                          |
| **I/O Contract**       | ✅          | Input/output definitions                              |
| **Non-Goals**          | Recommended | What this agent explicitly does NOT do                |
| **Workflow**           | Recommended | Step-by-step procedure                                |
| **Progress Reporting** | Recommended | How to report progress (e.g., `manage_todo_list`)     |
| **Error Handling**     | Recommended | Error patterns and responses                          |
| **Idempotency**        | Recommended | How to guarantee safe retries                         |

### ⚠️ Critical: Done Criteria Placement

**Define Done Criteria in exactly ONE place.** Multiple definitions cause confusion.

## Full Template

````markdown
---
name: example-agent
description: Brief description of what this agent does
tools: ["read", "edit", "search"]
---

# Example Agent

## Role

[Single sentence defining this agent's responsibility]

## Goals

- Goal 1: [Specific, measurable objective]
- Goal 2: [Another objective]
- Goal 3: [...]

## Done Criteria

Task is complete when ALL of the following are true:

- [ ] Criterion 1 (verifiable condition)
- [ ] Criterion 2 (verifiable condition)
- [ ] Criterion 3 (verifiable condition)

## Permissions

### Allowed

- Action 1
- Action 2

### Forbidden

- ❌ Action that should never be done
- ❌ Another prohibited action

## Non-Goals

Explicitly define what this agent does NOT do:

- ❌ Do not write code directly (delegate to implementation agent)
- ❌ Do not review own output (delegate to review agent)
- ❌ Do not assume user intent (ask for clarification)

> **Why Non-Goals?** Prevents orchestrators from doing work they should delegate.

## I/O Contract

### Input

| Field       | Type   | Required | Description          |
| ----------- | ------ | -------- | -------------------- |
| input_field | string | Yes      | Description of input |

### Output

| Field        | Type   | Description           |
| ------------ | ------ | --------------------- |
| output_field | string | Description of output |

## Workflow

1. **Step 1**: [Action description]
   - Details or sub-steps
2. **Step 2**: [Action description]
3. **Step 3**: [Action description]

## Error Handling

| Error Pattern        | Response                           |
| -------------------- | ---------------------------------- |
| File not found       | Report error, suggest alternatives |
| Invalid input format | Validate early, return clear error |
| External API failure | Retry with backoff, then escalate  |

## Progress Reporting

For long-running tasks, maintain visibility:

- Use `manage_todo_list` tool to track task status
- Update status at each sub-task completion
- Provide intermediate reports for tasks > 5 minutes

```markdown
**Progress:**

- [x] Task 1: Analyze requirements
- [x] Task 2: Generate IR
- [ ] Task 3: Validate output
```
````

## Idempotency

- Check current state before making changes
- Use unique identifiers to prevent duplicates
- Design operations to be safely retried

````

## Design Principles for Agents

### 1. Stateless Design

- Judge based on file system state, not conversation history
- Design workflows to converge to correct state when re-run

### 2. Single Responsibility

- One agent, one goal
- Separate by phase: planning, implementation, review, testing

### 3. Observability

- Record decisions as Issue comments or documents
- For long tasks, include regular status reports

## Examples by Role

### Orchestrator Agent

```yaml
---
name: orchestrator
description: Coordinates workflow and delegates to specialist agents
tools: ["agent", "read", "search", "todo"]
---
````

Key characteristics:

- Uses `#tool:agent` for delegation
- Maintains high-level view
- Does NOT perform detailed work itself

### Specialist Agent

```yaml
---
name: code-reviewer
description: Reviews code for quality, security, and best practices
tools: ["read", "search", "web"]
---
```

Key characteristics:

- Focused expertise
- Clear input/output contract
- Deterministic behavior where possible

### Implementation Agent

```yaml
---
name: implementer
description: Implements code changes based on specifications
tools: ["read", "edit", "execute", "search"]
---
```

Key characteristics:

- Receives clear specifications
- Makes targeted changes
- Reports results back to orchestrator

## Available Tools

Built-in tools for custom agents. Use **Primary Alias** in the `tools:` property.

| Primary Alias       | Compatible Aliases                                | Description                           |
| ------------------- | ------------------------------------------------- | ------------------------------------- |
| `execute`           | `shell`, `Bash`, `powershell`, `run_in_terminal`  | Shell command execution               |
| `read`              | `Read`, `NotebookRead`, `read_file`               | Read file contents                    |
| `edit`              | `Edit`, `MultiEdit`, `Write`, `NotebookEdit`      | Edit/create files                     |
| `search`            | `Grep`, `Glob`, `grep_search`, `file_search`      | Search files/text                     |
| `agent/runSubagent` | `agent`, `custom-agent`, `Task`, `runSubagent`    | Spawn sub-agent (specify `agentName`) |
| `web`               | `WebSearch`, `WebFetch`, `fetch`, `fetch_webpage` | Fetch web content                     |
| `todo`              | `TodoWrite`                                       | Task list management                  |
| `githubRepo`        | -                                                 | Search GitHub repositories            |
| `usages`            | -                                                 | Find code usages/references           |

### Tool Definition Examples

```yaml
# Orchestrator with sub-agent delegation
tools: ["agent/runSubagent", "execute", "read", "search"]

# Code reviewer
tools: ["read", "search", "web", "execute"]

# Translator/Editor
tools: ["read", "edit", "agent"]

# Sub-agent call template (Zenn format)
#tool:agent/runSubagent を使用して、Worker エージェントを呼び出してください。
- prompt: ${task to delegate}
- agentName: Worker
```

### Common Mistakes

⚠️ **Wrong**: Using non-primary aliases in `tools:` property

```yaml
# ❌ Bad - mixes non-primary aliases and omits agentName usage
tools: ["run_in_terminal", "read_file", "runSubagent"]

# ✅ Good - use Primary Alias and runSubagent spec
tools: ["execute", "read", "agent/runSubagent"]
```

**Troubleshooting**: If tools are not recognized, verify against [Custom Agents Configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

**MCP Server Tools**: Use `<server-name>/*` format to include all tools from an MCP server.

**Tool Reference Syntax**: Use `#tool:<tool-name>` in prompts (e.g., `#tool:agent`).

## Handoffs (Agent Transitions)

Handoffs enable guided sequential workflows between agents with suggested next steps.

### When to Use

- **Plan → Implementation**: Generate plan, then hand off to implementation agent
- **Implementation → Review**: Complete coding, then switch to code review agent
- **Write Failing Tests → Pass Tests**: Generate failing tests first, then implement code

### Configuration

```yaml
---
name: Planner
description: Generate an implementation plan
tools: ["search", "fetch", "read_file"]
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Implement the plan outlined above.
    send: false
---
```

| Property | Description                         |
| -------- | ----------------------------------- |
| `label`  | Button text shown to user           |
| `agent`  | Target agent identifier             |
| `prompt` | Pre-filled prompt for next agent    |
| `send`   | Auto-submit prompt (default: false) |

### Benefits

- **Human control**: User reviews each phase before proceeding
- **Context preservation**: Relevant context passed via prompt
- **Workflow orchestration**: Multi-step tasks with clear boundaries

## References

- [Custom Agents in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Custom Agents Configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
