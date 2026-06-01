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

- Review missing required fields and unsupported properties separately. Missing-field-only checks miss real validation failures.
- If repo-local authoring rules disagree with the current platform support matrix, treat that as contract drift and fix the rule before bulk-editing prompts.
- When possible, verify support mechanically with the local validator or current product docs instead of assuming one repo's convention is authoritative.

- The opening `---` must be the very first bytes in the file. Any stray characters or BOM-like garbage before it can prevent the prompt from being discovered in the slash prompt picker.
- `agent` is optional for `.prompt.md`. If omitted, VS Code uses the current agent/mode. Use `agent: agent` when a prompt must consistently run in Agent mode, or `agent: <custom-agent-name>` when it should bind to a specific custom agent. Use `agent: ask` or `agent: plan` only when the prompt should avoid autonomous edit/execute behavior.

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

Use `agent:` only when the prompt should consistently route through a specific built-in mode or custom agent role. Otherwise omit it.

### `agent` / `model` decision rules for `.prompt.md`

- Use `agent: agent` for execution prompts that are expected to edit files, run tests, use tools, or continue autonomously even when invoked from another chat mode.
- Use `agent: <custom-agent-name>` when the prompt depends on that custom agent's persona, tool restrictions, handoffs, or subagent policy.
- Omit `agent` when the prompt should respect the user's currently selected chat mode or agent.
- Omit `model` unless you have verified the exact model display name in the current environment and intentionally want to pin or provide an ordered fallback. Model names change; stale `model:` values create portability friction.
- Do not use `mode:` in new prompt files. It is deprecated; use `agent:` or omit the field.

### When to use `agent` and `tools`

Both `agent` and `tools` are **restrictive** by default. Specifying them narrows what the prompt can do.

| Field   | Effect when present                                         | Effect when absent                              |
| ------- | ----------------------------------------------------------- | ----------------------------------------------- |
| `agent` | Routes execution through that built-in mode or custom agent | Uses the current agent/mode                     |
| `tools` | **Only** listed tools are available during execution        | All tools the selected/current agent can access |

**Design rule**: Use these fields only when you want to _restrict_, not to _describe_.

- General-purpose prompts that may need web search, doc fetch, file editing, terminal, etc. → **omit both**
- Security-sensitive prompts that must not touch files or run commands → specify `tools` to allowlist
- Prompts that need a specialist persona or delegation boundary → specify `agent`

**Common mistake**: Listing tools you expect to use (e.g. `tools: [edit/editFiles, execute/runInTerminal]`) on a general prompt. This silently blocks web search, doc retrieval, and other tools the task may need at runtime.

In VS Code, prompt-level `tools:` can also surface as a current-chat-session-only tools configuration in the picker. If a global Agent tool set appears to shrink after running a slash prompt, check the prompt file's frontmatter first.

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
