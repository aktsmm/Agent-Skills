# Agent & Prompt Template

Standard structure and specification for `.agent.md` and `.prompt.md` files.

> Custom agents were formerly "custom chat modes": rename `.chatmode.md` to `.agent.md`. In `.prompt.md`, `mode:` is deprecated; use `agent:`.

## File Format Rules

### フェンスラッパー禁止

`.agent.md` / `.prompt.md` / `.instructions.md` は素の YAML フロントマター (`---`) で始める（`.instructions.md` はフロントマター省略可）。` ````prompt ` や ` ````chatagent ` のコードフェンスで囲むと VS Code がフロントマターを認識せず、ピッカーに `description` が出ない。`---` より前に余分な文字があっても同様。

## YAML Front Matter

### For `.agent.md` files

```yaml
---
name: <agent-name> # Optional: defaults to the file name
description: <description> # Recommended: routing surface for pickers and subagent discovery
argument-hint: <hint> # Optional: chat input hint
model: <model-name> # Optional: string or prioritized array
tools: [...] # Optional: tool / tool set allowlist
agents: [...] # Optional: allowed subagents ('*' = all, [] = none)
handoffs: [...] # Optional: objects with label/agent/prompt/send(/model)
user-invocable: true # Optional: show in agents dropdown (default: true)
disable-model-invocation: false # Optional: block subagent invocation (default: false)
target: vscode # Optional: vscode | github-copilot
---
```

