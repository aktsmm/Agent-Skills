# Agent Evaluation

A framework for measuring agent workflow effectiveness based on vscode-ai-toolkit best practices.

## Table of Contents

- [Overview](#overview) - Why evaluation matters
- [Three Core Metrics](#three-core-metrics) - Intent Resolution, Tool Call Accuracy, Task Adherence
- [Evaluation Methodology](#evaluation-methodology) - How to evaluate
- [Evaluation Best Practices](#evaluation-best-practices) - Guidelines for effective evaluation
- [Common Evaluation Pitfalls](#common-evaluation-pitfalls) - Anti-patterns to avoid
- [Evaluation Checklist](#evaluation-checklist) - Quick check template

---

## Overview

Effective agent evaluation goes beyond simple success/fail metrics. It requires assessing the quality of reasoning, tool usage, and task adherence across diverse scenarios.

## Three Core Metrics

### 1. Intent Resolution

**Does the agent correctly understand and fulfill user intent?**

| Aspect               | Description                                          |
| -------------------- | ---------------------------------------------------- |
| **What to Measure**  | Accuracy of understanding user's goal                |
| **Success Criteria** | Agent addresses the actual need, not surface request |
| **Common Failures**  | Misinterpreting ambiguous requests, literal parsing  |

#### Evaluation Questions

- [ ] Did the agent clarify ambiguous requests?
- [ ] Did it address the underlying goal or just the explicit ask?
- [ ] Were edge cases and constraints considered?
- [ ] Did the output match user expectations?

#### Example Scenarios

| User Request         | Poor Intent Resolution               | Good Intent Resolution                    |
| -------------------- | ------------------------------------ | ----------------------------------------- |
| "Fix the bug"        | Changes random code without analysis | Reproduces bug, identifies root cause     |
| "Add authentication" | Implements basic login               | Asks about requirements (OAuth, JWT, etc) |
| "Make it faster"     | Random optimizations                 | Profiles code, targets bottlenecks        |

### 2. Tool Call Accuracy

**Does the agent use tools correctly and efficiently?**

| Aspect               | Description                                       |
| -------------------- | ------------------------------------------------- |
| **What to Measure**  | Correctness and appropriateness of tool selection |
| **Success Criteria** | Right tool, right parameters, right sequence      |
| **Common Failures**  | Wrong tool, hallucinated tools, inefficient usage |

#### Evaluation Questions

- [ ] Did the agent use available tools (not reimplementing)?
- [ ] Were tool parameters correct and complete?
- [ ] Was the tool sequence logical and efficient?
- [ ] Were errors handled gracefully?

#### Common Tool Usage Mistakes

| Mistake                    | Example                                           | Fix                                     |
| -------------------------- | ------------------------------------------------- | --------------------------------------- |
| **Hallucinated Tools**     | Calls `search_web()` when not defined             | Validate tool availability              |
| **Wrong Parameters**       | Passes string when tool expects array             | Strict parameter validation             |
| **Inefficient Chains**     | Reads same file 10 times                          | Cache results, batch operations         |
| **Missing Error Handling** | Continues after tool failure                      | Check return codes, implement fallbacks |
| **Tool Reimplementation**  | Writes grep-like logic instead of using grep tool | Document tool capabilities clearly      |

#### Tool Call Metrics

```markdown
**Accuracy:** (Correct Tool Calls) / (Total Tool Calls)
**Efficiency:** (Optimal Tool Count) / (Actual Tool Count)
**Coverage:** (Tools Used) / (Relevant Tools Available)
```

### 3. Task Adherence

**Does the agent follow instructions and constraints?**

| Aspect               | Description                                   |
| -------------------- | --------------------------------------------- |
| **What to Measure**  | Compliance with explicit and implicit rules   |
| **Success Criteria** | Respects boundaries, doesn't overstep or skip |
| **Common Failures**  | Scope creep, ignoring constraints, shortcuts  |

#### Evaluation Questions

- [ ] Did the agent respect scope boundaries?
- [ ] Were constraints (time, resources, safety) followed?
- [ ] Did it avoid making unauthorized changes?
- [ ] Were deliverables complete per specification?

#### Adherence Violations

| Violation Type        | Example                                     | Impact                    |
| --------------------- | ------------------------------------------- | ------------------------- |
| **Scope Creep**       | Asked to fix bug, refactors entire codebase | Wasted time, new risks    |
| **Constraint Bypass** | Ignores "don't delete files" rule           | Data loss, trust breach   |
| **Premature Action**  | Starts execution before plan approval       | Wasted work, misalignment |
| **Incomplete Output** | Returns half-finished documentation         | User must finish work     |

---

## Evaluation Methodology

### 1. Test Data Generation

**Create diverse, realistic test scenarios**

#### Scenario Categories

| Category             | Description                         | Example                             |
| -------------------- | ----------------------------------- | ----------------------------------- |
| **Happy Path**       | Clear, straightforward requests     | "List files in src/ directory"      |
| **Ambiguous**        | Requires clarification              | "Make it better" (what aspect?)     |
| **Edge Cases**       | Boundary conditions, unusual inputs | Empty repository, large file counts |
| **Error Handling**   | Simulated failures                  | File not found, API timeout         |
| **Multi-Step**       | Complex workflows                   | Analyze → Design → Implement → Test |
| **Constraint-Heavy** | Many restrictions                   | "Refactor but don't change API"     |

#### Test Data Generation Process

Start from 10-20 baseline use cases for the agent's domain and tools, then add phrasing variations, missing or conflicting information, boundary inputs, and simulated tool failures (unavailable, partial, timeout).

#### Example Test Set (Code Review Agent)

```yaml
test_cases:
  - id: "happy-001"
    input: "Review src/auth.py for security issues"
    expected_tools: ["read", "grep"]
    expected_output_type: "security_report"
    success_criteria:
      - Uses #tool:read to access file
      - Identifies security patterns (SQL injection, XSS, etc.)
      - Provides severity ratings

  - id: "ambiguous-001"
    input: "Check this"
    expected_behavior: "Request clarification"
    success_criteria:
      - Asks what to check
      - Offers options (code, tests, docs)
      - Doesn't make assumptions

  - id: "edge-001"
    input: "Review all Python files"
    context: "Repository has 1000+ .py files"
    expected_behavior: "Plan-First approach"
    success_criteria:
      - Creates plan before execution
      - Proposes batching or sampling
      - Estimates time required

  - id: "error-001"
    input: "Review src/nonexistent.py"
    expected_behavior: "Graceful error handling"
    success_criteria:
      - Detects file doesn't exist
      - Informs user clearly
      - Suggests alternatives (similar files, search)
```

### 2. Evaluation Rubric

Score each metric 0-5 instead of pass/fail:

| Score | Intent Resolution                      | Tool Call Accuracy                       | Task Adherence                         |
| ----- | -------------------------------------- | ---------------------------------------- | -------------------------------------- |
| **5** | Correct, with proactive clarification  | Optimal tools and parameters, error-free | Respects all constraints               |
| **3** | Mostly correct, minor misunderstanding | Mostly correct, some suboptimal choices  | Some scope creep or missed constraints |
| **1** | Misunderstood intent, wrong direction  | Wrong or hallucinated tools              | Major violations, ignores instructions |
| **0** | No engagement with the request         | Tool calls fail, agent cannot proceed    | Disregards requirements                |

Scores 4 and 2 are the intermediate levels.

### 3. Automated Testing

**Implement programmatic evaluation where possible**

#### What Can Be Automated

| Aspect                    | Automation Approach                           |
| ------------------------- | --------------------------------------------- |
| **Tool Call Validation**  | Parse logs, check tool names and parameters   |
| **Output Format**         | Schema validation (JSON, YAML)                |
| **File Operations**       | Verify files created/modified as expected     |
| **Performance Metrics**   | Measure execution time, tool call count       |
| **Constraint Violations** | Check against rule list (deleted files, etc.) |

#### Prefer Stable Assertions

Programmatic evaluation is strongest when assertions survive renames, workspace changes, and normal output variation.

Prefer:

- schema or heading checks over long exact-string matches
- tool-usage checks over replaying one transcript verbatim
- stable identifiers (file basenames, declared section names, output schema keys)

Avoid:

- temporary workspace paths
- machine-specific absolute paths
- exact output assertions copied from a single recorded run

#### What Requires Human Review

| Aspect                   | Why Human Needed                              |
| ------------------------ | --------------------------------------------- |
| **Intent Understanding** | Nuanced interpretation of ambiguous requests  |
| **Output Quality**       | Subjective assessment (clarity, completeness) |
| **Creativity**           | Innovation and problem-solving approach       |
| **Edge Case Handling**   | Appropriateness of fallback strategies        |

For tool-call automation, parse the execution log and count total calls, calls to tools outside the expected set (hallucinated), and failed calls.

---

## Evaluation Best Practices

### 1. Establish Baselines

Before making changes, measure current performance:

```markdown
Baseline Evaluation (v1.0)

- Intent Resolution: 3.8/5.0
- Tool Call Accuracy: 4.2/5.0
- Task Adherence: 4.5/5.0

After Optimization (v1.1)

- Intent Resolution: 4.3/5.0 ✅ +13%
- Tool Call Accuracy: 4.6/5.0 ✅ +9.5%
- Task Adherence: 4.4/5.0 ⚠️ -2.2%
```

### 2. Diverse Test Set

Cover all major features with real user phrasing, a range of difficulty, and failure scenarios, not only happy paths.

### 3. Iterative Improvement

Baseline → identify weaknesses → fix → re-evaluate; deploy only on improvement, otherwise try a different approach.

### 4. Log Everything

Per test run, log `test_id`, timestamp, user input, agent plan, each tool call (`tool`, `params`, `status`), output, per-metric scores, and evaluator notes.

Logs are valuable inputs for designing evals, but they should not become the assertion wholesale. Use logs to discover robust checks, then reduce them to stable criteria.

### 5. Continuous Monitoring

**Evaluation isn't one-time; monitor in production**

| Metric                     | Frequency       | Action Threshold            |
| -------------------------- | --------------- | --------------------------- |
| **User Satisfaction**      | After each task | <80% positive → investigate |
| **Tool Call Failures**     | Real-time       | >5% failure rate → alert    |
| **Task Completion Rate**   | Daily           | <90% → review failures      |
| **Average Execution Time** | Weekly          | +20% vs baseline → profile  |

---

## Common Evaluation Pitfalls

| Pitfall                     | Countermeasure                                                    |
| --------------------------- | ----------------------------------------------------------------- |
| Overfitting to the test set | Held-out set; refresh scenarios; add user-reported issues         |
| Ignoring user feedback      | Review real usage logs and qualitative feedback alongside metrics |
| Binary pass/fail            | Graded rubric across multiple dimensions                          |
| Testing only happy paths    | Simulate timeouts, missing resources, malformed inputs            |
| No regression testing       | Keep the suite and rerun it before each release                   |

### Brittle Recorded Evaluations

**Problem:** A recorded test only passes for the original session because it encodes one temporary path or one exact output.

**Solution:**

- Rewrite assertions around structure, tool behavior, or schema
- Replace workspace-specific paths with stable identifiers
- Re-run evaluation after renames to confirm the checks still hold

---

## Evaluation Checklist

Before deploying an agent workflow:

```markdown
- [ ] Created diverse test set (happy, ambiguous, edge, error)
- [ ] Defined success criteria for each test
- [ ] Established baseline metrics
- [ ] Tested all major workflows
- [ ] Verified tool call accuracy
- [ ] Confirmed constraint adherence
- [ ] Assertions rely on stable structure or tool behavior, not one recorded run
- [ ] Logged evaluation results
- [ ] Identified improvement areas
- [ ] Documented known limitations
- [ ] Set up monitoring for production
```

---

## References

- [vscode-ai-toolkit Agent Evaluation](https://github.com/microsoft/vscode-ai-toolkit)
- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Prompt Engineering Guide - OpenAI](https://platform.openai.com/docs/guides/prompt-engineering)
