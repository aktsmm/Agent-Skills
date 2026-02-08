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

> **Platform Note (2026/02 Updated)**:
>
> - **VS Code Copilot**: Use `agent` in `tools:` and `#tool:agent` in prompts (`runSubagent` is a legacy alias)
> - **Claude Code**: Use `Task` in `tools:`

### Legacy call patterns (avoid in new docs)

The following legacy forms may still work but should not be used in new documentation:

- `tools: ["runSubagent"]` → use `tools: ["agent"]`
- `#tool:runSubagent` → use `#tool:agent`
- `runSubagent({ ... })` → use `agent({ ... })`
- `agent/runSubagent` (old tool path) → use `agent`

## What is agent?

The `agent` tool launches an independent agent with a **clean context window** to handle complex, multi-step tasks autonomously.

### Key Characteristics

| Aspect        | Description                                                       |
| ------------- | ----------------------------------------------------------------- |
| **Context**   | Each sub-agent has its own context window (isolated from main)    |
| **Execution** | Synchronous - main agent waits for result (NOT async/background)  |
| **Stateless** | One-shot execution - no follow-up conversation possible           |
| **Return**    | Only final summary returns to main agent                          |
| **Parallel**  | ✅ Supported (2026/01+) - multiple sub-agents can run in parallel |
| **Nesting**   | ❌ NOT supported - sub-agents cannot call agent                   |

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
tools: ["agent", "web/fetch", "readFile"]
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

```markdown
# MyOrchestrator.agent.md

---

name: MyOrchestrator
tools: ['agent']

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

```yaml
---
name: Code Review Orchestrator
description: Reviews code changes across multiple files using sub-agents
tools: ["agent", "read_file", "grep_search"]
---
# Code Review Orchestrator

## Workflow

1. **Identify changed files**
- Use grep_search or read_file to list modified files

2. **Dispatch review sub-agents** ⚠️ MUST USE agent
For each file, call #tool:agent with prompt:
```

Review the file at [filepath]:

- Security issues (HIGH/MEDIUM/LOW)
- Logic bugs
- Style violations
  Return as structured JSON: {security: [], bugs: [], style: []}

```

3. **Synthesize results**
- Aggregate all sub-agent outputs
- Prioritize by severity
- Generate final review report

## CRITICAL: Sub-agent Dispatch

You MUST use #tool:agent for file reviews.
Do NOT review files directly in main context.
Each sub-agent keeps file content isolated.
```

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

### Pitfall 3: Nested Sub-agent Calls (Not Supported)

❌ **Problem:** Sub-agent tries to call another sub-agent

**Reality:** Sub-agents cannot call `agent` themselves. Nesting is not supported.

**Solution:** Keep hierarchy flat:

```
✅ Correct:
Orchestrator → Worker A
            → Worker B
            → Worker C

❌ Wrong:
Orchestrator → Worker A → Sub-Worker (NOT ALLOWED)
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

### Pitfall 5: Sub-agent Handoff to Named Agents

❌ **Problem:** Trying to use `subagentType=my-agent` doesn't work

**Reality:** agent creates fresh agents, cannot handoff to existing agent definitions.

**Solution:** Define sub-agent behavior in the prompt parameter, not in separate files.

### Pitfall 6: Custom Agent as Sub-agent (Experimental)

⚠️ **Experimental Feature:** As of 2026/01, you can invoke custom agents as sub-agents with additional configuration.

**Enable in VS Code:**

```json
// settings.json
{
  "chat.customAgentInSubagent.enabled": true
}
```

**Usage:**

```markdown
#tool:agent を使用して、以下の処理をサブエージェントで実行してください。

- prompt: {サブエージェントへの入力}
- agentName: my-custom-agent
```

**Limitations:**

- Custom agent must have `infer: true` (default)
- Sub-agent cannot access main session context
- Parallel execution available (2026/01+) but with overhead

---

## Inline Sub-agent Pattern (Recommended)

Instead of referencing external `.agent.md` files, embed the sub-agent's role definition directly in the prompt.

### Why Inline?

| Approach                                    | Pros                     | Cons                              |
| ------------------------------------------- | ------------------------ | --------------------------------- |
| External reference (`agentName: developer`) | Reusable, DRY            | May not work reliably, dependency |
| **Inline definition**                       | Self-contained, reliable | Slightly longer prompts           |

### Example: Inline Developer Sub-agent

`markdown
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
`

### Benefits

1. **Reliability**: No dependency on external files
2. **Portability**: Single file works anywhere
3. **Clarity**: Sub-agent behavior is explicit in the orchestrator

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

| Feature          | Handoffs                  | agent                   |
| ---------------- | ------------------------- | ----------------------- |
| **Context**      | Shared (via prompt)       | Isolated (clean window) |
| **User Control** | Manual approval           | Automatic execution     |
| **Use Case**     | Phase transitions         | Context isolation       |
| **Workflow**     | Plan → Implement → Review | Research, log analysis  |

**Recommendation:**

- Use **Handoffs** for human-in-the-loop phase transitions
- Use **agent (旧 runSubagent)** for context-heavy isolated tasks

---

## Checklist

```markdown
## agent Implementation Checklist

### Agent Definition

- [ ] tools includes "agent"
- [ ] Explicit instructions to USE sub-agents (not just "can use")
- [ ] Sub-agent prompt template defined

### Prompt Engineering

- [ ] Clear task description in sub-agent prompt
- [ ] Expected output format specified
- [ ] Constraints/scope defined
- [ ] Return structure (JSON/Markdown/etc.) specified

### Anti-patterns Avoided

- [ ] No "process in parallel" expectations
- [ ] No vague "analyze this" prompts
- [ ] No reliance on handoff to named agents
- [ ] Orchestrator doesn't do sub-agent work itself

### Testing

- [ ] Verified sub-agents are actually called (not skipped)
- [ ] Checked return summaries are appropriately sized
- [ ] Confirmed main context stays clean
```

---

## References

- [Chat in IDE - GitHub Docs](https://docs.github.com/en/copilot/how-tos/chat-with-copilot/chat-in-ide#using-subagents)
- [Custom Agents in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [GitHub Copilot agent (旧 runSubagent) - Zenn](https://zenn.dev/openjny/articles/2619050ec7f167)
- [Context Engineering for Agents - LangChain Blog](https://blog.langchain.com/context-engineering-for-agents/)- [Handoffs Guide](handoffs-guide.md) - Alternative for human-in-the-loop workflows
- [Splitting Criteria](splitting-criteria.md) - When to use sub-agents

---

## ⚠️ tools 形式の注意点（2026/02 Updated）

VS Code Copilot のカスタムエージェントで正しくサブエージェントを呼び出すには、以下の形式を守る必要があります。

### 正しいツールエイリアス

| エイリアス | 説明                     | 間違い例              |
| ---------- | ------------------------ | --------------------- |
| agent      | サブエージェント呼び出し | runSubagent           |
| read       | ファイル読み取り         | read/readFile         |
| edit       | ファイル編集             | edit/editFiles        |
| search     | 検索                     | search/textSearch     |
| execute    | コマンド実行             | execute/runInTerminal |
| todo       | タスク管理               | todos                 |

> **参考:** [GitHub Docs - Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools)

### JSON配列形式を推奨

YAML配列形式は動作しない場合があります。JSON配列形式を使用してください。

正しい形式:
tools: ["agent", "read", "edit", "search", "execute", "todo"]

間違い形式:
tools:

- agent
- read

### シンプルなプロンプト構造

複雑な450行のプロンプトより、シンプルな70行のプロンプトの方が効果的です。
