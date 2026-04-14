---
name: skill-creator-plus
description: Guide for designing and reviewing high-quality Agent Skills, and for deciding when a request should be a skill instead of a prompt, instruction, agent, or hook. Use when creating a new skill, updating an existing skill, reviewing SKILL.md files, or fixing poor skill triggering. Triggers on "create skill", "review skill", "fix skill trigger", "SKILL.md", "スキル作成".
license: Apache-2.0
metadata:
  author: yamapan (based on Anthropic)
---

# Skill Creator+

Design and review Agent Skills that trigger reliably and stay lean.

## Decision Flow

Start by deciding whether the user really needs a skill.

| Need | Use |
| ---- | --- |
| Reusable multi-step workflow with bundled scripts, references, or templates | **Skill** |
| Single focused slash task with parameterized input | **Prompt** |
| Always-on or file-scoped guidance | **Instruction** |
| Persona, tool restrictions, delegation, or handoffs | **Custom Agent** |
| Deterministic enforcement or lifecycle automation | **Hook** |

If the answer is not **Skill**, stop and create the right primitive instead.

→ **[references/customization-primitives.md](references/customization-primitives.md)** for the full selection guide

## When to Use

- **Create skill**, **new skill**, **review skill**, **fix skill trigger**, **SKILL.md**, **スキル作成**
- Creating a new skill from scratch
- Updating or refactoring an existing skill
- Reviewing existing SKILL.md files
- Deciding whether a customization should be a skill before authoring it

## Core Principles

| Principle                  | Description                                                          |
| -------------------------- | -------------------------------------------------------------------- |
| **Concise is Key**         | Context window is shared. Only add what Claude doesn't already know. |
| **Discovery First**        | The description is the routing surface. Triggers must be explicit.   |
| **Degrees of Freedom**     | Match specificity to task fragility (high/medium/low freedom)        |
| **Progressive Disclosure** | Split into 3 levels: Metadata → Body → References                    |
| **Right Primitive**        | A good skill is not a fallback for prompt/agent/instruction design.  |
| **Scope Before File**      | Decide workspace vs profile before creating anything.                |

> **Default assumption:** Claude is already very smart. Challenge each piece: "Does this justify its token cost?"

## Skill Structure

→ **[references/skill-structure.md](references/skill-structure.md)** for locations, frontmatter, and bundled resource rules

```
skill-name/
├── SKILL.md (required)        # Lean overview + decision points
├── scripts/                   # Deterministic helpers
├── references/                # Load on demand
└── assets/                    # Templates and reusable outputs
```

→ See [skill-structure.md > What NOT to Include](references/skill-structure.md#what-not-to-include) for excluded files.

## Creation Process

→ **[references/creation-process.md](references/creation-process.md)** for the end-to-end workflow

| Step | Action                                                  |
| ---- | ------------------------------------------------------- |
| 0    | Choose primitive + scope (skill vs prompt/agent/etc.)   |
| 1    | Understand with concrete examples and trigger phrases   |
| 2    | Plan reusable contents (scripts/references/assets)      |
| 3    | Initialize or refactor the skill folder                 |
| 4    | Write SKILL.md and implement resources                  |
| 5    | Validate frontmatter, structure, and trigger quality    |
| 6    | Test on real prompt patterns and iterate                |

## Frontmatter and Triggering

Use the smallest viable frontmatter.

```yaml
---
name: skill-name
description: "What it does. Use when [trigger conditions]. Triggers on 'keyword', 'phrase'."
argument-hint: "Optional slash-command hint"
user-invocable: true
disable-model-invocation: false
---
```

- `name` must match the folder name
- `description` must say both **what** and **when**
- Optional fields should be intentional, not boilerplate
- Resource links must stay relative and shallow

→ **[references/common-pitfalls.md](references/common-pitfalls.md)** for silent failures and trigger misses

## SKILL.md Guidelines

### Size Target

→ See [skill-review-checklist.md > Line Count Target](references/skill-review-checklist.md#line-count-target) for size guidelines.

**Quick rule:** < 150 lines is good, > 300 lines must split to references.

| ✅ Good                                                                                                                                                                 | ❌ Bad               |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Extract text and tables from PDF files, fill forms, merge documents. **Use when** working with PDF files or when the user mentions PDFs, forms, or document extraction. | Helps with documents |
| Set up book writing workspace. **Triggers on** "book writing", "執筆ワークスペース", "technical writing project".                                                       | Creates workspaces   |

### When to Use Section

Start with **generic keywords** users are likely to say:

```markdown
## When to Use

- **PDF**, **extract text**, **form filling** ← Keywords first
- Processing documents with embedded images
- Filling PDF forms programmatically
```

### Body

- Use imperative/infinitive form
- Link to references for details
- Keep essential workflow only
- Add decision points when misuse is common
- Push reference material out of SKILL.md aggressively

## Review Checklist

→ **[references/skill-review-checklist.md](references/skill-review-checklist.md)**

```markdown
- [ ] SKILL.md under 150 lines?
- [ ] Request truly needs a skill?
- [ ] Description has trigger conditions?
- [ ] Optional frontmatter fields are intentional?
- [ ] Details moved to references/?
- [ ] No README.md or auxiliary docs?
```

## Key References

| Topic            | Reference                                                                    |
| ---------------- | ---------------------------------------------------------------------------- |
| Primitive Choice | [references/customization-primitives.md](references/customization-primitives.md) |
| Skill Structure  | [references/skill-structure.md](references/skill-structure.md)               |
| Creation Process | [references/creation-process.md](references/creation-process.md)             |
| Review Checklist | [references/skill-review-checklist.md](references/skill-review-checklist.md) |
| Common Pitfalls  | [references/common-pitfalls.md](references/common-pitfalls.md)               |
| Workflows        | [references/workflows.md](references/workflows.md)                           |
| Output Patterns  | [references/output-patterns.md](references/output-patterns.md)               |

## Done Criteria

- [ ] Request is confirmed to be a skill, not another primitive
- [ ] Scope is decided before file creation
- [ ] SKILL.md created and under 150 lines
- [ ] Frontmatter has name + description with trigger conditions
- [ ] Optional fields are added only when they change behavior
- [ ] Details moved to references/ (Progressive Disclosure)
- [ ] Review checklist passed
