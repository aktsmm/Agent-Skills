# Agent (Sub-agent) Guide

Practical guide for using subagent tools in VS Code Copilot and Claude Code.

## Table of Contents

- [What is agent?](#what-is-agent) - Key characteristics and purpose
- [When to Use](#when-to-use) - Effective scenarios and anti-patterns
- [How to Invoke](#how-to-invoke) - Enabling and invocation methods
- [Prompt Engineering](#prompt-engineering-for-agent) - Sub-agent prompt requirements
- [Orchestrator-Workers Pattern](#orchestrator-workers-pattern-with-agent) - Architecture examples
- [Common Pitfalls](#common-pitfalls) - Avoiding delegation failures
- [Token Efficiency](#token-efficiency) - Trade-offs and recommendations
- [Handoffs vs agent](#handoffs-vs-agent) - Comparison
- [Checklist](#checklist) - Implementation checklist

> **Platform Note (2026/10 verified)**:
>
> - **VS Code Copilot (Local harness)**: Put the `agent` tool set in `tools:` (individual tool id: `agent/runSubagent`) and reference it as `#tool:agent` in the body
> - **Claude Code**: Use `Task` in `tools:`
> - Do not write the old flat name `tools: ["runSubagent"]` in new docs

## What is agent?

The `agent` tool launches an independent agent with a **clean context window** to handle complex, multi-step tasks autonomously.

### Key Characteristics

| Aspect        | Description                                                                           |
| ------------- | ------------------------------------------------------------------------------------- |
| **Context**   | Each sub-agent has its own context window (isolated from main)                        |
| **Execution** | Synchronous - main agent waits for result (NOT async/background)                      |
| **Stateless** | One-shot execution - no follow-up conversation possible                               |
| **Return**    | Only final summary returns to main agent                                              |
| **Parallel**  | ✅ Supported (2026/01+) - multiple sub-agents can run in parallel                     |
| **Nesting**   | ⚠️ Off by default (see [Pitfall 3](#pitfall-3-nested-sub-agent-calls-off-by-default)) |

### Primary Purpose

> "agent is for **context management**, NOT for speed optimization."

Use when you want to:

- Keep main session context **clean** (avoid context rot)
- Isolate detailed exploration from synthesis
- Process large data without polluting main context

---

## When to Use

→ See also **[splitting-criteria.md](splitting-criteria.md)** for the complete escalation ladder and quantitative thresholds.

### ✅ Effective Scenarios

| Scenario                    | Example                                                |
| --------------------------- | ------------------------------------------------------ |
| **Research mid-session**    | "Investigate this library's API" during implementation |
| **Log/data analysis**       | Parse thousands of log lines, return only conclusions  |
| **File-by-file operations** | Fix ESLint errors in each file independently           |
| **Phase-based workflows**   | Plan → Implement → Review (each phase = sub-agent)     |

When a workflow matches these scenarios or the thresholds in [splitting-criteria.md](splitting-criteria.md), write delegation as a requirement, not permission. Prefer "MUST use agent for these files/logs/URLs" over "may use sub-agents if needed". If the orchestrator intentionally does not delegate, record the reason: small scope, enough context already loaded, tool unavailable, or overhead greater than benefit.

### ❌ When NOT to Use Sub-agents

→ **[splitting-criteria.md#part-4-when-not-to-split](splitting-criteria.md#part-4-when-not-to-split)** for detailed decision matrix and complexity scaling guidelines.

**Quick reference:** Avoid sub-agents for single file/< 5 min tasks, simple Q&A, or when follow-up conversation is needed.

---

## How to Invoke

### Enabling agent

**Option 1: Tool Picker**

- Open VS Code chat → Tool picker → Enable `agent`

**Option 2: Agent YAML (Recommended)**

```yaml
# VS Code Copilot
---
name: Orchestrator
tools: ["agent", "web/fetch", "read"]
---
# Claude Code
---
name: Orchestrator
tools: ["Task", "WebSearch", "Read"]
---
```

### Invocation Methods

#### Method 1: Direct Tool Reference (Most Reliable)

```markdown
Use #tool:agent for each URL to fetch and summarize the content.
```

#### Method 2: Natural Language

```markdown
For each file, launch a sub-agent to analyze and return findings.
```

#### Method 3: Explicit Tool Call (In Agent Definition)

```markdown
## Workflow

1. Analyze requirements
2. For each identified file:
   - Call #tool:agent with prompt:
     "Read [filename], identify issues, suggest fixes"
3. Synthesize all sub-agent results
```

---

## Prompt Engineering for agent

### Sub-agent Prompt Requirements

When calling `agent`, your **prompt** parameter must include:

| Element             | Example                                       |
| ------------------- | --------------------------------------------- |
| **agentName**       | `Researcher`                                  |
| **Clear task**      | "Fetch and summarize the content of this URL" |
| **Expected output** | "Return a 100-word summary with key points"   |
| **Constraints**     | "Focus only on pricing information"           |
| **Return format**   | "Output as bullet points with source quotes"  |

### Zenn-compliant minimal template

`MyOrchestrator.agent.md`:

```markdown
---
name: MyOrchestrator
tools: ["agent"]
agents: ["Researcher"]
---

#tool:agent を使用して、Researcher エージェントを呼び出してください。

- prompt: ${調査したい内容}
- agentName: Researcher
```

### Good Prompt Examples

```markdown
# Research Sub-agent

Fetch https://example.com/docs and analyze:

1. Core features (max 3)
2. Pricing tiers
3. Limitations

Return as structured Markdown with:

- Feature list
- Price comparison table
- Recommendation
```

```markdown
# Code Review Sub-agent

Read the file at {filepath} and:

1. Identify potential bugs
2. Check for security issues
3. Suggest performance improvements

Return: JSON with {bugs: [], security: [], performance: []}
```

### Bad Prompt Examples

❌ Too vague: "Look at this and tell me what you think"
❌ Missing return format: "Analyze the logs" (what format?)
❌ Too broad: "Research everything about React" (unbounded)

---

## Orchestrator-Workers Pattern with agent

### Architecture

```
Main Agent (Orchestrator)
├── Decompose task into subtasks
├── For each subtask:
│   └── agent(subtask_prompt)
│       └── Returns: summary (1-2k tokens)
└── Synthesize all summaries
```

### Example: Multi-File Code Review

**Orchestrator Agent Definition:**

````markdown
---
name: Code Review Orchestrator
description: Reviews code changes across multiple files using sub-agents
tools: ["agent", "read", "search", "search/changes"]
---

# Code Review Orchestrator

## Workflow

1. **Identify changed files**
   - Use #tool:search/changes to list modified files
2. **Dispatch review sub-agents** (MUST use #tool:agent)
   For each file, call #tool:agent with prompt:

   ```text
   Review the file at [filepath]:
   - Security issues (HIGH/MEDIUM/LOW)
   - Logic bugs
   - Style violations
   Return as structured JSON: {security: [], bugs: [], style: []}
   ```

3. **Synthesize results**
   - Aggregate all sub-agent outputs, prioritize by severity, generate the final report

## Sub-agent Dispatch

Use #tool:agent for file reviews. Do not review files directly in the main context.
````

---

## Common Pitfalls

### Pitfall 1: Orchestrator Does the Work Itself

❌ **Problem:** Orchestrator reads files directly instead of delegating

**Symptoms:**

- No #tool:agent calls in execution
- Main context fills up
- Agent says "I'll review each file" but doesn't spawn sub-agents

**Solution:** Use explicit, imperative instructions:

```markdown
## MANDATORY: You MUST use #tool:agent

Do NOT read file contents directly.
Do NOT review code in main context.
For EACH file → agent with specific prompt.
```

### Pitfall 2: Parallel Execution Overhead

⚠️ **Note:** As of 2026/01, agent supports parallel execution, but with overhead.

**Trade-off:** Parallel sub-agents add VS Code processing overhead. In one test:

| Metric         | Sequential | Parallel (8 sub-agents) |
| -------------- | ---------- | ----------------------- |
| Total tokens   | 33,000     | ~80,000                 |
| Execution time | 5 sec      | 33 sec                  |
| Main context   | 33,000     | 10,000                  |

**Recommendation:** Use parallel sub-agents when:

- Context isolation is the primary goal
- Tasks are truly independent
- Main session needs to stay clean for follow-up work

```markdown
# For parallel execution, group related files into batches

# to reduce overhead while maintaining context isolation
```

### Pitfall 3: Nested Sub-agent Calls (Off by Default)

❌ **Problem:** Sub-agent tries to call another sub-agent and silently does the work itself

**Reality:** Local subagents cannot invoke further subagents by default. Nesting requires `chat.subagents.allowInvocationsFromSubagents: true` (max depth 5) and `agent` in the subagent's `tools`. A self-referential agent (listing itself in `agents`) also needs this setting.

**Solution:** Keep hierarchy flat unless recursion is intentional; if enabled, include a stopping condition:

```
✅ Correct:
Orchestrator → Worker A
            → Worker B
            → Worker C

⚠️ Only with the nesting setting enabled:
Orchestrator → Worker A → Sub-Worker
```

### Pitfall 4: Vague Sub-agent Prompts

❌ **Problem:** "Analyze this file" → Sub-agent doesn't know what to return

**Solution:** Always specify output format:

```markdown
Return as:

- Summary: (1 paragraph)
- Issues: (bullet list)
- Recommendation: (1 sentence)
```

### Pitfall 5: Named Custom Agent Not Invoked

❌ **Problem:** The orchestrator names a worker agent but a generic subagent runs instead, or the call fails

**Causes:** Agent names are case-sensitive (use the exact `name`); the worker has `disable-model-invocation: true`; the coordinator's `agents` list does not include it.

**Solution:** Use the exact name, check the coordinator's `agents` list, and confirm in Chat view > right-click > Diagnostics that the worker loaded without errors.

### Pitfall 6: Custom Agent as Sub-agent

Custom agents can run as subagents without any extra setting (the old `chat.customAgentInSubagent.enabled` setting is no longer needed).

**Usage:**

```markdown
#tool:agent を使用して、以下の処理をサブエージェントで実行してください。

- prompt: {サブエージェントへの入力}
- agentName: my-custom-agent
```

**Controls:**

- `user-invocable: false` hides the worker from the agents dropdown only; it stays callable as a subagent
- `disable-model-invocation: true` blocks subagent invocation, but explicitly listing the agent in a coordinator's `agents` overrides it
- `agents: [...]` on the coordinator restricts allowed workers (`['*']` or omitted = all, `[]` = none); include `agent` in its `tools`
- `infer:` は deprecated。`user-invocable` / `disable-model-invocation` を使用すること
- Model order: explicit `model` in the call > worker's `model` > main model. A model above the main model's cost tier makes the subagent fail
- Sub-agent cannot access main session history; ask-question and todo tools are unavailable to Local subagents

### Pitfall 7: Restricting Orchestrator's tools Breaks Sub-agents

❌ **Problem:** Orchestrator の `tools:` から `edit` を外してSRPを強制 → サブエージェント（Writer等）が `edit` を使えなくなる

**Reality:** custom agent を指定しない汎用サブエージェントは、親の instructions と選択済みツールを継承する（公式 docs）。そのため親の `tools:` が実質的な上限になる。custom agent の worker は自分の `tools:` で上書きできると docs にあるが、親の制限を超えられるかは未検証のため、親で外したツールを worker に期待しない。

```
❌ Wrong: Orchestratorで edit を制限
---
name: Orchestrator
tools: ["agent", "read", "todo"]  # edit がない
---
→ Writer サブエージェントが edit/editFiles を使えない!

✅ Correct: tools を省略（全ツール利用可）
---
name: Orchestrator
description: サブエージェントに作業を委譲
---
→ サブエージェントは全ツールを使える
```

**Solution:**

- Orchestrator は `tools:` を**省略**する（= 全ツール利用可、agent-template.md推奨）
- SRP の強制は `tools:` ではなく、**プロンプト内の MANDATORY 指示**で行う
- `tools:` 制限は Worker エージェント（末端）に対してのみ適用する

---

## Inline Sub-agent Pattern (One-off Tasks)

For one-off delegation, embed the sub-agent's role definition directly in the prompt instead of creating an `.agent.md` file.

### Inline vs Named Custom Agent

| Approach                                    | Pros                               | Cons                                  |
| ------------------------------------------- | ---------------------------------- | ------------------------------------- |
| Named custom agent (`agentName: developer`) | Reusable, own tools/model          | Needs exact name, discoverable file   |
| **Inline definition**                       | Self-contained, no file dependency | Inherits parent tools; longer prompts |

### Example: Inline Developer Sub-agent

```markdown
#tool:agent を使用してサブエージェントを起動してください。

**prompt**: 以下の内容を渡す

# Developer Agent

## Role

あなたは開発者です。バグ修正、コードの改善を行います。

## Goals

- TypeScript のベストプラクティスに従う
- エラーなくコンパイルされることを確認

## Done Criteria

- `npm run compile` がエラーなしで完了

---

## タスク

{具体的な修正内容}
```

## Token Efficiency

### Comparison

| Approach                 | Main Context | Total Tokens | Time   |
| ------------------------ | ------------ | ------------ | ------ |
| Direct (no sub-agents)   | 33,000       | 33,000       | 5 sec  |
| With sub-agents (8 URLs) | 9,000        | 40,000       | 71 sec |

### Trade-off

- **Speed:** Direct is faster (no sub-agent overhead)
- **Context quality:** Sub-agents keep main context clean
- **Long sessions:** Sub-agents prevent context rot

### Recommendation

| Session Length   | Recommendation         |
| ---------------- | ---------------------- |
| < 30 min         | Direct (no sub-agents) |
| 30 min - 2 hours | Selective sub-agents   |
| > 2 hours        | Mandatory sub-agents   |

---

## Handoffs vs agent

| Feature          | Handoffs                                | agent                   |
| ---------------- | --------------------------------------- | ----------------------- |
| **Context**      | Shared conversation + pre-filled prompt | Isolated (clean window) |
| **User Control** | Manual approval                         | Automatic execution     |
| **Use Case**     | Phase transitions                       | Context isolation       |
| **Workflow**     | Plan → Implement → Review               | Research, log analysis  |

**Recommendation:**

- Use **Handoffs** for human-in-the-loop phase transitions
- Use **agent (旧 runSubagent)** for context-heavy isolated tasks

---

## Checklist

```markdown
## agent Implementation Checklist

### Agent Definition

- [ ] tools includes "agent" (required when `agents:` is set)
- [ ] Explicit instructions to USE sub-agents (not just "can use")
- [ ] Sub-agent prompt template defined

### Prompt Engineering

- [ ] Clear task description in sub-agent prompt
- [ ] Expected output format specified
- [ ] Constraints/scope defined
- [ ] Return structure (JSON/Markdown/etc.) specified

### Anti-patterns Avoided

- [ ] Parallel sub-agents only for truly independent tasks
- [ ] No vague "analyze this" prompts
- [ ] Named workers: exact name, coordinator `agents` list, `disable-model-invocation` checked
- [ ] Orchestrator doesn't do sub-agent work itself

### Testing

- [ ] Verified sub-agents are actually called (not skipped)
- [ ] Checked return summaries are appropriately sized
- [ ] Confirmed main context stays clean
```

---

## References

- [Use subagents in VS Code](https://code.visualstudio.com/docs/agents/run/subagents)
- [Custom Agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [Chat in IDE - GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/chat-with-copilot/chat-in-ide#using-subagents)
- [GitHub Copilot agent (旧 runSubagent) - Zenn](https://zenn.dev/openjny/articles/2619050ec7f167)
- [Context Engineering for Agents - LangChain Blog](https://www.langchain.com/blog/context-engineering-for-agents)
- [Handoffs Guide](handoffs-guide.md) - Alternative for human-in-the-loop workflows
- [Splitting Criteria](splitting-criteria.md) - When to use sub-agents

---

## tools 形式の注意点

ツール名・エイリアス・形式は [agent-template.md の Recommended tools style](agent-template.md#recommended-tools-style-for-agentmd) を SSOT とする。サブエージェント関連で非自明な点だけ残す。

- `agent` tool set を入れ忘れると `agents:` を書いても委譲されない
- 旧フラット名（`runSubagent`, `readFile`, `fetch` 等）ではなく tool set（`read`）か `<set>/<tool>`（`read/readFile`, `web/fetch`）で書く
- 公式例に合わせ flow 形式（`tools: ["agent", "read", "search"]`）で書く

### シンプルなプロンプト構造

複雑な450行のプロンプトより、シンプルな70行のプロンプトの方が効果的です。
