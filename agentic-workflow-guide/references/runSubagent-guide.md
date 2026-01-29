# runSubagent Guide

Practical guide for using subagent tools in VS Code Copilot and Claude Code.

## Table of Contents

- [What is runSubagent?](#what-is-runsubagent) - Key characteristics and purpose
- [When to Use](#when-to-use) - Effective scenarios and anti-patterns
- [How to Invoke](#how-to-invoke) - Enabling and invocation methods
- [Prompt Engineering](#prompt-engineering-for-runsubagent) - Sub-agent prompt requirements
- [Orchestrator-Workers Pattern](#orchestrator-workers-pattern-with-runsubagent) - Architecture examples
- [Common Pitfalls](#common-pitfalls) - Avoiding delegation failures
- [Token Efficiency](#token-efficiency) - Trade-offs and recommendations
- [Handoffs vs runSubagent](#handoffs-vs-runsubagent) - Comparison
- [Checklist](#checklist) - Implementation checklist

> **Platform Note**:
>
> - **VS Code Copilot**: Use `runSubagent` in `tools:` and `#tool:runSubagent` in prompts
> - **Claude Code**: Use `Task` in `tools:`

## What is runSubagent?

`runSubagent` launches an independent agent with a **clean context window** to handle complex, multi-step tasks autonomously.

### Key Characteristics

| Aspect        | Description                                                       |
| ------------- | ----------------------------------------------------------------- |
| **Context**   | Each sub-agent has its own context window (isolated from main)    |
| **Execution** | Synchronous - main agent waits for result (NOT async/background)  |
| **Stateless** | One-shot execution - no follow-up conversation possible           |
| **Return**    | Only final summary returns to main agent                          |
| **Parallel**  | ✅ Supported (2026/01+) - multiple sub-agents can run in parallel |
| **Nesting**   | ❌ NOT supported - sub-agents cannot call runSubagent             |

### Primary Purpose

> "runSubagent is for **context management**, NOT for speed optimization."

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

### Enabling runSubagent

**Option 1: Tool Picker**

- Open VS Code chat → Tool picker → Enable `runSubagent`

**Option 2: Agent YAML (Recommended)**

```yaml
# VS Code Copilot
---
name: Orchestrator
tools: ["runSubagent", "fetch", "readFile"]
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
Use #tool:runSubagent for each URL to fetch and summarize the content.
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
   - Call #tool:runSubagent with prompt:
     "Read [filename], identify issues, suggest fixes"
3. Synthesize all sub-agent results
```

---

## Prompt Engineering for runSubagent

### Sub-agent Prompt Requirements

When calling `runSubagent`, your **prompt** parameter must include:

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
tools: ['runSubagent']

---

#tool:runSubagent を使用して、Researcher エージェントを呼び出してください。

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

## Orchestrator-Workers Pattern with runSubagent

### Architecture

```
Main Agent (Orchestrator)
├── Decompose task into subtasks
├── For each subtask:
│   └── runSubagent(subtask_prompt)
│       └── Returns: summary (1-2k tokens)
└── Synthesize all summaries
```

### Example: Multi-File Code Review

**Orchestrator Agent Definition:**

```yaml
---
name: Code Review Orchestrator
description: Reviews code changes across multiple files using sub-agents
tools: ["runSubagent", "read_file", "grep_search"]
---
# Code Review Orchestrator

## Workflow

1. **Identify changed files**
- Use grep_search or read_file to list modified files

2. **Dispatch review sub-agents** ⚠️ MUST USE runSubagent
For each file, call #tool:runSubagent with prompt:
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

You MUST use #tool:runSubagent for file reviews.
Do NOT review files directly in main context.
Each sub-agent keeps file content isolated.
```

### Example: Research Aggregator

```yaml
---
name: Research Orchestrator
tools: ["runSubagent", "fetch"]
---

# Research Orchestrator

## Task

Research multiple URLs and synthesize findings.

## Execution (⚠️ MANDATORY STEPS)

1. **For EACH URL, call #tool:runSubagent:**
```

Prompt: "Fetch {url} and summarize:

- Main topic (1 sentence)
- Key facts (3 bullet points)
- Relevance to query: {user_query}
  Return: Markdown summary, max 200 words"

```

2. **After ALL sub-agents return:**
- Synthesize into unified report
- Highlight conflicts between sources
- Provide recommendation

## Why Sub-agents?

- Each URL's full content stays in sub-agent context
- Main agent only receives 200-word summaries
- Enables processing 10+ URLs without context overflow
```

---

## Common Pitfalls

### Pitfall 1: Orchestrator Does the Work Itself

❌ **Problem:** Orchestrator reads files directly instead of delegating

**Symptoms:**

- No runSubagent calls in execution
- Main context fills up
- Agent says "I'll review each file" but doesn't spawn sub-agents

**Solution:** Use explicit, imperative instructions:

```markdown
## MANDATORY: You MUST use #tool:runSubagent

Do NOT read file contents directly.
Do NOT review code in main context.
For EACH file → runSubagent with specific prompt.
```

### Pitfall 2: Parallel Execution Overhead

⚠️ **Note:** As of 2026/01, runSubagent supports parallel execution, but with overhead.

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

**Reality:** Sub-agents cannot call `runSubagent` themselves. Nesting is not supported.

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

### Pitfall 4: Sub-agent Handoff to Named Agents

❌ **Problem:** Trying to use `subagentType=my-agent` doesn't work

**Reality:** runSubagent creates fresh agents, cannot handoff to existing agent definitions.

**Solution:** Define sub-agent behavior in the prompt parameter, not in separate files.

### Pitfall 5: Custom Agent as Sub-agent (Experimental)

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
#tool:runSubagent を使用して、以下の処理をサブエージェントで実行してください。

- prompt: {サブエージェントへの入力}
- agentName: my-custom-agent
```

**Limitations:**

- Custom agent must have `infer: true` (default)
- Sub-agent cannot access main session context
- Parallel execution available (2026/01+) but with overhead

---

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

## Handoffs vs runSubagent

| Feature          | Handoffs                  | runSubagent             |
| ---------------- | ------------------------- | ----------------------- |
| **Context**      | Shared (via prompt)       | Isolated (clean window) |
| **User Control** | Manual approval           | Automatic execution     |
| **Use Case**     | Phase transitions         | Context isolation       |
| **Workflow**     | Plan → Implement → Review | Research, log analysis  |

**Recommendation:**

- Use **Handoffs** for human-in-the-loop phase transitions
- Use **runSubagent** for context-heavy isolated tasks

---

## Checklist

```markdown
## runSubagent Implementation Checklist

### Agent Definition

- [ ] tools includes "runSubagent"
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
- [GitHub Copilot runSubagent - Zenn](https://zenn.dev/openjny/articles/2619050ec7f167)
- [Context Engineering for Agents - LangChain Blog](https://blog.langchain.com/context-engineering-for-agents/)- [Handoffs Guide](handoffs-guide.md) - Alternative for human-in-the-loop workflows
- [Splitting Criteria](splitting-criteria.md) - When to use sub-agents
