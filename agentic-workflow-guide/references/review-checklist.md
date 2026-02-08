# Review Checklist

Comprehensive review checklist for agent workflows. Includes anti-pattern detection.

## Anti-Pattern Quick Reference

| Anti-Pattern         | Problem                            | Solution                        |
| -------------------- | ---------------------------------- | ------------------------------- |
| God Agent            | All responsibilities in 1 agent    | Split with SRP                  |
| Context Overload     | Passing excessive unnecessary info | Minimize with ISP               |
| Silent Failure       | Ignoring errors and continuing     | Stop immediately with Fail Fast |
| Infinite Loop        | Loops without termination          | Set maximum iterations          |
| Big Bang             | Building everything at once        | Build small with Iterative      |
| Premature Complexity | Complex design from the start      | Simplicity First                |
| Black Box            | Internal state invisible           | Transparency                    |
| Tight Coupling       | Tight coupling between agents      | Loose Coupling                  |
| Hallucination        | Fabricating unverified info        | No Hallucination principle      |
| False Negative       | Treating "no results" as "empty"   | Re-query with explicit params   |


## How to Use

1. Review this checklist after completing workflow design
2. Mark each item as ✅ or ❌
3. If there are ❌ items, consider solutions
4. Improve until all items are ✅

---

## Quick Check (5 minutes)

Minimum items to verify:

```markdown
- [ ] Is each agent focused on a single responsibility? (SRP)
- [ ] Can errors be detected and stopped immediately? (Fail Fast)
- [ ] Is it divided into small steps? (Iterative)
- [ ] Can results be verified at each step? (Feedback Loop)
- [ ] Is there any possibility of infinite loops?
- [ ] Are related files (references, scripts) simple and minimal? (DRY)
```

---

## agent Check (Orchestrator-Workers)

⚠️ **Critical for sub-agent delegation issues.** If orchestrator doesn't spawn workers, check these items.

