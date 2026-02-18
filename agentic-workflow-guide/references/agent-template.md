# Agent & Prompt Template

Standard structure and specification for `.agent.md` and `.prompt.md` files.

> **Note**: Both file types use similar YAML front matter. The `mode:` field is deprecated for both.

## File Format Rules

### ⚠️ フェンスラッパーに関する重要な注意

`.prompt.md` と `.instructions.md` ファイルは **素の YAML フロントマター (`---`) で始めること**。
コードフェンス（` ````prompt ` 等）で囲む必要はない。フェンスで囲むと VS Code がフロントマターを認識できず、プロンプトピッカーに `description` が表示されなくなる。

| ファイル種別       | 正しい形式                               | 不正な形式               |
| ------------------ | ---------------------------------------- | ------------------------ |
| `.prompt.md`       | `---` で始まる YAML フロントマター       | ` ````prompt ` で囲む    |
| `.instructions.md` | `#` 見出しで始まる（フロントマター不要） | フェンスで囲む           |
| `.agent.md`        | `---` で始まる YAML フロントマター       | ` ````chatagent ` で囲む |

`````yaml
# ✅ .prompt.md — 正しい
---
description: セッション内容をXポスト用に変換
---
# プロンプト本文...

# ❌ .prompt.md — 間違い（description が表示されない）
````prompt
---
description: セッション内容をXポスト用に変換
---
# プロンプト本文...
`````

# ✅ .agent.md — 正しい（フェンス不要、素の `---` だけ）

```yaml
---
name: my-agent
description: Does something useful
---
# エージェント本文...
```

````

## YAML Front Matter

### For `.agent.md` files

```yaml
---
name: <agent-name> # Required: Identifier for @mention
description: <description> # Required: One-line role description
model: <model-name> # Optional: LLM model to use
tools: [...] # Optional: Tool whitelist
handoffs: [...] # Optional: Agent transitions
user-invokable: true # Optional: Show in agents dropdown (default: true)
disable-model-invocation: false # Optional: Prevent subagent invocation (default: false)
---
````

### ⚠️ 非標準フィールド禁止（バリデーションエラーの原因）

`author`, `repository`, `license`, `copyright` 等のメタデータを YAML frontmatter に書くと **バリデーションエラー** になる。
これらは YAML の外、`---` 終端の直後に **HTMLコメント** として記述すること。

```yaml
# ✅ 正しい — メタデータはHTMLコメント
---
name: my-agent
description: Does something useful
---

<!-- author: aktsmm
     repository: https://github.com/aktsmm/ghc_template
     license: CC BY-NC-SA 4.0
     copyright: Copyright (c) 2025 aktsmm -->

