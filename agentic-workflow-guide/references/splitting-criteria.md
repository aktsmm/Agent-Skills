# Splitting Criteria

Guide for deciding when to escalate complexity (Prompt → Agent → Multi-Agent) and when to split into sub-agents.

's recommendation.

### Evidence Levels

| Icon | Meaning                             |
| ---- | ----------------------------------- |
| ✅   | Official source (Anthropic, OpenAI) |
| ⚠️   | Indirect evidence / best practice   |
| 📊   | Community-verified (empirical)      |

> **Note on Thresholds:** Specific numeric thresholds (50 lines, 70%, etc.) are practical guidelines derived from community experience. Adjust based on your project needs. See Part 5 for customization.

---

## Part 1: Escalation Ladder

When a simple approach isn't working, escalate to the next level.

### Levels

| Level  | Configuration         | When to Use                                | Escalation Triggers (Observable Signals)                                   | Evidence |
| ------ | --------------------- | ------------------------------------------ | -------------------------------------------------------------------------- | -------- |
| **L0** | Single Prompt         | Simple Q&A, single response completes task | Same request retried 3+ times, output format unstable                      | ⚠️       |
| **L1** | Prompt + Instructions | Repeated use, consistency needed           | Steps > 5, complex branching, **repeated "missed" or "overlooked" errors** | ⚠️       |
| **L2** | Single Agent          | Dynamic decisions, tool use required       | Multiple responsibilities, context > 70%, phase transitions needed         | ✅ [^1]  |
| **L3** | Multi-Agent           | Complex workflows, parallel processing     | Independent subtasks, context isolation required                           | ✅ [^2]  |

> **Context Rot:** Research shows LLM performance degrades as context length increases, even on simple tasks. This supports the "context > 70%" threshold as a safety margin. [^3]

### Observable Escalation Signals

**L0 → L1 (Add Instructions)**

- [ ] Same request retried 3+ times with different phrasing
- [ ] Output format varies between runs
- [ ] Need to repeat the same constraints every time

**L1 → L2 (Create Agent)**

- [ ] Agent says "I missed that" or "I overlooked" something
- [ ] Later instructions in long prompts are ignored
- [ ] Need dynamic tool selection based on input
- [ ] Steps exceed 5-7 and require conditional branching
- [ ] User frequently needs to correct/redirect mid-task

**L2 → L3 (Multi-Agent)**

- [ ] Single agent context exceeds 70%
- [ ] Multiple independent responsibilities that could run in parallel
- [ ] Detailed exploration pollutes main task context
- [ ] Clear phase boundaries (Plan → Implement → Review)

### Decision Flowchart

```
Task received
│
├─ Single LLM call sufficient?
│   ├─ YES → L0: Single Prompt
│   └─ NO ↓
│
├─ Repeated use / consistency needed?
│   ├─ NO → L0: Single Prompt
│   └─ YES ↓
│
├─ Steps ≤ 5 AND no complex branching?
│   ├─ YES → L1: Prompt + Instructions
│   └─ NO ↓
│
├─ Dynamic decisions / tool use needed?
│   ├─ NO → L1: Prompt + Instructions
│   └─ YES ↓
│
├─ Single responsibility AND context < 70%?
│   ├─ YES → L2: Single Agent
│   └─ NO → L3: Multi-Agent
```

---

## Part 2: Sub-agent Splitting Criteria

Once at L2/L3, use these criteria to decide sub-agent boundaries.

### Quantitative Triggers

| Metric                  | Threshold              | Action                                  | Evidence |
| ----------------------- | ---------------------- | --------------------------------------- | -------- |
| **Prompt line count**   | > 50 lines             | Consider splitting                      | ⚠️       |
| **Step count**          | > 5-7 sequential steps | Consider phase splitting                | ⚠️       |
| **Context usage**       | > 70%                  | Mandatory: use sub-agents or compaction | ⚠️ [^3]  |
| **Session duration**    | > 30 min               | Selective sub-agent use                 | ⚠️       |
| **Session duration**    | > 2 hours              | Sub-agents mandatory                    | ⚠️       |
| **Files to process**    | > 3-5 files            | File-per-subagent pattern               | 📊 [^4]  |
| **Tool calls expected** | > 15-20 calls          | Consider task splitting                 | ✅ [^2]  |
| **Subtask count**       | Dynamic/unknown        | Orchestrator-Workers pattern            | ✅ [^1]  |

### Qualitative Triggers

