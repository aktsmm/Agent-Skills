# Deep Agent Patterns

Patterns for building research-oriented agents with recursive information gathering and quality evaluation.

## Overview

Deep Agents are specialized for comprehensive information gathering with citation-backed outputs. Key characteristics:

- **Exhaustive Coverage**: Multi-perspective investigation
- **Recursive Collection**: Follow links to original sources (max 3 levels)
- **Quality Gates**: Evaluator sub-agent validates output
- **Citation Required**: Every non-trivial fact needs a reference

## Core Structure

```yaml
---
name: DeepResearch
description: "Comprehensive topic research with citations"
tools: ["search", "web/fetch", "agent", "edit/editFiles", "todo"]
---
```

## Four Phases

| Phase                | Purpose            | Key Actions                                      |
| -------------------- | ------------------ | ------------------------------------------------ |
| **0. Clarification** | Understand intent  | Ask: purpose, focus areas, constraints           |
| **1. Preparation**   | Plan investigation | List perspectives, check for duplicates          |
| **2. Execution**     | Gather information | Sub-agents per perspective, recursive collection |
| **3. Evaluation**    | Quality check      | Evaluator sub-agent, iterate if needed           |
| **4. Completion**    | Finalize           | Update status, report to user                    |

## Scaling by Complexity

| Complexity  | Example               | Perspectives |
| ----------- | --------------------- | ------------ |
| **Simple**  | Definition check      | 1-2          |
| **Medium**  | Feature investigation | 3-4          |
| **Complex** | Comparative analysis  | 5+           |

## Recursive Collection Strategy

### Depth Levels

| Level  | Target           | Example                         |
| ------ | ---------------- | ------------------------------- |
| **L0** | Entry point      | Official blog, docs page        |
| **L1** | In-article links | Referenced specs, related docs  |
| **L2** | Spec links       | Best practices, implementations |

### Stop Conditions

- Same domain: max 3 levels
- Per entry point: max 10 sources

### Source Priority

1. **Official Docs** (Microsoft Docs, GitHub Docs)
2. **Official Blogs** (Azure Blog, GitHub Blog)
3. **Tech Blogs** (Zenn, Qiita, dev.to)
4. **Community** (Stack Overflow, Reddit)
5. **Social** (Twitter/X) ← Last resort

## Sub-agent Definitions

### Research Sub-agent

```markdown
**Purpose**: Search and document findings for a specific perspective.

**Input**:

- Topic: <research target>
- Perspective: <focus area>
- Output file: <report path>

**Search Strategy**:

1. Start broad: Short general queries for overview
2. Narrow down: Refine based on discoveries
3. Recursive collect: Follow in-article links
4. Cross-reference: Compare across vendors/specs
5. Alternative paths: Try official sites if paywalled

**Output**: NULL (writes directly to file)
```

### Evaluator Sub-agent

```markdown
**Purpose**: Analyze report quality and identify gaps.

**Input**:

- Path: <report file>
- Topic: <original topic>

**Detection Criteria** (by priority):

1. **Missing information** (high): Gaps in coverage
2. **Missing citations** (high): Facts without references
3. **Unsubstantiated claims** (high): Opinions as facts
4. **Insufficient explanation** (medium): Key concepts unclear
5. **Stale information** (low): Outdated data

**Output**: JSON list of issues found
```

## Stop Conditions

### Coverage (early exit OK)

- Each sub-question has 2+ independent sources
- New searches yield no new information
- Contradictions resolved or documented

### Budget Limits (hard stop)

| Limit             | Value    |
| ----------------- | -------- |
| Time              | 30 min   |
| Sources           | 20       |
| Per entry point   | 10 URLs  |
| Recursion depth   | 3 levels |
| Reflection cycles | 5        |

### Error Handling

| Error                  | Action                               |
| ---------------------- | ------------------------------------ |
| Search error           | Retry 3x, then try alternative query |
| Source inaccessible    | Skip, find alternative               |
| 3 consecutive failures | Report to user, ask to continue      |

## Output Format

### Report Template

```markdown
---
topic: <topic>
date: YYYY-MM-DD
status: draft|review|final
sources_count: <N>
reflection_count: <N>
---

# <Topic> Research Report

## TL;DR

<1-3 sentence summary>

## Findings

### <Section 1>

<content>[^1]

### <Section 2>

<content>[^2]

## References

[^1]: <URL> - <description>

[^2]: <URL> - <description>

## Limitations

- <points not verified>
- <areas needing more research>
```

### Manifest (History)

Track research sessions in `research/manifest.md`:

```markdown
## Research History

| Date       | Topic   | File   | Status      | Sources |
| ---------- | ------- | ------ | ----------- | ------- |
| YYYY-MM-DD | <topic> | <file> | draft/final | N       |

## Latest Session

### YYYY-MM-DD: <topic>

- **Perspectives**: <list>
- **Reflections**: N/5
- **Stop reason**: Coverage / Budget / User
- **Unresolved**: <remaining issues>
```

## Permissions Pattern

```yaml
### Allowed
- Web page fetch and analysis
- Documentation search
- File creation in `research/`
- Sub-agent invocation

### Forbidden
- ❌ Don't present inference as fact
- ❌ Don't cite unusual facts without reference
- ❌ Don't edit files outside `research/`
```

## Anti-patterns

| ❌ Don't                | ✅ Do Instead                        |
| ----------------------- | ------------------------------------ |
| Mix opinions with facts | Clearly separate or exclude opinions |
| Skip citations          | Add footnote for every claim         |
| Single-source findings  | Require 2+ independent sources       |
| Unlimited recursion     | Set hard depth/count limits          |
| No quality check        | Always run evaluator sub-agent       |

## Key Principles

1. **Facts Only**: No inference, no opinions, no recommendations
2. **Citation Everything**: Every non-trivial fact needs a source
3. **Recursive but Bounded**: Follow links, but with hard limits
4. **Quality Gates**: Evaluator sub-agent before finalization
5. **Transparent Limitations**: Document what wasn't verified

## External References

- [Anthropic: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) - 8 principles for multi-agent design
- [LangChain: Deep Agents](https://blog.langchain.com/deep-agents/) - 4 elements of Deep Agents
- [PromptLayer: How Deep Research Works](https://blog.promptlayer.com/how-deep-research-works/) - 5-phase process, stop conditions
- [openjny: なんちゃって Deep Research](https://zenn.dev/openjny/articles/ac83e9eca6678a) - VS Code Copilot implementation
- [OpenAI: Introducing Deep Research](https://openai.com/ja-JP/index/introducing-deep-research/) - Official specification
