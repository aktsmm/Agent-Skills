# runSubagent Guide

Practical guide for using `runSubagent` tool in VS Code Copilot.

> **Note**: The official Primary Alias is `agent`. Use `agent` in the `tools:` property.
> `runSubagent` works as a compatible alias in prompts and tool references.

## What is runSubagent?

`runSubagent` launches an independent agent with a **clean context window** to handle complex, multi-step tasks autonomously.

### Key Characteristics

| Aspect        | Description                                                      |
| ------------- | ---------------------------------------------------------------- |
| **Context**   | Each sub-agent has its own context window (isolated from main)   |
| **Execution** | Synchronous - main agent waits for result (NOT async/background) |
| **Stateless** | One-shot execution - no follow-up conversation possible          |
| **Return**    | Only final summary returns to main agent                         |
| **Parallel**  | ❌ NOT supported (2025/12) - executes sequentially               |

### Primary Purpose

> "runSubagent is for **context management**, NOT for speed optimization."

Use when you want to:

- Keep main session context **clean** (avoid context rot)
- Isolate detailed exploration from synthesis
- Process large data without polluting main context

---

## When to Use

### ✅ Effective Scenarios

| Scenario                    | Example                                                |
| --------------------------- | ------------------------------------------------------ |
| **Research mid-session**    | "Investigate this library's API" during implementation |
| **Log/data analysis**       | Parse thousands of log lines, return only conclusions  |
| **File-by-file operations** | Fix ESLint errors in each file independently           |
| **Phase-based workflows**   | Plan → Implement → Review (each phase = sub-agent)     |

### ❌ Avoid When

| Scenario                  | Reason                                               |
| ------------------------- | ---------------------------------------------------- |
| Need follow-up questions  | Sub-agents are stateless, no "tell me more"          |
| Task is too lightweight   | Startup overhead > benefit                           |
| Need context accumulation | Previous step's details are lost in sub-agent return |

---

## How to Invoke

### Enabling runSubagent

**Option 1: Tool Picker**

- Open VS Code chat → Tool picker → Enable `runSubagent`

**Option 2: Agent YAML (Recommended)**

```yaml
---
name: Orchestrator
# Use Primary Aliases in tools: property
tools: ["agent", "web", "read"]
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
| **Clear task**      | "Fetch and summarize the content of this URL" |
| **Expected output** | "Return a 100-word summary with key points"   |
| **Constraints**     | "Focus only on pricing information"           |
| **Return format**   | "Output as bullet points with source quotes"  |

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

### Pitfall 2: Expecting Parallel Execution

❌ **Problem:** Prompt says "process in parallel" but runSubagent is sequential

**Reality:** As of 2025/12, runSubagent does NOT support parallel execution.

**Solution:** Accept sequential execution or reduce sub-agent count:

```markdown
# Note: Sub-agents execute sequentially

# Optimize by grouping related files

For each MODULE (not each file), use one sub-agent
```

### Pitfall 3: Vague Sub-agent Prompts

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
- [Context Engineering for Agents - LangChain Blog](https://blog.langchain.com/context-engineering-for-agents/)
