# Prompt Composition Template

Use a minimal, high-signal prompt structure. Keep only what the task needs.

## Template

```markdown
# Objective

- Do: [what to do]
- Don't: [what to avoid]

# Input

- Data: [files, text, or references]
- Assumptions: [constraints or environment]

# Output Format

- Format: [bullet list / JSON / table]
- Length: [max items / max tokens]

# Examples (1–3 representative)

- Example 1: [input → output]
  - Note: Explain why this is a good example

# Validation Criteria

- Test: [test name or procedure]
- Expected: [exact pass condition]
- Fail: [what to do on failure]

# Escape Hatch

- If missing or uncertain, return: "Not found" (or specified fallback)

# Additional Context

- Only the minimum needed context
```

## Usage Guidelines

- **Objective**: Always start with clear Do/Don't boundaries
- **Examples**: 1-3 representative examples are more effective than lengthy explanations
- **Validation**: Define measurable success criteria upfront
- **Escape Hatch**: Prevent hallucination by providing explicit fallback behavior
- **description (REQUIRED)**: Every `.prompt.md` must have a `description` in YAML frontmatter — it appears in the VS Code prompt picker UI and helps both humans and AI identify the prompt's purpose

```yaml
---
description: One-line summary of what this prompt does
---
```

## Frontmatter Constraints

VS Code validates frontmatter strictly. Only use supported fields — unsupported fields cause validation errors.

- The opening `---` must be the very first bytes in the file. Any stray characters or BOM-like garbage before it can prevent the prompt from being discovered in the slash prompt picker.
- `agent` is optional for `.prompt.md`. If you use it, the value must match a real registered agent name. Do not use placeholders such as `agent: agent`.

| File type          | Supported fields                                                  | Notes                                                       |
| ------------------ | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| `.prompt.md`       | `agent`, `argument-hint`, `description`, `model`, `name`, `tools` | `author`, `copyright`, `license` etc. are **NOT** supported |
| `.instructions.md` | `applyTo`                                                         | All other fields are **NOT** supported                      |
| `.skill.md`        | `name`, `description`, `license`, `metadata`                      | Supports nested `metadata:` block                           |

### Recommended `.prompt.md` frontmatter shapes

Keep prompt frontmatter minimal unless a bound agent, model, or tool restriction is required.

```yaml
---
description: "Summarize selected logs into a markdown incident report"
---
```

```yaml
---
description: "Generate test cases for selected code"
agent: reviewer
argument-hint: path or selected code context
---
```

```yaml
---
description: "Investigate issue history using GitHub and web search"
agent: researcher
tools: [search, web]
---
```

Use `agent:` only when the prompt should consistently route through a specific agent role. Otherwise omit it.

### Tool priority

When both a prompt and a referenced custom agent define tools, the prompt-level tool configuration wins.

Use that sparingly. If the prompt always needs a narrower tool set than the agent, it may be a sign that the agent boundary is wrong.

**Workaround for custom metadata** (author, copyright, repository, license):  
Use HTML comments — they are ignored by the validator but preserved in the file.

```markdown
---
description: "What this prompt does"
---

<!-- author: yourname -->
<!-- repository: https://github.com/org/repo -->
<!-- license: CC BY-NC-SA 4.0 -->
<!-- copyright: Copyright (c) 2025 yourname -->
```

If a prompt does not need a specific sub-agent binding, omit `agent` entirely and keep the frontmatter minimal.

## Prompt vs Skill vs Agent

Use a prompt when the task is a single focused request with parameterized input.

| Need                                    | Best fit |
| --------------------------------------- | -------- |
| One focused task                        | Prompt   |
| Multi-step workflow with bundled assets | Skill    |
| Specialist role or tool boundary        | Agent    |

Quick check:

- If you are writing a reusable task sentence, start with a prompt
- If you need scripts, templates, or references, move to a skill
- If the behavior depends on role isolation or tool restriction, use an agent

## Minimal Template (Quick Use)

```markdown
# Task

[One sentence objective]

# Input

[Data source]

# Output

[Format: JSON/Markdown/etc.]
[Max length if applicable]

# Example

Input: [x] → Output: [y]
```