| Signal                     | Description                                          | Recommended Action                      |
| -------------------------- | ---------------------------------------------------- | --------------------------------------- |
| **Responsibility overlap** | One prompt has multiple independent responsibilities | Split by SRP                            |
| **Context pollution**      | Detailed exploration pollutes main task              | Isolate in sub-agent                    |
| **Parallelizable**         | Tasks can run independently                          | Parallelization or Orchestrator-Workers |
| **Phase transitions**      | Clear Plan → Implement → Review flow                 | Use Handoffs                            |
| **Quality loop needed**    | "Until good enough" iteration required               | Evaluator-Optimizer                     |
| **Dynamic task count**     | Subtask count depends on input                       | Orchestrator-Workers                    |
| **Input branching**        | Processing varies by input type                      | Routing                                 |

### Complexity Scaling ✅

 Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) [^2]

| Query Complexity  | Sub-agent Count | Tool Calls per Agent       |
| ----------------- | --------------- | -------------------------- |
| Simple fact check | 1               | 3-10                       |
| Direct comparison | 2-4             | 10-15 each                 |
| Complex research  | 10+             | Clear responsibility split |

---

## Part 3: Quick Split Check

### 5-Item Checklist

Run this check when creating or reviewing prompts/agents:

```markdown
## Quick Split Check

- [ ] Prompt > 50 lines of instructions?
- [ ] More than 5-7 sequential steps?
- [ ] Multiple independent responsibilities? (SRP violation)
- [ ] Expected context usage > 70%?
- [ ] Quality loop ("until good enough") needed?

→ **Any YES = Consider splitting** (See Part 2 for pattern selection)
→ **2+ YES = Splitting recommended**
→ **3+ YES = Splitting mandatory**
```

### Pattern Selection Guide

| Condition                         | Recommended Pattern  |
| --------------------------------- | -------------------- |
| Tasks have clear ordering         | Prompt Chaining      |
| Tasks are independent             | Parallelization      |
| Number of tasks is dynamic        | Orchestrator-Workers |
| Repeat until quality criteria met | Evaluator-Optimizer  |
| Processing varies by input type   | Routing              |

---

## Part 4: When NOT to Split

Sub-agents have overhead. Avoid when: ✅ [^1] 📊 [^4]

> **Empirical Data:** Sub-agent overhead can be significant. In one test, sub-agents reduced main session tokens by 70% but increased total tokens by 2.4x and execution time by 6.6x. [^4]

| Scenario                    | Reason                                    | Alternative                  |
| --------------------------- | ----------------------------------------- | ---------------------------- |
| Single file, short task     | Overhead > benefit                        | Direct processing            |
| Simple Q&A                  | Overkill                                  | L0 prompt                    |
| Need follow-up conversation | Sub-agents are stateless                  | Keep in main context         |
| Context accumulation needed | Previous details lost in sub-agent return | Single agent with compaction |
| Task < 5 min expected       | Setup overhead dominates                  | Direct processing            |

### Splitting Decision Matrix

| Condition                     | Use Sub-agent? | Reason                  |
| ----------------------------- | -------------- | ----------------------- |
| Single file, < 5 min          | ❌             | Overhead > benefit      |
| Multiple files, > 30 min      | ✅             | Context isolation value |
| Research + Implement + Review | ✅             | Phase separation        |
| Simple Q&A                    | ❌             | Single call sufficient  |
| Log analysis (1000+ lines)    | ✅             | Return only conclusions |
| Dynamic subtask discovery     | ✅             | Orchestrator-Workers    |

---

## Part 5: Customizing Thresholds

Default thresholds can be overridden in `.github/copilot-instructions.md`:

```markdown
## Splitting Criteria Overrides

<!-- Customize thresholds for this project -->

| Metric                       | Default | Project Override |
| ---------------------------- | ------- | ---------------- |
| Prompt line threshold        | 50      | 80               |
| Step count threshold         | 5-7     | 10               |
| Context usage threshold      | 70%     | 60%              |
| Session duration (selective) | 30 min  | 45 min           |
```

---

## References

### Official Sources

[^1]: [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents) — 5 workflow patterns, when to use agents

[^2]: [How We Built Our Multi-Agent Research System - Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) — Complexity scaling, sub-agent counts

[^3]: [Context Rot - Chroma Research](https://research.trychroma.com/context-rot) — LLM performance degrades with context length

### Community / Empirical

[^4]: [GitHub Copilot Chat サブエージェント検証 - Zenn](https://zenn.dev/openjny/articles/2619050ec7f167) — Overhead measurements

### Internal References

- [runSubagent-guide.md](runSubagent-guide.md) — Detailed sub-agent implementation
- [workflow-patterns/overview.md](workflow-patterns/overview.md) — 5 workflow patterns
- [context-engineering.md](context-engineering.md) — Context management techniques