# エージェント本文...
```

```yaml
# ❌ 間違い — YAMLに非標準フィールドを追加
---
author: aktsmm        ← バリデーションエラー
repository: https://...
name: my-agent
---
```

### For `.prompt.md` files

```yaml
---
description: <description> # Required: Brief description of the prompt
---
```

### ⚠️ Deprecated Fields

| Field    | Status        | Applies To                | Use Instead                                                       |
| -------- | ------------- | ------------------------- | ----------------------------------------------------------------- |
| `mode:`  | ❌ Deprecated | `.agent.md`, `.prompt.md` | Use `agent:` field (see below)                                    |
| `infer:` | ❌ Deprecated | `.agent.md`               | Use `user-invokable:` and `disable-model-invocation:` (see below) |

**`infer:` Migration Guide:**

`infer: true` (default) はプルダウン表示とサブエージェント呼び出しの両方を制御していたが、新しいフィールドでは独立制御が可能。

```yaml
# ❌ Wrong (deprecated)
---
infer: false
---
# ✅ Correct: プルダウンに非表示（サブエージェントとしては呼び出し可能）
---
user-invokable: false
---
# ✅ Correct: サブエージェント呼び出しを禁止（プルダウンには表示）
---
disable-model-invocation: true
---
# ✅ Correct: 両方禁止
---
user-invokable: false
disable-model-invocation: true
---
```

| フィールド                 | デフォルト | 説明                                         |
| -------------------------- | ---------- | -------------------------------------------- |
| `user-invokable`           | `true`     | プルダウンに表示するか                       |
| `disable-model-invocation` | `false`    | サブエージェントとしての呼び出しを禁止するか |

> ⚠️ **サブディレクトリの罠（2026年2月時点）**: `.github/agents/` は**直下のファイルだけをスキャン**。
> サブフォルダに入れると `runSubagent` でも呼び出せなくなる。フラットに置くこと。
> 非表示にしたい場合はサブフォルダではなく `user-invokable: false` を使うこと。

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

| Pattern         | Description               | Example                |
| --------------- | ------------------------- | ---------------------- |
| `category/tool` | Specific tool             | `read/readFile`        |
| `category/*`    | All tools in category     | `workiq/*`             |
| MCP tools       | External MCP server tools | `workiq/*`, `github/*` |

**Common Tool Categories:**

| Category | Tools                                     |
| -------- | ----------------------------------------- |
| `read`   | `readFile`                                |
| `edit`   | `editFiles`                               |
| `search` | `fileSearch`, `textSearch`                |
| `workiq` | M365 integration (email, calendar, files) |

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
| `tools: []`   | No tools available                         |
| Tool names    | Only listed tools available (whitelist)    |

> **Note**: MCP server tools become available at runtime automatically. Unknown tool names cause errors.

### ⚠️ tools フィールドの注意事項

**ツール名は `category/toolName` 形式で指定すること。** カテゴリが間違っていると VS Code がエラーを出す。

| ツール | ✅ 正しい指定 | ❌ 間違い | 備考 |
|--------|------------|---------|------|
| シェル実行 | `execute/runInTerminal` | `run/runInTerminal` | カテゴリは `execute` |
| ファイル読み | `read/readFile` | `readFile` | カテゴリ必須 |
| ファイル編集 | `edit/editFiles` | `editFiles` | カテゴリ必須 |
| テキスト検索 | `search/textSearch` | `textSearch` | カテゴリ必須 |
| ファイル検索 | `search/fileSearch` | `fileSearch` | カテゴリ必須 |
| Web フェッチ | `web/fetch` | `fetch` | カテゴリ必須 |
| サブエージェント | `agent` | `runSubagent` | カテゴリなし |
| タスク管理 | `todo` | `todos` | カテゴリなし |

**`tools:` に登録できないもの（チャット変数としてのみ利用可）:**
- `problems` / `changes` / `usages` / `codebase` / `githubRepo` → `#problems` 等でチャット内参照は可能だが、`tools:` ホワイトリストには登録不可

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
# VS Code Copilot tools (adjust for Claude Code: Read, Edit, Search)
tools: ["readFile", "editFiles", "textSearch"]
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
`````

```

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
tools: ["runSubagent", "readFile", "textSearch", "todos"]
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

Key characteristics:

- Uses subagent tool for delegation (`#tool:agent` / `Task`)
- Maintains high-level view
- Does NOT perform detailed work itself

## Available Tools

Built-in tools for custom agents. Tool names differ by platform:

### VS Code Copilot Tools (Official)

| Tool Name        | Description                              | Tool Set       |
| ---------------- | ---------------------------------------- | -------------- |
| `#runInTerminal` | Run shell command in integrated terminal | `#runCommands` |
| `#readFile`      | Read file contents                       | -              |
| `#editFiles`     | Edit/create files                        | `#edit`        |
| `#createFile`    | Create new file                          | `#edit`        |
| `#textSearch`    | Search text in files                     | `#search`      |
| `#fileSearch`    | Search files by glob pattern             | `#search`      |
| `#runSubagent`   | Spawn sub-agent with isolated context    | -              |
| `#web/fetch`     | Fetch web page content                   | `#web`         |
| `#todos`         | Task list management                     | -              |
| `#codebase`      | Search codebase for context              | -              |
| `#changes`       | List source control changes              | -              |
| `#problems`      | Get workspace issues                     | -              |
| `#usages`        | Find references/implementations          | -              |
| `#githubRepo`    | Search GitHub repository                 | -              |

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

| Purpose         | VS Code Copilot            | Claude Code      |
| --------------- | -------------------------- | ---------------- |
| Shell execution | `runInTerminal`            | `Bash`           |
| Read file       | `readFile`                 | `Read`           |
| Edit file       | `editFiles`                | `Write`/`Edit`   |
| Search          | `textSearch`, `fileSearch` | `Search`, `Grep` |
| Subagent        | `runSubagent`              | `Task`           |
| Web fetch       | `web/fetch`                | (MCP)            |
| Todo list       | `todos`                    | `TodoWrite`      |

### Tool Definition Examples

**VS Code Copilot:**

```yaml
---
name: orchestrator
description: Coordinates workflow and delegates to specialist agents
tools: ["runSubagent", "readFile", "textSearch", "todos"]
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
tools: ["textSearch", "web/fetch", "readFile"]
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

```

```
