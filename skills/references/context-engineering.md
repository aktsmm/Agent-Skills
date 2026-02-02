# Context Engineering

Strategies for curating and managing context in long-running AI agents.

> "Context engineering is the art and science of curating what will go into the limited context window."
> — Anthropic

## Overview

| Concept                     | Description                                         | Use Case                            |
| --------------------------- | --------------------------------------------------- | ----------------------------------- |
| **Prompt Engineering**      | Writing effective prompts (system prompts)          | One-shot tasks                      |
| **Context Engineering**     | Managing entire context state across multiple turns | Long-running agents                 |
| **Compaction**              | Summarizing and compressing context to continue     | Context window limits               |
| **Structured Note-taking**  | Persisting notes outside the context window         | Multi-hour tasks, progress tracking |
| **Sub-agent Architectures** | Specialized sub-agents with clean context windows   | Complex research, parallel tasks    |

---

## Why Context Engineering Matters

### Context Rot

As tokens increase, recall accuracy decreases. This is called **context rot**.

```
Token Count vs. Recall Accuracy

Low tokens   ████████████████ High accuracy
Medium       ██████████░░░░░░ Moderate
High tokens  ████░░░░░░░░░░░░ Low accuracy (context rot)
```

### Key Insight

> "Context must be treated as a finite resource with diminishing marginal returns."

**Principle:** Find the smallest set of high-signal tokens that maximize the likelihood of desired outcomes.

---

## Techniques

### 1. Compaction

**Summarize context when approaching limits, reinitialize with summary.**

#### When to Use

- Context window is 70-80% full
- Long conversation with accumulated tool outputs
- Need to continue with fresh focus

#### Implementation

```
Original Context (90% full):
- System prompt
- 50 conversation turns
- 100 tool call results
- Accumulated state

    ↓ Compaction

Compacted Context (30% full):
- System prompt (preserved)
- Summary of key decisions
- Unresolved issues
- 5 most recent files/resources
```

#### What to Keep vs. Discard

| Keep (High Signal)              | Discard (Low Signal)         |
| ------------------------------- | ---------------------------- |
| Architectural decisions         | Verbose tool outputs         |
| Unresolved bugs/issues          | Completed successful tasks   |
| Critical implementation details | Redundant conversation turns |
| Current goals and constraints   | Exploratory dead-ends        |

#### Anthropic's Tip

> "Start by maximizing recall to ensure your compaction prompt captures every relevant piece of information, then iterate to improve precision by eliminating superfluous content."

---

### 2. Structured Note-taking (Agentic Memory)

**Persist notes outside the context window for later retrieval.**

#### When to Use

- Multi-hour tasks with clear milestones
- Progress tracking across context resets
- Learning and improvement over time

#### Implementation Patterns

```
Pattern A: File-based Memory
└── NOTES.md or TODO.md persisted to disk

Pattern B: Structured JSON
└── state.json with typed fields

Pattern C: Key-Value Store
└── Database or MCP memory tool
```

#### Example: NOTES.md

```markdown
# Agent Notes

## Current Objective

Training Pikachu to level 25 in Route 1

## Progress

- Steps completed: 1,234
- Pikachu level: 18 → 23 (+5)
- Remaining: 2 levels

## Learned Strategies

- Thunder Shock effective vs. Pidgey
- Avoid Rattata (wastes HP)

## Next Actions

1. Continue grinding until level 25
2. Move to Route 2
```

#### Benefits

- Survives context resets
- Agent can read own notes and continue
- Enables long-horizon coherence

---

### 3. Sub-agent Architectures

**Delegate to specialized sub-agents with clean context windows.**

#### When to Use

- Complex research requiring deep exploration
- Parallel exploration of multiple paths
- Need to isolate detailed work from main context

#### Architecture

```mermaid
graph TD
    A[Main Agent] --> B[Sub-agent 1: Search]
    A --> C[Sub-agent 2: Analysis]
    A --> D[Sub-agent 3: Code Review]
    B --> |Summary 1-2k tokens| E[Synthesis]
    C --> |Summary 1-2k tokens| E
    D --> |Summary 1-2k tokens| E
    E --> A
```

#### Key Pattern

| Sub-agent Work          | Return to Main Agent      |
| ----------------------- | ------------------------- |
| 50,000+ tokens explored | 1,000-2,000 token summary |
| Deep file reading       | Key findings only         |
| Multiple tool calls     | Synthesized conclusions   |

#### Benefits

- Clean separation of concerns
- Detailed search context stays isolated
- Main agent focuses on synthesis

---

## Just-in-Time Context Retrieval

**Load context dynamically at runtime instead of pre-loading everything.**

### Pattern

```
Traditional (Pre-load):
1. Load all relevant files into context
2. Process
3. Respond
→ Wastes context on unused information

Just-in-Time:
1. Keep lightweight references (file paths, queries, links)
2. Load specific data when needed
3. Discard after use
→ Efficient, focused context
```

### Implementation

```python
# Instead of loading entire codebase:
context = read_all_files("src/")  # ❌ Wasteful

# Use just-in-time retrieval:
relevant_files = grep_search("function_name")  # ✅ Targeted
context = read_file(relevant_files[0])         # ✅ On-demand
```

### Progressive Disclosure

> "Agents can assemble understanding layer by layer, maintaining only what's necessary in working memory."

---

## Hybrid Strategy

**Combine pre-retrieval and just-in-time for optimal performance.**

### Example: Claude Code Approach

| Pre-loaded (Upfront)             | Just-in-Time (On-demand)      |
| -------------------------------- | ----------------------------- |
| CLAUDE.md / copilot-instructions | File contents via glob/grep   |
| Project structure overview       | Specific function definitions |
| Key configuration                | Test results, logs            |

### Decision Matrix

| Task Characteristic          | Strategy     |
| ---------------------------- | ------------ |
| Static reference docs        | Pre-load     |
| Dynamic file contents        | Just-in-time |
| Frequently accessed          | Pre-load     |
| Rarely accessed              | Just-in-time |
| Large volume, low relevance  | Just-in-time |
| Small volume, high relevance | Pre-load     |

---

## Long-Horizon Task Checklist

```markdown
## Context Engineering Checklist

### Before Starting

- [ ] Is this a long-horizon task (>30 min continuous work)?
- [ ] Will context window likely fill up?
- [ ] Are there clear milestones to track?

### Technique Selection

- [ ] **Compaction**: Set up summarization trigger at 70% context
- [ ] **Note-taking**: Create NOTES.md or state file
- [ ] **Sub-agents**: Identify tasks suitable for delegation

### During Execution

- [ ] Monitor context usage
- [ ] Write notes at milestones
- [ ] Compact when needed
- [ ] Use just-in-time retrieval for large data

### After Completion

- [ ] Archive notes for future reference
- [ ] Document lessons learned
```

---

## Anti-Patterns

| Anti-Pattern            | Problem                           | Solution                |
| ----------------------- | --------------------------------- | ----------------------- |
| **Context Hoarding**    | Loading everything "just in case" | Just-in-time retrieval  |
| **No Compaction**       | Running until context exhausted   | Proactive summarization |
| **Stateless Loops**     | Forgetting progress on reset      | Structured note-taking  |
| **Monolithic Agent**    | One agent doing everything        | Sub-agent delegation    |
| **Premature Retrieval** | Loading data before knowing needs | Lazy loading            |

---

## References

- [Effective context engineering for AI agents - Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Building effective agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [How we built our multi-agent research system - Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)
