# Agent & Prompt Template

Standard structure and specification for `.agent.md` and `.prompt.md` files.

## Table of Contents

- [YAML Front Matter](#yaml-front-matter) - Agent/prompt metadata configuration
- [Agent Body Structure](#agent-body-structure) - Required and recommended sections
- [Full Template](#full-template) - Complete agent example
- [Design Principles](#design-principles-for-agents) - Stateless, SRP, Observability
- [Examples by Role](#examples-by-role) - Orchestrator, Specialist, Implementation
- [Available Tools](#available-tools) - VS Code Copilot / Claude Code tool mapping
- [Handoffs](#handoffs-agent-transitions) - Agent transitions configuration

> **Note**: Both file types use similar YAML front matter. The `mode:` field is deprecated for both.

## YAML Front Matter

### For `.agent.md` files

```yaml
---
name: <agent-name> # Required: Identifier for @mention
description: <description> # Required: One-line role description
model: <model-name> # Optional: LLM model to use (e.g., "Claude Sonnet 4")
tools: [...] # Optional: Tool whitelist
handoffs: [...] # Optional: Agent transitions
target: <vscode|github-copilot> # Optional: Target environment
infer: <true|false> # Optional: Allow as subagent (default: true)
argument-hint: <hint-text> # Optional: Input field placeholder
---
```

### YAML Properties Reference (VS Code 1.106+)

| Property        | Required | Type     | Description                                                         |
| --------------- | -------- | -------- | ------------------------------------------------------------------- |
| `name`          | ✅       | string   | Agent identifier for @mention                                       |
| `description`   | ✅       | string   | Brief description (shown as placeholder in chat)                    |
| `tools`         | ❌       | string[] | Tool whitelist (omit for all tools)                                 |
| `model`         | ❌       | string   | AI model to use (e.g., `Claude Sonnet 4`, `GPT-4o`)                 |
| `handoffs`      | ❌       | object[] | Agent transition buttons (→ [handoffs-guide.md](handoffs-guide.md)) |
| `target`        | ❌       | string   | `vscode` or `github-copilot` (default: both)                        |
| `infer`         | ❌       | boolean  | Allow as subagent target (default: `true`)                          |
| `argument-hint` | ❌       | string   | Hint text in chat input field                                       |
| `mcp-servers`   | ❌       | object[] | MCP server config (org/enterprise agents only)                      |

### For `.prompt.md` files

```yaml
---
description: <description> # Required: Brief description of the prompt
---
```

### ⚠️ Deprecated Fields

| Field   | Status        | Applies To                | Use Instead                    |
| ------- | ------------- | ------------------------- | ------------------------------ |
| `mode:` | ❌ Deprecated | `.agent.md`, `.prompt.md` | Use `agent:` field (see below) |

**`mode:` Migration Guide:**

```yaml
# ❌ Wrong (deprecated)
---
mode: agent
---
# ✅ Correct: Specify agent name
---
description: Daily report generator
agent: report-generator
---
# ✅ Correct: Boolean value
---
description: Daily report generator
agent: true
---
# ✅ Correct: Omit (default behavior)
---
description: Daily report generator
---
```

**`agent:` Field Options:**

| Value           | Behavior                                      |
| --------------- | --------------------------------------------- |
| `agent: <name>` | Use specific agent (e.g., `report-generator`) |
| `agent: true`   | Enable agent mode                             |
| _(omit field)_  | Default behavior                              |

### Complete `.prompt.md` Example

```yaml
---
description: デイリーレポート自動生成（業務ログから1日分のレポートを作成）
agent: report-generator
tools:
  [
    "read/readFile",
    "edit/editFiles",
    "search/fileSearch",
    "search/textSearch",
    "workiq/*",
  ]
---
```

**Tools Pattern Reference:**

| Pattern           | Description                | Example                                   |
| ----------------- | -------------------------- | ----------------------------------------- |
| `category`        | Category alias (all tools) | `read`, `edit`, `search`, `execute`       |
| `category/tool`   | Specific tool              | `read/readFile`, `execute/runInTerminal`  |
| `mcp-server/*`    | All MCP server tools       | `bicep/*`, `github/*`                     |
| `mcp-server/tool` | Specific MCP tool          | `github/search_code`                      |
| Mixed             | Combine any patterns       | `['execute', 'read/readFile', 'bicep/*']` |

**Tool Aliases (VS Code Copilot):**

| Alias     | Included Tools                         | Description        |
| --------- | -------------------------------------- | ------------------ |
| `execute` | shell, Bash, powershell, runInTerminal | シェル実行         |
| `read`    | readFile, NotebookRead                 | ファイル読み取り   |
| `edit`    | editFiles, MultiEdit, Write            | ファイル編集       |
| `search`  | fileSearch, textSearch, Grep, Glob     | 検索               |
| `agent`   | runSubagent, custom-agent, Task        | サブエージェント   |
| `web`     | WebSearch, WebFetch, fetch             | Web 取得           |
| `todo`    | manage_todo_list, TodoWrite            | タスクリスト       |
| `vscode`  | VS Code specific tools                 | VS Code 固有ツール |

> **💡 Tips:**
>
> - エイリアス形式 (`"read"`) とフルパス形式 (`"read/readFile"`) は混在可能
> - 認識されないツール名は**無視される**（エラーにならない）
> - MCP サーバーは `server-name/*` でワイルドカード指定可能

---

# ✅ Correct

---

name: my-agent
description: Does something useful

---

`````

### Tools Field Behavior

| Specification | Behavior                                   |
| ------------- | ------------------------------------------ |
| **Omitted**   | All tools available (recommended for most) |
| `tools: ["*"]`| All tools available (explicit)             |
| `tools: []`   | No tools available                         |
| Tool names    | Only listed tools available (whitelist)    |

> **Note**: MCP server tools become available at runtime automatically. Unknown tool names are **ignored** (not errors).

## Agent Body Structure

Each agent should include these sections:

| Section                | Required    | Description                                           |
| ---------------------- | ----------- | ----------------------------------------------------- |
| **Role**               | ✅          | Single sentence defining responsibility               |
| **Goals**              | ✅          | List of objectives to achieve                         |
| **Done Criteria**      | ✅          | Verifiable completion conditions (**one place only**) |
| **Permissions**        | ✅          | What's allowed and forbidden                          |
| **I/O Contract**       | ✅          | Input/output definitions                              |
| **When to Use**    | Recommended | Trigger conditions for agent selection               |
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
# VS Code Copilot tools (adjust for Claude Code: Read, Edit, Search)
tools: ["read/readFile", "edit/editFiles", "search/textSearch"]
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

## When to Use

Define trigger conditions for when this agent should be selected:

- User reports specific keywords (e.g., "fix", "broken", "doesn't work")
- Specific task type is requested
- Context matches agent's expertise

> **Why When to Use?** Improves agent selection accuracy in multi-agent systems.

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


  ### Phase Skip Conditions (Optional)

  Define conditions to skip phases when context is already clear:

  > **Skip Conditions**: Proceed directly to next phase if ALL of the following are met:
  > - User provided specific operation and problem description
  > - Expected behavior is clear or explicitly stated  
  > - Error messages or screenshots are provided

  ### Steps
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
`````

```

## Idempotency

- Check current state before making changes
- Use unique identifiers to prevent duplicates
- Design operations to be safely retried

```

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

→ **Full Example**: See [examples/orchestrator.agent.md](examples/orchestrator.agent.md) for complete definition.

**Quick Reference (YAML front matter only):**

| Platform        | tools                                                      |
| --------------- | ---------------------------------------------------------- |
| VS Code Copilot | `["agent", "read/readFile", "search/textSearch", "todos"]` |
| Claude Code     | `["Task", "Read", "Search", "TodoWrite"]`                  |

Key characteristics:

- Uses subagent tool for delegation (`#runSubagent` / `Task`)
- Maintains high-level view
- Does NOT perform detailed work itself

### Specialist Agent

**VS Code Copilot:**

```yaml
---
name: code-reviewer
description: Reviews code for quality, security, and best practices
tools: ["read/readFile", "search/textSearch", "fetch"]
---
```

Key characteristics:

- Focused expertise
- Clear input/output contract
- Deterministic behavior where possible

### Implementation Agent

**VS Code Copilot:**

```yaml
---
name: implementer
description: Implements code changes based on specifications
tools: ["read/readFile", "edit/editFiles", "runInTerminal", "search/textSearch"]
---
```

Key characteristics:

- Receives clear specifications
- Makes targeted changes
- Reports results back to orchestrator

## Available Tools

Built-in tools for custom agents. Tool names differ by platform:

### VS Code Copilot Tools (Official)

| Tool Name            | Description                              | Tool Set   |
| -------------------- | ---------------------------------------- | ---------- |
| `#runInTerminal`     | Run shell command in integrated terminal | `#execute` |
| `#read/readFile`     | Read file contents                       | `#read`    |
| `#edit/editFiles`    | Edit/create files                        | `#edit`    |
| `#edit/createFile`   | Create new file                          | `#edit`    |
| `#search/textSearch` | Search text in files                     | `#search`  |
| `#search/fileSearch` | Search files by glob pattern             | `#search`  |
| `#agent`             | Spawn sub-agent with isolated context    | -          |
| `#fetch`             | Fetch web page content                   | `#web`     |
| `#todos`             | Task list management                     | `#todo`    |
| `#codebase`          | Search codebase for context              | -          |
| `#changes`           | List source control changes              | -          |
| `#problems`          | Get workspace issues                     | -          |
| `#usages`            | Find references/implementations          | -          |
| `#githubRepo`        | Search GitHub repository                 | -          |

### Claude Code Tools (Anthropic)

| Tool Name         | Description             |
| ----------------- | ----------------------- |
| `Bash`            | Shell command execution |
| `Read`            | Read file contents      |
| `Write` / `Edit`  | Create/edit files       |
| `Search` / `Grep` | Search files/text       |
| `Task`            | Spawn sub-agent         |
| `TodoWrite`       | Task list management    |
| `WebSearch`       | Web search (via MCP)    |

### Cross-Platform Mapping

| Purpose         | VS Code Copilot                          | Claude Code      |
| --------------- | ---------------------------------------- | ---------------- |
| Shell execution | `runInTerminal`                          | `Bash`           |
| Read file       | `read/readFile`                          | `Read`           |
| Edit file       | `edit/editFiles`                         | `Write`/`Edit`   |
| Search          | `search/textSearch`, `search/fileSearch` | `Search`, `Grep` |
| Subagent        | `agent`                                  | `Task`           |
| Web fetch       | `fetch`                                  | (MCP)            |
| Todo list       | `todo`                                   | `TodoWrite`      |

### Tool Definition Examples

**VS Code Copilot:**

```yaml
---
name: orchestrator
description: Coordinates workflow and delegates to specialist agents
tools: ["agent", "read", "search", "todo"]
---
```

**Claude Code:**

```yaml
---
name: orchestrator
description: Coordinates workflow and delegates to specialist agents
tools: ["Task", "Read", "Search", "TodoWrite"]
---
```

### Tool Reference Syntax

- **VS Code Copilot**: Use `#tool:<tool-name>` in prompts (e.g., `#tool:runSubagent`)
- **Claude Code**: Reference tools directly by name

### MCP Server Tools

Use `<server-name>/*` format to include all tools from an MCP server.

**Troubleshooting**: If tools are not recognized:

- VS Code: Check [VS Code Chat Tools Reference](https://code.visualstudio.com/docs/copilot/reference/copilot-vscode-features#_chat-tools)
- Claude Code: Check [Custom Agents Configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

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
# VS Code Copilot tools
tools: ["search", "web", "read"]
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
- [Handoffs Guide](handoffs-guide.md) - Detailed handoffs configuration
- [runSubagent Guide](agent-guide.md) - Sub-agent delegation

```

```

### ⚠️ Tool Name Format Changes (VS Code 2026+)

Some tool names require full path format. Use the following:

| Tool | Correct Format | Notes |
|------|---------------|-------|
| runInTerminal | `execute/runInTerminal` | Alias `execute` does NOT work |
| problems | `read/problems` | Renamed from `problems` |
| codebase | `search/codebase` | Renamed from `codebase` |
| terminalLastCommand | `read/terminalLastCommand` | Renamed from `terminalLastCommand` |
| runSubagent | `agent` | Alias works |
| todo | `todo` | Alias works |

**Example (correct):**
```yaml
tools:
  - read/readFile
  - edit/editFiles
  - search/textSearch
  - search/fileSearch
  - execute/runInTerminal  # Full path required
  - agent                  # Alias OK
  - todo                   # Alias OK
  - read/problems          # Full path required
```




