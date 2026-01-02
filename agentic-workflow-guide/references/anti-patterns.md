# Anti-Patterns

> **Note:** Anti-pattern details have been consolidated into [review-checklist.md](review-checklist.md) to reduce duplication and improve maintainability.

## Quick Reference

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

---

→ **See [review-checklist.md](review-checklist.md)** for:

- Detailed anti-pattern descriptions with code examples
- Detection checklist
- Solutions and fixes

---

### 5. Big Bang

**Building everything at once**

#### Symptoms

```
❌ Bad Example:
1. Complete design for all features
2. Implement all agents at once
3. Test everything at the end
→ Late problem discovery, high fix costs
```

- Implementing everything at once
- Testing is deferred
- Late problem discovery
- Wide scope of fixes

#### Solution

```
✅ Good Example:
1. Design minimum functionality
2. Implement 1 agent
3. Test and verify
4. Add next agent
5. Repeat
```

**Applicable Principle:** Iterative Refinement

---

### 6. Premature Complexity

**Complex design from the start**

#### Symptoms

```
❌ Bad Example:
From the start:
- 10-agent complex workflow
- Complex conditional branching
- Advanced error handling
→ Turned out not to be needed
```

- YAGNI (You Aren't Gonna Need It) violation
- Increased maintenance cost
- Hard to understand

#### Solution

```
✅ Good Example:
1. First try with a single agent
2. Consider splitting if problems occur
3. Add complexity as needed
```

**Applicable Principle:** Simplicity First, YAGNI

**Anthropic's Recommendation:**

> "Start with simple prompts, optimize them with comprehensive evaluation, and add multi-step agentic systems only when simpler solutions fall short."

---

### 7. Black Box

**Internal state invisible**

#### Symptoms

```
❌ Bad Example:
Agent: (Processing without any output...)
User: "What are you doing?"
```

- Progress unknown
- Difficult to identify causes when problems occur
- User feels anxious

#### Solution

```
✅ Good Example:
Agent: "Step 1/3: Fetching data..."
Agent: "Step 2/3: Analyzing..."
Agent: "Step 3/3: Generating report..."
```

**Applicable Principle:** Transparency

---

### 8. Tight Coupling

**Tight coupling between agents**

#### Symptoms

```
❌ Bad Example:
Change Agent A's output format
→ Agents B, C, D all require changes
```

- Wide impact of changes
- Testing is difficult
- Hard to reuse

#### Solution

```
✅ Good Example:
- Standardized interfaces
- Each agent can be tested independently
- Changes are localized
```

**Applicable Principle:** Loose Coupling

---

## Checklist

Verify with this list when designing workflows:

```markdown
- [ ] God Agent: Is too much responsibility packed into one agent?
- [ ] Context Overload: Is excessive context being passed?
- [ ] Silent Failure: Are errors being ignored and continuing?
- [ ] Infinite Loop: Are there loops without termination conditions?
- [ ] Big Bang: Trying to build everything at once?
- [ ] Premature Complexity: Making it more complex than necessary?
- [ ] Black Box: Is internal state invisible?
- [ ] Tight Coupling: Are agents tightly coupled?
```

---

## Related Documents

- [design-principles.md](design-principles.md) - Design principles details
- [review-checklist.md](review-checklist.md) - Review checklist
