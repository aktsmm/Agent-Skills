# Agent & Prompt Template

Standard structure and specification for `.agent.md` and `.prompt.md` files.

> Custom agents were formerly "custom chat modes": rename `.chatmode.md` to `.agent.md`. In `.prompt.md`, `mode:` is deprecated; use `agent:`.

## File Format Rules

### フェンスラッパー禁止

`.agent.md` / `.prompt.md` / `.instructions.md` は素の YAML フロントマター (`---`) で始める（`.instructions.md` はフロントマター省略可）。` ````prompt ` や ` ````chatagent ` のコードフェンスで囲むと VS Code がフロントマターを認識せず、ピッカーに `description` が出ない。`---` より前に余分な文字があっても同様。

## YAML Front Matter

### For `.agent.md` files

Identify the intended harness before selecting fields or model syntax. Shared `.github/agents` storage does not imply shared semantics.

```yaml
---
name: <agent-name> # Optional: defaults to the file name
description: <description> # Required for Copilot
model: <verified-model-identifier> # Optional: string or prioritized array
tools: [...] # Optional: allowlist using this harness's inventory
user-invocable: true
disable-model-invocation: false
target: github-copilot # Editor interpretation only; does not switch the session harness
---
```

| Setting | Local (`target: vscode`) | Copilot / Agent Host (`target: github-copilot`) |
| --- | --- | --- |
| `model` | Verified display name, including vendor where needed | Runtime model ID; exact provider-qualified ID for BYOK |
| `agents` | Allowed subagents; omit / `['*']` = all, `[]` = none | Unsupported; not an enforced allowlist |
| `handoffs`, `argument-hint` | Supported | Unsupported |
| Delegation | `agent` tool set / `agent/runSubagent` | Native `task`; verify exposed tools |

Use model completions for the intended harness, not a scheduler's display name or metadata ID alone. Keep provider/profile identity; do not construct an ID from a friendly name. An ordered `model` array selects the first available entry only when fallback is authorized. Within the chosen family/tier, prefer the newest verified generation.

Check parent defaults, scheduler overrides and child dispatch separately: omitted child `model` is not proof of parent inheritance, and Local cost-tier rules are not a universal Agent Host constraint. Observe effective model and native parent/child linkage before claiming a switch worked; saved YAML and a clean diff prove only configuration. Do not add a no-op paid probe where the first authorized bounded call can supply that evidence.

For Local only, `handoffs` uses objects with `label`, `agent`, `prompt`, `send` and optional `model`. A Local `agents` list requires the `agent` tool and can explicitly allow an agent with `disable-model-invocation: true`. Do not set `target: vscode` merely to hide a Copilot warning or remove an allowlist without assessing the lost restriction.

Source: [VS Code custom agent reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference) (harness compatibility and model preferences); verify against the installed version.

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
| `chat.modeFilesLocations` | ❌ Deprecated | legacy settings | Prefer native agent folders; `chat.agentFilesLocations` remains supported and forwards agents to Agent Host (see [placement](vscode-agent-placement.md)) |

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

Treat authored tool references and runtime registration names as separate inventories. A successful native tool call does not validate that name in frontmatter; use destination-harness completions/inventory, supported aliases, and configured MCP server names. Neither a familiar prefix nor success in another client proves availability.

Body から特定ツールを明示したい場合は `#tool:<name>` 参照を使う。

```markdown
Use #tool:agent for each independent file review.
Use #tool:web when external documentation is required.
```

> **Local worker tools**: Generic subagents inherit the parent's selected tools; named custom workers can override them. An agent-only coordinator can delegate editing to a custom worker. Choose the boundary deliberately and verify effective capabilities; do not infer a universal parent ceiling. See [Pitfall 7](agent-guide.md#pitfall-7-confusing-generic-and-custom-worker-tools-local) and the [official example](https://code.visualstudio.com/docs/agents/run/subagents#_delegate-implementation-to-a-worker).

### Local の tools フィールド

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

**Portable な書き方**: 上表は Local の例であり Copilot の許可リストではない。両 harness で使う資産は対応済みの tool set 別名を優先し、本文は内部 tool 名でなく能力で記述する。MCP は実際の構成名による `<server>/*` を使い、namespace 内の変更系操作にも役割の禁止事項を適用する。警告を消すためだけに `tools: ['*']` へ広げない。

### Migration Verification

- Parse the original and revised YAML without repairing whitespace first; inspect body references as well as frontmatter. Replacing Local handoffs or memory must preserve explicit approval, no-rerun, persistence and user-controlled transition rules.
- Check unknown-tool Hints in the destination editor, not just error counts. If the diagnostic tool omits that severity, validate against the destination inventory and report the UI check as unverified. Report editor schema acceptance and standalone CLI warnings separately; `target` does not make them equivalent.
- Freeze the installed definition before a representative run. Exercise planning-only, approved execution, completed/no-rerun and read-only paths where applicable; verify the exact saved output schema and a subsequent read of the same file. An edited definition invalidates that run's evidence; rerun affected cases, not unchanged agents.

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
# Local generic workers inherit selected tools; named custom workers can override them.
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
- Copilot harness: [VS Code harness compatibility](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility). Copilot cloud agent has a separate [GitHub configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration); `target` is not a cloud-execution switch.

## Handoffs (Agent Transitions)

Local-only `handoffs` enable guided sequential workflows between agents with suggested next steps; these fields are not supported by Copilot.

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