> **Platform Note**: See [agent-guide.md](agent-guide.md#what-is-agent) for VS Code / Claude Code tool names.

```markdown
## Agent Definition

- [ ] Does `tools:` include subagent tool? (`agent` for VS Code, `Task` for Claude Code)
- [ ] Are instructions MANDATORY ("MUST use") not permissive ("can use")?
- [ ] Is explicit tool reference present? (`#tool:agent` for VS Code)
- [ ] Is orchestrator explicitly told NOT to do worker tasks itself?

## Sub-agent Prompts

- [ ] Does each agent call have a complete prompt?
- [ ] Is output format specified (JSON/Markdown/etc.)?
- [ ] Are constraints and scope defined?
- [ ] Is expected return size reasonable (1-2k tokens)?

## Common Anti-patterns

- [ ] ❌ "You can use sub-agents if needed" (too vague)
- [ ] ❌ "Process in parallel" (not supported as of 2025/12)
- [ ] ❌ Orchestrator reading files directly instead of delegating
- [ ] ❌ Missing subagent tool in tools: property
- [ ] ❌ Nested sub-agent calls (sub-agents cannot call agent)

## Correct Pattern Example

✅ Good (VS Code):

- "You MUST use #tool:agent for EACH file"
- "Do NOT read file contents directly in main context"
- "Each sub-agent prompt must include output format"
```

---

## Hallucination Check

⚠️ **Critical for information accuracy.** Detect and prevent fabricated outputs.

```markdown
## Source Verification

- [ ] Does every claim have a verifiable source?
- [ ] Are all URLs real and accessible?
- [ ] Are dates, numbers, and statistics from official sources?
- [ ] Is the agent using "probably", "likely", or "possibly" as facts?

## Detection Patterns

- [ ] ❌ Citing non-existent documentation
- [ ] ❌ Describing features not in official docs
- [ ] ❌ Generating fake URLs or file paths
- [ ] ❌ Filling knowledge gaps with assumptions

## Correct Behavior

- [ ] ✅ Returns status=not_found when information unavailable
- [ ] ✅ States "not explicitly documented" for uncertain info
- [ ] ✅ ESCALATEs to user when verification impossible
- [ ] ✅ Only outputs information backed by sources
```

---

## Hallucination Check

Critical for information accuracy. Detect and prevent fabricated outputs.

```markdown
## Source Verification

- [ ] Does every claim have a verifiable source?
- [ ] Are all URLs real and accessible?
- [ ] Are dates, numbers, and statistics from official sources?
- [ ] Is the agent using "probably", "likely", or "possibly" as facts?

## Detection Patterns

- [ ] No citing non-existent documentation
- [ ] No describing features not in official docs
- [ ] No generating fake URLs or file paths
- [ ] No filling knowledge gaps with assumptions

## Correct Behavior

- [ ] Returns status=not_found when information unavailable
- [ ] States "not explicitly documented" for uncertain info
- [ ] ESCALATEs to user when verification impossible
- [ ] Only outputs information backed by sources
```

---

## Detailed Check

### Core Principles Check

```markdown
## SSOT (Single Source of Truth)

- [ ] Is the same information defined in multiple places?
- [ ] Is configuration/context centrally managed?
- [ ] Is there a mechanism to reflect updates across the entire system?

## SRP (Single Responsibility Principle)

- [ ] Is each agent focused on a single responsibility?
- [ ] Are responsibility boundaries clear?
- [ ] Is there role overlap between agents?

## Simplicity First

- [ ] Is this the simplest possible solution?
- [ ] Are there unnecessary agents or steps?
- [ ] Could this be achieved with a simpler approach?

## Fail Fast

- [ ] Can errors be detected immediately?
- [ ] Can the system stop appropriately on errors?
- [ ] Are error messages clear?

## Iterative Refinement

- [ ] Is it divided into small steps?
- [ ] Can each step be verified?
- [ ] Is the structure suitable for gradual improvement?

## Feedback Loop

- [ ] Can results be verified at each step?
- [ ] Can feedback be applied to the next step?
- [ ] Is there a structure for improvement cycles?
```

### Quality Principles Check

```markdown
## Transparency

- [ ] Are plans and progress visualized?
- [ ] Is it clear to users what's happening?
- [ ] Are logs being output sufficiently?

## Gate/Checkpoint

- [ ] Is validation performed at each step?
- [ ] Are conditions for proceeding clearly defined?
- [ ] Is handling for validation failures defined?

## DRY (Don't Repeat Yourself)

- [ ] Are common processes being reused?
- [ ] Are prompt templates being utilized?
- [ ] Is there duplication of the same logic?

## ISP (Interface Segregation Principle)

- [ ] Is only the minimum necessary information being passed?
- [ ] Is unnecessary context being included?
- [ ] Is required information for each agent clear?

## Idempotency

- [ ] Is it safe to retry?
- [ ] Does executing the same operation multiple times produce the same result?
- [ ] Are side effects being managed?
```

### Scale & Safety Check

```markdown
## Human-in-the-Loop

- [ ] Are important decisions requiring human confirmation?
- [ ] Is there confirmation before high-risk operations?
- [ ] Is the balance between automation and human judgment appropriate?

## Termination Conditions

- [ ] Is there any possibility of infinite loops?
- [ ] Is a maximum iteration count set?
- [ ] Is a timeout set?

## Error Handling

- [ ] Is error handling missing anywhere?
- [ ] Is there handling for unexpected errors?
- [ ] Are recovery procedures defined?

## Security

- [ ] Is sensitive information being handled appropriately?
- [ ] Are permissions set to minimum?
- [ ] Can audit logs be collected?
```

---

## Related File Simplicity Check

**NEW:** Verify that referenced Markdown files, scripts, and assets are simple and maintainable.

```markdown
## Documentation (references/, .md files)

- [ ] Is information duplicated across multiple files?
- [ ] Could any reference files be consolidated?
- [ ] Are large files (>200 lines) well-structured with TOC?
- [ ] Is there orphaned documentation no longer referenced?

## Scripts (scripts/)

- [ ] Are scripts focused on a single task? (SRP for code)
- [ ] Are there duplicate functions across scripts?
- [ ] Is script logic simple enough to understand quickly?
- [ ] Are scripts tested and working?

## Prompts and Templates

- [ ] Are prompts reused where possible? (DRY)
- [ ] Is there copy-pasted prompt text that should be templated?
- [ ] Are prompt variations clearly organized?

## Overall Structure

- [ ] Is the total number of files reasonable (<15 for most workflows)?
- [ ] Is the directory structure intuitive?
- [ ] Can a new contributor understand the layout quickly?
```

---

## Anti-Pattern Detection

Detect and fix common workflow anti-patterns:

### God Agent

**Problem:** All responsibilities packed into one agent

```
❌ Bad:  Agent handles "search + analyze + report + email"
✅ Good: Separate agents for each responsibility
```

**Solution:** Split with SRP

---

### Context Overload

**Problem:** Passing excessive unnecessary information

```
❌ Bad:  Pass all files, entire history, all config
✅ Good: Pass only task-relevant data
```

**Solution:** Minimize with ISP

---

### Silent Failure

**Problem:** Ignoring errors and continuing

```python
# ❌ Bad
try:
    result = agent.execute()
except:
    pass  # Silent failure

# ✅ Good
try:
    result = agent.execute()
except AgentError as e:
    log.error(f"Agent failed: {e}")
    raise  # Stop immediately
```

**Solution:** Fail Fast

---

### Infinite Loop

**Problem:** Loops without termination conditions

```python
# ❌ Bad
while not evaluator.is_satisfied():
    result = generator.generate()
    # No termination condition

# ✅ Good
MAX_ITERATIONS = 5
for i in range(MAX_ITERATIONS):
    result = generator.generate()
    if evaluator.is_satisfied():
        break
else:
    log.warning("Max iterations reached")
```

**Solution:** Set maximum iterations

---

### Big Bang

**Problem:** Building everything at once

```
❌ Bad:  Design all → Implement all → Test at end
✅ Good: Design 1 → Implement 1 → Test → Repeat
```

**Solution:** Iterative Refinement

---

### Premature Complexity

**Problem:** Complex design from the start

```
❌ Bad:  Start with 10-agent workflow
✅ Good: Start with 1 agent, add complexity as needed
```

**Solution:** Simplicity First

> See [design-principles.md > Simplicity First](design-principles.md#3-simplicity-first) for Anthropic's recommendation.

---

### Black Box

**Problem:** Internal state invisible

```
❌ Bad:  Agent processes silently, user sees nothing
✅ Good: "Step 1/3: Fetching data..." → "Step 2/3: Analyzing..."
```

**Solution:** Transparency

---

### Tight Coupling

**Problem:** Changes to one agent cascade to many others

```
❌ Bad:  Change Agent A's output → B, C, D all break
✅ Good: Standardized interfaces, independent testing
```

**Solution:** Loose Coupling

---

## Review Result Template

```markdown
# Workflow Review Results

## Overview

- **Workflow Name**:
- **Review Date**:
- **Reviewer**:

## Check Results

### Core Principles

| Principle            | Result | Comment |
| -------------------- | ------ | ------- |
| SSOT                 | ✅/❌  |         |
| SRP                  | ✅/❌  |         |
| Simplicity First     | ✅/❌  |         |
| Fail Fast            | ✅/❌  |         |
| Iterative Refinement | ✅/❌  |         |
| Feedback Loop        | ✅/❌  |         |

### Quality Principles

| Principle       | Result | Comment |
| --------------- | ------ | ------- |
| Transparency    | ✅/❌  |         |
| Gate/Checkpoint | ✅/❌  |         |
| DRY             | ✅/❌  |         |
| ISP             | ✅/❌  |         |
| Idempotency     | ✅/❌  |         |

### Related File Simplicity

| Check                 | Result | Comment |
| --------------------- | ------ | ------- |
| No duplication        | ✅/❌  |         |
| Files consolidated    | ✅/❌  |         |
| Scripts focused       | ✅/❌  |         |
| Reasonable file count | ✅/❌  |         |

### Anti-Patterns

| Pattern              | Detected | Solution Applied |
| -------------------- | -------- | ---------------- |
| God Agent            | ✅/❌    |                  |
| Context Overload     | ✅/❌    |                  |
| Silent Failure       | ✅/❌    |                  |
| Infinite Loop        | ✅/❌    |                  |
| Big Bang             | ✅/❌    |                  |
| Premature Complexity | ✅/❌    |                  |
| Black Box            | ✅/❌    |                  |
| Tight Coupling       | ✅/❌    |                  |

## Improvement Proposals

1.
2.
3.

## Overall Evaluation

- [ ] Approved
- [ ] Conditionally Approved (after minor fixes)
- [ ] Requires Revision
```

---

## Next Steps

After review completion:

1. **All ✅** → Proceed to implementation
2. **Minor ❌** → Re-check after fixes
3. **Major ❌** → Revise design, re-review

---

## Related Documents

- [design-principles.md](design-principles.md) - Design principles details
- [workflow-patterns/overview.md](workflow-patterns/overview.md) - Workflow pattern details
- [context-engineering.md](context-engineering.md) - Context management for long tasks

---

## SSOT & Duplication Check

Check for Single Source of Truth violations and unnecessary duplication:

```markdown
## Definition Duplication

- [ ] Same table/logic appears in only one file? (no duplicate tables)
- [ ] Definitions referenced from other files have SSOT markers?
- [ ] Cross-file references use standard format: `> **SSOT**: See [file](path)`?

## View vs Master Separation

- [ ] Dashboard/view files contain links only, not full data?
- [ ] Master files are clearly designated as SSOT?
- [ ] Archive files have clear completion criteria?

## Common SSOT Anti-patterns

- [ ] ❌ Same task table in both DASHBOARD.md and active.md
- [ ] ❌ Holiday/validation rules duplicated in 3+ files
- [ ] ❌ Configuration repeated instead of referenced
- [ ] ❌ "Copy this section" instructions (violates DRY)

## Correct SSOT Pattern

✅ Good:

- Master file defines full rule
- Other files: `> **SSOT**: See [master.md](path) for details`
- Changes only needed in one place
```


---

## API/Tool Query Check

⚠️ **Critical for external data retrieval.** Prevent false assumptions from incomplete results.

| Anti-Pattern | Problem | Solution |
| --- | --- | --- |
| False Negative Assumption | Treating "no results" as "nothing exists" | Re-query with explicit parameters |
| Range Query Overconfidence | Week-range query misses specific days | Query each day individually |
| Format Assumption | Output format differs from user expectation | Confirm format before output |

### Detection Patterns

- [ ] ❌ "No meetings found" → "Calendar is empty"
- [ ] ❌ Querying week-range without day-by-day verification
- [ ] ❌ Outputting without confirming user's preferred format

### Correct Patterns

- [ ] ✅ If results seem incomplete → Re-query with specific date/criteria
- [ ] ✅ For multi-day ranges → Query each day individually
- [ ] ✅ Ask for output format preference before generating final output
