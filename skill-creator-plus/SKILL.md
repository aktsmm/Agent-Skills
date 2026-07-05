---
name: skill-creator-plus
description: Create or review a reusable skill (SKILL.md) that packages a workflow, and decide whether the request should be a skill instead of a prompt, instruction, agent, or hook. Use when creating a new skill, extracting a workflow from a conversation, updating an existing skill, reviewing SKILL.md quality, or fixing weak skill triggering. Triggers on "create skill", "/create-skill", "new skill", "review skill", "fix skill trigger", "SKILL.md", "スキル作成".
argument-hint: "作りたい skill の目的、trigger、入れたい resources"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (based on Anthropic)
---

# Skill Creator+

Design and review reusable skills that trigger reliably and stay lean.

## Decision Flow

Start by deciding whether the user really needs a skill.

| Need                                                                        | Use              |
| --------------------------------------------------------------------------- | ---------------- |
| Reusable multi-step workflow with bundled scripts, references, or templates | **Skill**        |
| Single focused slash task with parameterized input                          | **Prompt**       |
| Always-on or file-scoped guidance                                           | **Instruction**  |
| Persona, tool restrictions, delegation, or handoffs                         | **Custom Agent** |
| Deterministic enforcement or lifecycle automation                           | **Hook**         |

If the answer is not **Skill**, stop and create the right primitive instead.

> 上表は「skill にすべきか」の即時ゲート。primitive 選択の詳細 SSOT は **agentic-workflow-guide** skill。

→ **[references/customization-primitives.md](references/customization-primitives.md)** for the full selection guide

## When to Use

- **Create skill**, **/create-skill**, **new skill**, **review skill**, **fix skill trigger**, **SKILL.md**, **workflow**, **スキル作成**
- Creating a new skill from scratch
- Extracting a repeated workflow from a conversation, incident, or checklist
- Updating or refactoring an existing skill
- Reviewing existing SKILL.md files
- Deciding whether a customization should be a skill before authoring it

## Start Here

1. Extract the workflow you want to package.
2. Clarify only the missing dimensions: target outcome, personal vs workspace scope, checklist vs full workflow.
3. Draft the smallest useful SKILL.md, then move detail into references.

## Core Principles

| Principle                  | Description                                                          |
| -------------------------- | -------------------------------------------------------------------- |
| **Concise is Key**         | Context window is shared. Only add what Claude doesn't already know. |
| **Discovery First**        | The description is the routing surface. Triggers must be explicit.   |
| **Degrees of Freedom**     | Match specificity to task fragility (high/medium/low freedom)        |
| **Progressive Disclosure** | Split into 3 levels: Metadata → Body → References                    |
| **Integrate Before Add**   | Update, merge, or replace existing guidance before appending more.   |
| **Right Primitive**        | A good skill is not a fallback for prompt/agent/instruction design.  |
| **Scope Before File**      | Decide workspace vs profile before creating anything.                |
| **Self-Contained**         | The skill must carry its own knowledge. Bundle into references/scripts; do not just link to workspace files (instructions, memory, ledgers) that die when copied elsewhere. Abstract env-specific values (paths, names) into args/config. |

> **Default assumption:** Claude is already very smart. Challenge each piece: "Does this justify its token cost?"

Before adding a new section, ask whether it can replace an existing rule, move to `references/`, or be dropped as session-specific.

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

| Step | Action                                                |
| ---- | ----------------------------------------------------- |
| 0    | Choose primitive + scope (skill vs prompt/agent/etc.) |
| 1    | Extract the workflow from the conversation or examples |
| 2    | Plan reusable contents (scripts/references/assets)    |
| 3    | Initialize or refactor the skill folder               |
| 4    | Write SKILL.md and implement resources                |
| 5    | Validate frontmatter, structure, and trigger quality  |
| 6    | Test on real prompt patterns and iterate              |

## Clarify if Needed

- What outcome should this skill produce?
- Should it live in workspace scope or personal scope?
- Is a short checklist enough, or does it need a full multi-step workflow?

### Refactor Order

When improving an existing skill, use this order:

1. Delete stale or low-value guidance
2. Merge duplicate rules
3. Move long detail to `references/`
4. Add genuinely missing guidance last

## Frontmatter and Triggering

Use the smallest viable frontmatter: `name`, `description`, and only behavior-changing optional fields. `name` must match the folder and `description` must include trigger conditions.

Frontmatter details and silent failures: [references/common-pitfalls.md](references/common-pitfalls.md)

## SKILL.md Guidelines

Keep `SKILL.md` lean: <150 lines is good, >300 lines must split to references. Start `When to Use` with user phrases, keep essential workflow only, and push long examples / schemas / recipes to references.

Detailed review criteria: [references/skill-review-checklist.md](references/skill-review-checklist.md)

## Iteration Loop

1. Draft the skill and save it.
2. Identify the weakest or most ambiguous parts.
3. Tighten those parts, then summarize what the skill produces and example prompts to try.

## Review Checklist

Use [references/skill-review-checklist.md](references/skill-review-checklist.md). For bloat review, use [references/skill-bloat-review.md](references/skill-bloat-review.md).

## Key References

| Topic             | Reference                                                                        |
| ----------------- | -------------------------------------------------------------------------------- |
| Primitive Choice  | [references/customization-primitives.md](references/customization-primitives.md) |
| Skill Structure   | [references/skill-structure.md](references/skill-structure.md)                   |
| Structure Gallery | [references/skill-structure-gallery.md](references/skill-structure-gallery.md)   |
| Creation Process  | [references/creation-process.md](references/creation-process.md)                 |
| Review Checklist  | [references/skill-review-checklist.md](references/skill-review-checklist.md)     |
| Bloat Review      | [references/skill-bloat-review.md](references/skill-bloat-review.md)             |
| Common Pitfalls   | [references/common-pitfalls.md](references/common-pitfalls.md)                   |
| Workflows         | [references/workflows.md](references/workflows.md)                               |
| Output Patterns   | [references/output-patterns.md](references/output-patterns.md)                   |

## Done Criteria

- [ ] Request is confirmed to be a skill, not another primitive
- [ ] Scope is decided before file creation
- [ ] SKILL.md created and under 150 lines
- [ ] Frontmatter has name + description with trigger conditions
- [ ] Manually used skills have `argument-hint`
- [ ] `user-invocable` is set intentionally
- [ ] Optional fields are added only when they change behavior
- [ ] Details moved to references/ (Progressive Disclosure)
- [ ] Self-Contained: no hard reference to other skills / workspace files; env-specific values (paths, customer names, tenant IDs) abstracted
- [ ] Review checklist passed