> **Model note:** In VS Code, subagents inherit the parent's model unless `.agent.md` sets `model:` or the caller specifies one (highest priority). A requested model cannot exceed the parent's cost tier. Use only exact names verified locally. [VS Code Docs](https://code.visualstudio.com/docs/agents/run/subagents#_select-the-model-for-a-subagent)

When fallback matters, `model:` can be an ordered array and the first available model is used. Use only model display names verified in the current environment.

```yaml
model: ["<verified-model-name-1>", "<verified-model-name-2>"]
```

`handoffs` は文字列配列ではなく、`label`・`agent`・`prompt`・`send` を持つオブジェクト配列で定義する。

`agents` は親 agent が呼び出せる subagent 名の制限。省略または `'*'` で全許可、`[]` で禁止。指定する場合は `tools` に `agent` を含める。親の `agents` に明示した agent は、その agent の `disable-model-invocation: true` を上書きして呼び出せる。

### ⚠️ 非標準フィールド禁止（バリデーションエラーの原因）

`author`, `repository`, `license`, `copyright` 等のメタデータを YAML frontmatter に書くと **バリデーションエラー** になる。
これらは YAML の外、`---` 終端の直後に **HTMLコメント** として記述すること。

```yaml
# ✅ 正しい — メタデータはHTMLコメント
---
name: my-agent
description: Does something useful
---

<!-- author: <your-name>
     repository: https://github.com/<owner>/<repo>
     license: CC BY-NC-SA 4.0
     copyright: Copyright (c) 2025 <your-name> -->

# エージェント本文...
```

```yaml
# ❌ 間違い — YAMLに非標準フィールドを追加
---
author: <your-name>   ← バリデーションエラー
repository: https://...
name: my-agent
---
```

### For `.prompt.md` files

> Prompt files are deprecated for Agent Host sessions (e.g. Copilot) and are not loaded there; they work only with the Local agent, which is planned for removal. Prefer an agent skill for new reusable slash workflows (VS Code offers prompt → skill migration).

```yaml
---
description: <description> # Required: Brief description of the prompt
# agent: <agent-name> # Optional: Bind to a specific agent
---
```

Do not add `tools:` to `.prompt.md` by default. Prompt-level `tools:` is an allowlist that overrides the selected or referenced agent's tools for that prompt run. Use it only when losing unrelated built-in, extension, web, or MCP tools is intentional.

### ⚠️ Deprecated Fields

| Field / setting                                        | Status        | Applies To            | Use Instead                                                                                    |
| ------------------------------------------------------ | ------------- | --------------------- | ---------------------------------------------------------------------------------------------- |
| `mode:`                                                | ❌ Deprecated | `.prompt.md`          | `agent:` (see below)                                                                           |
| `infer:`                                               | ❌ Deprecated | `.agent.md`           | `user-invocable:` and `disable-model-invocation:` (see below)                                  |
| `.chatmode.md`                                         | ❌ Old name   | file                  | Rename to `.agent.md`                                                                          |
| `chat.agentFilesLocations` / `chat.modeFilesLocations` | ❌ Deprecated | settings (Local only) | Move files to supported locations (see [vscode-agent-placement.md](vscode-agent-placement.md)) |

**`infer:` Migration Guide:**

`infer: true` (default) はプルダウン表示とサブエージェント呼び出しの両方を制御していたが、新しいフィールドでは独立制御が可能。

```yaml
# ❌ Wrong (deprecated)
---
infer: false
---
# ✅ Correct: プルダウンに非表示（サブエージェントとしては呼び出し可能）
---
user-invocable: false
---
# ✅ Correct: サブエージェント呼び出しを禁止（プルダウンには表示）
---
disable-model-invocation: true
---
# ✅ Correct: 両方禁止
---
user-invocable: false
disable-model-invocation: true
---
```

> ⚠️ **typo注意**: `user-invokable` は誤記で無効。ピッカー非表示には必ず `user-invocable: false` を使うこと。

> ⚠️ **サブディレクトリの罠（2026-02 実測、公式は「`.github/agents` 内の `.md` を検出」とだけ記載）**: `.github/agents/` は直下のファイルだけを認識し、サブフォルダに置くと `runSubagent` でも呼び出せなかった。非表示にしたい場合はサブフォルダではなく `user-invocable: false` を使う。

### Manifest Validation Checklist

複数の `.agent.md` をまとめて編集したら、最低限次を確認すること。

- `user-invokable` などの誤記が front matter に混入していない
- `user-invocable: false` の agent が意図どおり subagent 専用になっている
- front matter 編集後も本文先頭の `## Role` など必須セクションが崩れていない

**`mode:` Migration Guide (`.prompt.md`):**

```yaml
# ❌ Wrong (deprecated)
---
mode: agent
---
# ✅ Correct: built-in agent or custom agent name
---
description: Daily report generator
agent: report-generator
---
# ✅ Correct: omit to use the current agent
---
description: Daily report generator
---
```

| Value                        | Behavior                                          |
| ---------------------------- | ------------------------------------------------- |
| `agent: ask` / `plan`        | Read-oriented built-in agent                      |
| `agent: agent`               | Built-in Agent (edit / execute)                   |
| `agent: <custom-agent-name>` | Bind to a custom agent (e.g., `report-generator`) |
| _(omit field)_               | Current agent; `agent` if `tools` is set          |

**Tools Pattern Reference:**

| Pattern         | Description                | Example          |
| --------------- | -------------------------- | ---------------- |
| `category/tool` | Specific tool              | `web/fetch`      |
| `category`      | Whole built-in tool set    | `search`, `edit` |
| `<server>/*`    | All tools of an MCP server | `github/*`       |

### Tools Field Behavior

| Specification | Behavior                                   |
| ------------- | ------------------------------------------ |
| **Omitted**   | All tools available (recommended for most) |
| `tools: []`   | No tools available                         |
| Tool names    | Only listed tools available (allowlist)    |

> **Note**: A listed tool that is unavailable at runtime is ignored (official docs), so a typo silently drops the tool instead of failing. Max 128 tools per request.

### Recommended `tools:` style for `.agent.md`

For custom agents, prefer the stable aliases below unless you specifically need a narrower tool path.

```yaml
tools: [read, search]
tools: [read, search, edit]
tools: [agent, read, search]
```

Use these aliases first:

| Purpose  | Preferred alias |
| -------- | --------------- |
| Read     | `read`          |
| Search   | `search`        |
| Edit     | `edit`          |
| Shell    | `execute`       |
| Web      | `web`           |
| Subagent | `agent`         |
| Todo     | `todo`          |

Avoid raw runtime tool IDs in `.agent.md` frontmatter. Names such as `read_file`, `grep_search`, and `semantic_search` are chat/runtime tool identifiers, not portable custom-agent tool names, and they trigger validation errors.

Body から特定ツールを明示したい場合は `#tool:<name>` 参照を使う。

```markdown
Use #tool:agent for each independent file review.
Use #tool:web when external documentation is required.
```

> **⚠️ Orchestrator の tools 制限に注意**: custom agent を指定しない汎用サブエージェントは親の選択済みツールを継承するため、親の `tools:` から `edit` を外すと Writer 等も `edit` を使えないことがある。custom agent の worker は自分の `tools:` を持てるが、親の制限を超えられるかは未検証。Orchestrator の `tools:` は必要な範囲を残し、SRP はプロンプトの指示で担保する。詳細は [agent-guide.md の Pitfall 7](agent-guide.md#pitfall-7-restricting-orchestrators-tools-breaks-sub-agents) を参照。

### ⚠️ tools フィールドの注意事項

**個別ツールは `category/toolName` 形式で指定する。** 旧フラット名やカテゴリ違いは利用不可として黙って無視される。

| ツール             | ✅ 現行 ID                                         | ❌ 旧名・誤り                                                   |
| ------------------ | -------------------------------------------------- | --------------------------------------------------------------- |
| シェル実行         | `execute/runInTerminal`                            | `runInTerminal`, `runCommands`, `terminal`, `run/runInTerminal` |
| ファイル読み       | `read/readFile`                                    | `readFile`                                                      |
| ファイル編集       | `edit/editFiles`                                   | `editFiles`                                                     |
| コード検索         | `search/codebase`                                  | `codebase`                                                      |
| テキスト検索       | `search/textSearch`                                | `textSearch`                                                    |
| 診断 / 変更 / 参照 | `read/problems`, `search/changes`, `search/usages` | `problems`, `changes`, `usages`                                 |
| Web フェッチ       | `web/fetch`                                        | `fetch`                                                         |
| サブエージェント   | `agent`（tool set）/ `agent/runSubagent`           | `runSubagent`                                                   |

`githubRepo` / `githubTextSearch` はカテゴリなしの ID。Local の subagent では todo と `vscode/askQuestions` は使えない。

## Agent Body Structure

### Built-in Aligned Minimal Template

If you do not need the full structured template, start from this smaller built-in aligned shape and expand only when required.

```markdown
---
description: "Use when... trigger phrases for subagent discovery"
tools: [read, search]
user-invocable: false
---

You are a specialist at {specific task}. Your job is to {clear purpose}.

## Constraints

- DO NOT {thing this agent should never do}
- DO NOT {another restriction}
- ONLY {the core responsibility}

## Approach

1. {Step one}
2. {Step two}
3. {Step three}

## Output Format

{Exactly what this agent should return}
```

Use the minimal template when:

- the agent is single-purpose
- tool boundaries matter more than rich documentation
- the return format is more important than a long workflow narrative

Use the full template below when you need explicit I/O contracts, progress reporting, or error handling tables.

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
| **Progress Reporting** | Recommended | How to report progress (e.g., todo list tool)         |
| **Error Handling**     | Recommended | Error patterns and responses                          |
| **Idempotency**        | Recommended | How to guarantee safe retries                         |

### ⚠️ Critical: Done Criteria Placement

**Define Done Criteria in exactly ONE place.** Multiple definitions cause confusion.

## Full Template

```markdown
---
name: example-agent
description: Brief description of what this agent does
tools: [read, edit, search]
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

- Track task status with the todo list tool (not available to Local subagents; return progress in the result instead)
- Update status at each sub-task completion
- Provide intermediate reports for tasks > 5 minutes

## Idempotency

- Check current state before making changes
- Use unique identifiers to prevent duplicates
- Design operations to be safely retried
```

## Examples by Role

→ See [design-principles.md](design-principles.md) for detailed design principles.

### Orchestrator Agent

**VS Code Copilot:**

```yaml
---
name: orchestrator
description: Coordinates workflow and delegates to specialist agents
# Omit tools for orchestrators unless a hard allowlist is intentional.
# Parent tool allowlists become ceilings for worker agents.
---
```

**Claude Code / `.claude/agents/*.md`** (tools is a comma-separated string):

```yaml
---
name: orchestrator
description: Coordinates workflow and delegates to specialist agents
tools: Agent, Read, Grep, Glob, TodoWrite
---
```

Key characteristics:

- Uses subagent tool for delegation (`#tool:agent` / `Agent`)
- Maintains high-level view
- Does NOT perform detailed work itself

## Available Tools

VS Code の現行 tool ID は上の「tools フィールドの注意事項」と [Tools and context reference](https://code.visualstudio.com/docs/agents/reference/tools-reference) を正とする。

### Cross-Platform Mapping

| Purpose         | VS Code Copilot | Claude Code                                        |
| --------------- | --------------- | -------------------------------------------------- |
| Shell execution | `execute`       | `Bash`                                             |
| Read file       | `read`          | `Read`                                             |
| Edit file       | `edit`          | `Write` / `Edit`                                   |
| Search          | `search`        | `Grep` / `Glob`                                    |
| Subagent        | `agent`         | `Agent`（旧 `Task`。v2.1.63 で改名、旧参照も動作） |
| Web             | `web/fetch`     | `WebFetch` / `WebSearch`                           |
| Todo list       | `todo`          | `TodoWrite`                                        |

VS Code は `.claude/agents` の Claude 形式ツール名を対応する VS Code ツールへマッピングする。

### Tool Reference Syntax

- **VS Code Copilot**: Use `#tool:<tool-name>` in the body (e.g., `#tool:web/fetch`)
- **Claude Code**: Reference tools directly by name

### MCP Server Tools

Use `<server-name>/*` format to include all tools from an MCP server.

**Troubleshooting**: If tools or agents are not recognized:

- VS Code: Chat view を右クリック → Diagnostics（読み込まれた agents / prompts / instructions / skills とエラー）、または Agent Debug Logs
- Claude Code: [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- GitHub Copilot cloud agent (`target: github-copilot`): [Custom Agents Configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

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
tools: [search, web, read]
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Implement the plan outlined above.
    send: false
---
```

| Property | Description                                        |
| -------- | -------------------------------------------------- |
| `label`  | Button text shown to user                          |
| `agent`  | Target agent identifier                            |
| `prompt` | Pre-filled prompt for next agent                   |
| `send`   | Auto-submit prompt (default: false)                |
| `model`  | Optional, qualified name such as `GPT-5 (copilot)` |

## References

- [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [Use subagents in VS Code](https://code.visualstudio.com/docs/agents/run/subagents)
- [Custom Agents Configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
