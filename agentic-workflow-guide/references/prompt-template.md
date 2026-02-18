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

| File type          | Supported fields                                                  | Notes                                                       |
| ------------------ | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| `.prompt.md`       | `agent`, `argument-hint`, `description`, `model`, `name`, `tools` | `author`, `copyright`, `license` etc. are **NOT** supported |
| `.instructions.md` | `applyTo`                                                         | All other fields are **NOT** supported                      |
| `.skill.md`        | `name`, `description`, `license`, `metadata`                      | Supports nested `metadata:` block                           |

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
