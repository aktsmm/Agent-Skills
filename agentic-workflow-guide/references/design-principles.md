# Design Principles

A collection of principles for designing agent workflows.

## Table of Contents

- [Tier 1: Core Principles](#tier-1-core-principles-essential) - SSOT, SRP, Simplicity First, Fail Fast, Iterative, Feedback Loop
- [Tier 2: Quality Principles](#tier-2-quality-principles-recommended) - Transparency, Gate/Checkpoint, DRY, ISP, Idempotency, Observability, Reasoning
- [IR Architecture](#intermediate-representation-ir-architecture) - Two-stage pattern (reference)
- [Tier 3: Scale Principles](#tier-3-scale-principles-advanced) - Human-in-the-Loop, KISS, Loose Coupling, Graceful Degradation
- [ACI Design](#aci-design-agent-computer-interface) - Tool design guidelines
- [File Organization](#file-organization-principles) - Instructions organization, naming conventions

---

## Tier 1: Core Principles (Essential)

### 1. SSOT (Single Source of Truth)

**Manage information in one place**

| Aspect                   | Description                                          |
| ------------------------ | ---------------------------------------------------- |
| **Definition**           | Don't define the same information in multiple places |
| **Workflow Application** | Centralize context, configuration, and state         |
| **Violation Example**    | Each agent maintains the same settings separately    |
| **Solution**             | Use shared context or configuration files            |

### 2. SRP (Single Responsibility Principle)

**1 Agent = 1 Responsibility**

| Aspect                   | Description                                       |
| ------------------------ | ------------------------------------------------- |
| **Definition**           | Each agent focuses on a single responsibility     |
| **Workflow Application** | Clearly separate tasks and assign to each agent   |
| **Violation Example**    | One agent handles "search + analysis + reporting" |
| **Solution**             | Split agents by role                              |

### 3. Simplicity First

**Start with the simplest solution**

| Aspect                   | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| **Definition**           | Keep complexity to what's necessary and sufficient             |
| **Workflow Application** | Try with a single agent first. Add complexity only when needed |
| **Violation Example**    | Designing a 10-agent workflow from the start                   |
| **Solution**             | Start minimal, extend gradually                                |

**Anthropic's Recommendation:**

> "Start with simple prompts, optimize them with comprehensive evaluation, and add multi-step agentic systems only when simpler solutions fall short."

### 4. Fail Fast

**Detect and fix errors early**

| Aspect                   | Description                                       |
| ------------------------ | ------------------------------------------------- |
| **Definition**           | Detect errors early and handle immediately        |
| **Workflow Application** | Validate at each step, stop immediately if issues |
| **Violation Example**    | Ignoring errors and continuing to the end         |
| **Solution**             | Set up Gates/Checkpoints                          |

### 5. Iterative Refinement

**Build small, improve repeatedly**

| Aspect                   | Description                                           |
| ------------------------ | ----------------------------------------------------- |
| **Definition**           | Prefer small improvements over large changes          |
| **Workflow Application** | MVP → verify → feedback → improve                     |
| **Violation Example**    | Implementing all features at once, testing at the end |
| **Solution**             | Implement and verify one task at a time               |

**Related Pattern:** Evaluator-Optimizer

### 6. Feedback Loop

**Verify results at each step → adjust**

| Aspect                   | Description                                        |
| ------------------------ | -------------------------------------------------- |
| **Definition**           | Get feedback from execution results, apply to next |
| **Workflow Application** | Evaluate agent output, re-execute if needed        |
| **Violation Example**    | One-way flow without result verification           |
| **Solution**             | Incorporate evaluation steps                       |

**Anthropic's Recommendation:**

> "During execution, it's crucial for the agents to gain 'ground truth' from the environment at each step to assess its progress."

---

## Tier 2: Quality Principles (Recommended)

### 7. Transparency

**Show plans and progress explicitly**

| Aspect                   | Description                                        |
| ------------------------ | -------------------------------------------------- |
| **Definition**           | Make what's happening visible                      |
| **Workflow Application** | Show start/end of each step, display progress      |
| **Violation Example**    | Black box with no visibility into what's happening |
| **Solution**             | Use logs, progress display, TodoWrite              |

**Anthropic's Recommendation:**

> "Prioritize transparency by explicitly showing the agent's planning steps."

### 8. Gate/Checkpoint

**Validation gates at each step**

| Aspect                   | Description                                   |
| ------------------------ | --------------------------------------------- |
| **Definition**           | Validate before proceeding to the next step   |
| **Workflow Application** | Don't proceed unless quality criteria are met |
| **Violation Example**    | Passing through all steps without validation  |
| **Solution**             | Quality checks with conditional branching     |

### 9. DRY (Don't Repeat Yourself)

**Eliminate duplication, promote reuse**

| Aspect                   | Description                                |
| ------------------------ | ------------------------------------------ |
| **Definition**           | Don't repeat the same logic                |
| **Workflow Application** | Template common processes, reuse prompts   |
| **Violation Example**    | Copy-pasting the same prompt to each agent |
| **Solution**             | Create common prompt templates             |

### 10. ISP (Interface Segregation Principle)

**Minimal context only**

| Aspect                   | Description                                    |
| ------------------------ | ---------------------------------------------- |
| **Definition**           | Pass only necessary information to each agent  |
| **Workflow Application** | Excessive context becomes noise                |
| **Violation Example**    | Passing all information to all agents          |
| **Solution**             | Select and pass only task-relevant information |

### 11. Idempotency

**Safe to retry**

| Aspect                   | Description                                               |
| ------------------------ | --------------------------------------------------------- |
| **Definition**           | Same operation produces same result regardless of retries |
| **Workflow Application** | Design to allow retries on failure                        |
| **Violation Example**    | Retrying causes data duplication                          |
| **Solution**             | State checking, use unique IDs                            |

### 13. No Hallucination (Anti-Fabrication)

**Don't guess, don't lie, don't fabricate**

| Aspect                   | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| **Definition**           | Never output information that cannot be verified by sources    |
| **Workflow Application** | If unsure, state "not found in official docs" and ESCALATE     |
| **Violation Example**    | Generating fake URLs, dates, or feature descriptions           |
| **Solution**             | Return `status=not_found` instead of guessing                  |

**Detection Patterns:**
- Citing non-existent URLs or sources
- Describing features not in official documentation
- Using phrases like "probably" or "likely" as facts
- Filling knowledge gaps with fabricated information

**Correct Responses When Uncertain:**

| Situation                      | ✅ Correct Response                                    | ❌ Prohibited                        |
| ------------------------------ | ----------------------------------------------------- | ----------------------------------- |
| Not in official docs           | "Not explicitly documented. Recommend official inquiry" | Guess or assume                    |
| Partial information only       | State known parts, mark unknowns explicitly            | Fabricate missing parts            |
| Search returns no results      | Return `status=not_found` and ESCALATE                 | Generate from memory               |


### 12. Observability

**Record decisions and make progress visible**

| Aspect                   | Description                                              |
| ------------------------ | -------------------------------------------------------- |
| **Definition**           | Make agent decisions and progress traceable              |
| **Workflow Application** | Log key decisions as Issue comments, files, or documents |
| **Violation Example**    | No visibility into why agent made a decision             |
| **Solution**             | Decision logs, regular status reports for long tasks     |

**Decision Log Example:**

```markdown
| Time  | Decision                      | Rationale                  |
| ----- | ----------------------------- | -------------------------- |
| 10:00 | Delegate to @impl for task-01 | Code change required       |
| 10:05 | Skip task-02                  | File already up-to-date    |
| 10:10 | Escalate to human             | Requires production access |
```

### 13. Reasoning Before Conclusions

**Show your thinking, then provide the answer**

| Aspect                   | Description                                            |
| ------------------------ | ------------------------------------------------------ |
| **Definition**           | Generate reasoning steps before jumping to conclusions |
| **Workflow Application** | Use chain-of-thought prompting, allow "scratch space"  |
| **Violation Example**    | Agent provides answer without explaining logic         |
| **Solution**             | Structure prompts to encourage step-by-step reasoning  |

**Why This Matters:**

LLMs perform better when they can "think out loud" before committing to an answer. This principle improves accuracy and makes agent decisions auditable.

**Prompt Design:**

✅ **Encourage reasoning:**

```markdown
Before selecting a workflow pattern:

1. Analyze the task characteristics
2. List applicable patterns with pros/cons
3. Recommend the best fit based on your analysis
```

❌ **Discourage reasoning:**

```markdown
Select the best workflow pattern for this task.
```

**Implementation Techniques:**

| Technique                  | Description                               |
| -------------------------- | ----------------------------------------- |
| **Chain-of-Thought (CoT)** | Prompt: "Let's think step by step..."     |
| **Scratch Space**          | Allow working area for calculations/notes |
| **Explicit Steps**         | Require "Analysis → Options → Decision"   |
| **Self-Verification**      | Ask agent to check its own reasoning      |

**Example Output:**

```markdown
## Analysis

- Task requires processing 10 files
- Files are independent
- No interdependencies detected

## Options Considered

1. Prompt Chaining: ❌ Sequential would be slow
2. Parallelization: ✅ Files are independent
3. Orchestrator-Workers: ⚠️ Overkill for fixed task count

## Decision

Use Parallelization pattern (Pattern 3)

## Implementation Plan

[Detailed steps...]
```

**Benefits:**

| Benefit             | Description                                     |
| ------------------- | ----------------------------------------------- |
| **Higher Accuracy** | Reduces hallucination and logical errors        |
| **Debuggability**   | Trace reasoning when output is wrong            |
| **Transparency**    | Users understand why agent chose action         |
| **Self-Correction** | Agent catches its own mistakes during reasoning |

**References:**

- [Chain-of-Thought Prompting - Google Research](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)
- [vscode-ai-toolkit Prompt Generation Best Practices](https://github.com/microsoft/vscode-ai-toolkit)

---

## Intermediate Representation (IR) Architecture

→ **[workflow-patterns/ir-architecture.md](workflow-patterns/ir-architecture.md)** (SSOT)

For complex workflows, use a two-stage architecture with an intermediate representation.
Core principle: **Same IR → Same Output.** No creativity in transformation phase.


### 14. No Hallucination (Anti-Fabrication)

**Don't guess, don't lie, don't fabricate**

| Aspect                   | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| **Definition**           | Never output information that cannot be verified by sources    |
| **Workflow Application** | If unsure, state "not found in official docs" and ESCALATE     |
| **Violation Example**    | Generating fake URLs, dates, or feature descriptions           |
| **Solution**             | Return status=not_found instead of guessing                    |

**Detection Patterns:**
- Citing non-existent URLs or sources
- Describing features not in official documentation
- Using phrases like "probably" or "likely" as facts
- Filling knowledge gaps with fabricated information

**Correct Responses When Uncertain:**

| Situation                      | Correct Response                                       | Prohibited                          |
| ------------------------------ | ----------------------------------------------------- | ----------------------------------- |
| Not in official docs           | "Not explicitly documented. Recommend official inquiry" | Guess or assume                    |
| Partial information only       | State known parts, mark unknowns explicitly            | Fabricate missing parts            |
| Search returns no results      | Return status=not_found and ESCALATE                   | Generate from memory               |


### 14. No Hallucination (Anti-Fabrication)

**Don't guess, don't lie, don't fabricate**

| Aspect                   | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| **Definition**           | Never output information that cannot be verified by sources    |
| **Workflow Application** | If unsure, state "not found in official docs" and ESCALATE     |
| **Violation Example**    | Generating fake URLs, dates, or feature descriptions           |
| **Solution**             | Return status=not_found instead of guessing                    |

**Detection Patterns:**
- Citing non-existent URLs or sources
- Describing features not in official documentation
- Using phrases like "probably" or "likely" as facts
- Filling knowledge gaps with fabricated information

**Correct Responses When Uncertain:**

| Situation                      | Correct Response                                       | Prohibited                          |
| ------------------------------ | ----------------------------------------------------- | ----------------------------------- |
| Not in official docs           | "Not explicitly documented. Recommend official inquiry" | Guess or assume                    |
| Partial information only       | State known parts, mark unknowns explicitly            | Fabricate missing parts            |
| Search returns no results      | Return status=not_found and ESCALATE                   | Generate from memory               |


### 14. No Hallucination (Anti-Fabrication)

**Don't guess, don't lie, don't fabricate**

| Aspect                   | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| **Definition**           | Never output information that cannot be verified by sources    |
| **Workflow Application** | If unsure, state "not found in official docs" and ESCALATE     |
| **Violation Example**    | Generating fake URLs, dates, or feature descriptions           |
| **Solution**             | Return status=not_found instead of guessing                    |

**Detection Patterns:**
- Citing non-existent URLs or sources
- Describing features not in official documentation
- Using phrases like "probably" or "likely" as facts
- Filling knowledge gaps with fabricated information

**Correct Responses When Uncertain:**

| Situation                      | Correct Response                                       | Prohibited                          |
| ------------------------------ | ----------------------------------------------------- | ----------------------------------- |
| Not in official docs           | "Not explicitly documented. Recommend official inquiry" | Guess or assume                    |
| Partial information only       | State known parts, mark unknowns explicitly            | Fabricate missing parts            |
| Search returns no results      | Return status=not_found and ESCALATE                   | Generate from memory               |

---

## Tier 3: Scale Principles (Advanced)

### 14. Human-in-the-Loop

**Human confirmation at critical points**

| Aspect                   | Description                                          |
| ------------------------ | ---------------------------------------------------- |
| **Definition**           | Balance automation with human judgment               |
| **Workflow Application** | Confirm before important decisions, risky operations |
| **Application Example**  | Before production deploy, before mass deletion       |

### 15. KISS (Keep It Simple, Stupid)

**Keep it simple**

| Aspect                   | Description                                      |
| ------------------------ | ------------------------------------------------ |
| **Definition**           | Avoid unnecessary complexity                     |
| **Workflow Application** | Sufficient number of agents, simple coordination |

### 16. Loose Coupling

**Loose coupling between agents**

| Aspect                   | Description                             |
| ------------------------ | --------------------------------------- |
| **Definition**           | Minimize dependencies between agents    |
| **Workflow Application** | Each agent can operate independently    |
| **Benefits**             | Limit impact of changes, easier testing |

### 17. Graceful Degradation

**Continue operation despite partial failures**

| Aspect                   | Description                                    |
| ------------------------ | ---------------------------------------------- |
| **Definition**           | Maintain overall function even when parts fail |
| **Workflow Application** | Fallback processing, skippable steps           |

---

## ACI Design (Agent-Computer Interface)

**Anthropic's Recommendation:**

> "Think about how much effort goes into human-computer interfaces (HCI), and plan to invest just as much effort in creating good agent-computer interfaces (ACI)."

### Core Principles

| Principle                  | Description                                            |
| -------------------------- | ------------------------------------------------------ |
| **Minimal Overlap**        | Each tool has a distinct, non-overlapping purpose      |
| **Self-Contained**         | Tools are robust to errors and handle edge cases       |
| **Clear Intent**           | Tool name and description unambiguously convey purpose |
| **Model-Friendly Formats** | Output formats are easy for LLMs to parse and use      |

### Tool Design Guidelines

1. **Clear Description** - Clarify tool purpose and usage
2. **Edge Cases** - Document boundary conditions
3. **Input Format** - Specify expected input format
4. **Error Handling** - Define behavior on failure
5. **Testing** - Actually use it and iterate
6. **Example Usage** - Include usage examples in description
7. **Poka-yoke** - Design to prevent mistakes (e.g., use absolute paths)

### Format Selection

Choose formats that minimize cognitive load for LLMs:

| Good Format                 | Avoid                              |
| --------------------------- | ---------------------------------- |
| Markdown code blocks        | JSON with escaped strings          |
| Absolute file paths         | Relative paths (context-dependent) |
| Structured sections         | Free-form text with implicit rules |
| Clear delimiters (XML tags) | Ambiguous separators               |

### Anthropic's Tool Format Recommendations

> "Give the model enough tokens to 'think' before it writes itself into a corner. Keep the format close to what the model has seen naturally occurring in text on the internet."

**Do:**

- Use formats the model has seen in training (Markdown, code, XML)
- Allow space for reasoning before final output
- Use descriptive parameter names

**Don't:**

- Require accurate counting (e.g., line numbers in diffs)
- Force heavy escaping (e.g., code inside JSON strings)
- Create ambiguous decision points between similar tools

### Tool Set Design

| Symptom                       | Problem                        | Solution                         |
| ----------------------------- | ------------------------------ | -------------------------------- |
| User unsure which tool to use | Overlapping functionality      | Consolidate or clearly delineate |
| Frequent tool misuse          | Unclear descriptions           | Improve docs, add examples       |
| Verbose tool outputs          | Wasted context tokens          | Return summaries, not raw data   |
| Error-prone inputs            | Complex parameter requirements | Simplify, use defaults           |

### Testing Checklist

```markdown
- [ ] Can a junior developer understand how to use this tool from its description?
- [ ] Does running multiple test inputs produce expected outputs?
- [ ] Are error messages actionable?
- [ ] Is the output format consistent and parseable?
- [ ] Does the tool handle edge cases gracefully?
```

---

## File Organization Principles

### Instructions Organization

**Group related instructions by domain/genre**

| Aspect                   | Description                                               |
| ------------------------ | --------------------------------------------------------- |
| **Definition**           | Organize instruction files into logical folder categories |
| **Workflow Application** | Categorize `.github/instructions/` by domain              |
| **Violation Example**    | All files flat in one directory                           |
| **Solution**             | Create genre-based folders (azure/, git/, skills/, etc.)  |

**Why This Matters:**

- Easier navigation for both humans and agents
- Related instructions stay together
- Reduces cognitive load when searching
- Enables folder-level `.gitignore` or permissions

**Recommended Structure:**

```
.github/instructions/
├── azure/
│   ├── bicep-style.instructions.md
│   ├── naming-conventions.instructions.md
│   └── resource-tagging.instructions.md
├── git/
│   ├── commit-message.instructions.md
│   ├── branch-naming.instructions.md
│   └── pr-contribution.instructions.md
├── code/
│   ├── python-style.instructions.md
│   ├── typescript-style.instructions.md
│   └── testing-guidelines.instructions.md
├── skills/
│   └── skill-creator.instructions.md
└── global.instructions.md  # Cross-cutting rules
```

**Benefits:**

| Benefit              | Description                                         |
| -------------------- | --------------------------------------------------- |
| **Discoverability**  | Find related files quickly                          |
| **Scoped Loading**   | Load only relevant folder for specific tasks        |
| **Team Ownership**   | Assign folder ownership to domain experts           |
| **Reduced Conflict** | Parallel edits in different folders avoid conflicts |

### Naming Conventions

**Use consistent, descriptive file names**

| Aspect                   | Description                                      |
| ------------------------ | ------------------------------------------------ |
| **Definition**           | Follow predictable naming patterns               |
| **Workflow Application** | File names convey purpose without opening        |
| **Violation Example**    | `notes.md`, `stuff.md`, `doc1.md`                |
| **Solution**             | Use descriptive kebab-case with file type suffix |

#### File Naming Rules

| Rule                    | Good Example                            | Bad Example         |
| ----------------------- | --------------------------------------- | ------------------- |
| **Kebab-case**          | `commit-message.instructions.md`        | `commitMessage.md`  |
| **Include type suffix** | `azure-deploy.instructions.md`          | `azure-deploy.md`   |
| **Be descriptive**      | `pr-contribution-guide.instructions.md` | `pr.md`             |
| **Avoid generic names** | `bicep-naming-conventions.md`           | `conventions.md`    |
| **Use lowercase**       | `github-actions.md`                     | `GitHub-Actions.md` |

#### Suffix Conventions

| Suffix             | Usage                           | Example                       |
| ------------------ | ------------------------------- | ----------------------------- |
| `.instructions.md` | Agent/Copilot instruction files | `code-review.instructions.md` |
| `.prompt.md`       | Reusable prompt templates       | `summarize-pr.prompt.md`      |
| `.agent.md`        | Agent definition files          | `code-reviewer.agent.md`      |
| `.md`              | General documentation           | `architecture-overview.md`    |

#### Folder Naming Rules

| Rule                   | Good Example                          | Bad Example       |
| ---------------------- | ------------------------------------- | ----------------- |
| **Singular or plural** | `skills/` or `skill/` (be consistent) | Mixed usage       |
| **Lowercase**          | `azure/`                              | `Azure/`          |
| **No spaces**          | `code-style/`                         | `code style/`     |
| **Domain-based**       | `infrastructure/`                     | `misc/`, `other/` |

#### Agent/Prompt File Naming

For `.agent.md` and `.prompt.md` files, use action-oriented names:

```
✅ Good:
- code-reviewer.agent.md
- pr-summarizer.agent.md
- test-generator.prompt.md
- refactor-suggestions.prompt.md

❌ Bad:
- agent1.agent.md
- my-agent.agent.md
- prompt.prompt.md
- test.prompt.md
```

#### Versioning in Names (When Needed)

If maintaining multiple versions:

```
feature-flags-v1.instructions.md
feature-flags-v2.instructions.md
```

Or use folders:

```
feature-flags/
├── v1/
│   └── implementation.instructions.md
└── v2/
    └── implementation.instructions.md
```

---

## References

- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Writing tools for AI agents - Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [12-Factor App](https://12factor.net/)





---

## SSOT Implementation Patterns

### SSOT Reference Pattern

When referencing shared definitions across multiple files, use this standard format:

**Format:**
```markdown
> **SSOT**: See [file](path) section "Section Name" for details
```

**Anti-pattern (Before):**
- Same logic duplicated in 3+ files (e.g., holiday check, validation rules)
- Requires updating all files when logic changes
- Inconsistencies emerge over time

**Best Practice (After):**
- Define authoritative rule in one file (e.g., `instructions.md`)
- Other files reference SSOT with link only
- Changes propagate automatically

**Example:**
```markdown
### Step 0-2: Holiday Check

> **SSOT**: See [copilot-instructions.md](../copilot-instructions.md) section "Holiday Rules"

1. Check holiday calendar
2. If holiday: skip and notify
```

### View vs Master Separation

For task/project management workflows, separate display views from data masters:

| File Type | Role | Update Frequency | Content |
|-----------|------|------------------|---------|
| **View (Dashboard)** | Today's top 3 actions | Daily (morning) | Links to Master |
| **Master (active.md)** | All task details (SSOT) | On change | Full task specs |
| **Archive (completed.md)** | Completion history | On task completion | Archived tasks |

> ⚠️ **Anti-pattern**: Putting task tables in both View and Master creates dual maintenance burden.

**Correct Structure:**
```
DASHBOARD.md (View)
├── Today's Focus: TOP 3 actions (links only)
├── This Week: Schedule view
└── Recent Completions: Last 5 items

Tasks/active.md (Master - SSOT)
├── Full task details
├── All metadata
└── History
```

### Activity Log Collection Strategy

When collecting activity logs from integrated tools (M365, Slack, etc.), use multiple query types for comprehensive coverage:

| Query Type | Purpose | Detection Target |
|------------|---------|------------------|
| **My Posts** | What I shared in channels | Knowledge sharing, contributions |
| **Mentions** | Messages that mentioned me | Requests, thanks, dependencies |
| **Files** | Files I shared/edited | Deliverables, documentation |

> ⚠️ **Single query anti-pattern**: Using only one query type causes detection gaps.

**Example queries:**
1. `What did I post in channels today?` → Own contributions
2. `What messages mentioned me today?` → Inbound requests
3. `What files did I share today?` → Artifacts created

