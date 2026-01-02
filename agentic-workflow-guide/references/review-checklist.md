# Review Checklist

Comprehensive review checklist for agent workflows. Includes anti-pattern detection.

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

> "Start with simple prompts, optimize them with comprehensive evaluation, and add multi-step agentic systems only when simpler solutions fall short." — Anthropic

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

## Anti-Pattern Quick Reference

| Anti-Pattern         | Symptom                            | Solution                        |
| -------------------- | ---------------------------------- | ------------------------------- |
| God Agent            | All responsibilities in 1 agent    | Split with SRP                  |
| Context Overload     | Passing excessive unnecessary info | Minimize with ISP               |
| Silent Failure       | Ignoring errors and continuing     | Stop immediately with Fail Fast |
| Infinite Loop        | Loops without termination          | Set maximum iterations          |
| Big Bang             | Building everything at once        | Build small with Iterative      |
| Premature Complexity | Complex design from the start      | Simplicity First                |
| Black Box            | Internal state invisible           | Transparency                    |
| Tight Coupling       | Tight coupling between agents      | Loose Coupling                  |

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
- [workflow-patterns.md](workflow-patterns.md) - Workflow pattern details
- [context-engineering.md](context-engineering.md) - Context management for long tasks
