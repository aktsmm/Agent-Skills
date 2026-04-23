# SKILL.md Review Checklist

Checklist for reviewing and improving SKILL.md files.

## Quick Check (5 items)

```markdown
- [ ] SKILL.md is under 150 lines? (GitHub guideline: "2 pages or less")
- [ ] Request really belongs in a skill?
- [ ] Frontmatter is valid and intentional?
- [ ] Description clearly states WHEN to use (trigger conditions)?
- [ ] Detailed content moved to references/ (Progressive Disclosure)?
- [ ] No README.md or auxiliary docs in skill folder?
```

## Bloat Review Order

When a skill feels crowded, review in this order:

1. Delete stale or low-value content
2. Merge duplicate rules
3. Move detail to `references/`
4. Add only what is still missing

→ Use [skill-bloat-review.md](skill-bloat-review.md) when the main issue is append-only growth.

## Size & Structure

### Line Count Target

| Status      | Lines   | Action                   |
| ----------- | ------- | ------------------------ |
| ✅ Good     | < 150   | Maintain                 |
| ⚠️ Warning  | 150-300 | Consider splitting       |
| ❌ Too Long | > 300   | Must split to references |

**Source:** [GitHub Docs - Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)

> "Instructions must be no longer than 2 pages."

### Progressive Disclosure

→ See [skill-structure.md > Progressive Disclosure](skill-structure.md#progressive-disclosure) for the 3-level loading system.

**Pattern: Keep SKILL.md lean, move details to references.**

```
❌ Bad: 400-line SKILL.md with all details inline
✅ Good: 120-line SKILL.md + references/detailed-guide.md
```

### Keep vs Move

| Keep in SKILL.md            | Move to references/     |
| --------------------------- | ----------------------- |
| Trigger conditions          | Large tables            |
| Core workflow               | Long examples           |
| Misuse-prevention decisions | Implementation variants |
| Minimal review gates        | Link collections        |

## Content Quality

### Frontmatter

```yaml
---
name: skill-name # Required
description: "..." # Required - include trigger conditions
license: MIT # Optional
metadata: # Optional
  author: name
---
```

**Description must answer:**

- What does this skill do?
- When should it be triggered?
- Which user phrases should help discovery?

**Optional fields to review intentionally:**

- `argument-hint`
- `user-invocable`
- `disable-model-invocation`

### Body Structure

| Section          | Required      | Notes                       |
| ---------------- | ------------- | --------------------------- |
| `# Title`        | ✅            | Match skill name            |
| `## When to Use` | ✅            | Trigger conditions (brief)  |
| Core workflow    | ✅            | Main instructions           |
| Decision point   | If applicable | Clarify why this is a skill |
| `## References`  | If applicable | Links to references/ files  |

### What NOT to Include

→ See [skill-structure.md > What NOT to Include](skill-structure.md#what-not-to-include) for the complete list.

## References Organization

### When to Create references/

| Condition                 | Action                        |
| ------------------------- | ----------------------------- |
| Section > 50 lines        | Move to references/           |
| Multiple variants/options | Split by variant              |
| Domain-specific schemas   | Separate reference file       |
| Detailed examples         | Move to references/examples/  |
| Primitive-selection logic | Move to a dedicated reference |

### Naming Convention

```
references/
├── {topic}.md           # General pattern
├── {variant-name}.md    # For variants (aws.md, gcp.md)
├── examples/            # Example files
└── schemas/             # Schema definitions
```

## Common Issues

### Issue 1: SKILL.md Too Long

**Symptoms:** > 300 lines, scrolling required to find key info

**Fix:**

1. Identify sections > 50 lines
2. Create `references/{section-name}.md`
3. Replace with summary + link: `→ See [references/{name}.md](references/{name}.md)`

### Issue 2: Vague Description

**Symptoms:** Description says what skill does, not when to use it

**Bad:**

```yaml
description: "Processes PDF files"
```

**Good:**

```yaml
description: "Extract text, rotate pages, and fill forms in PDF files. Use when working with .pdf documents for text extraction, page manipulation, or form automation."
```

### Issue 2b: Wrong Primitive

**Symptoms:** The asset mostly explains prompts, instructions, or agents instead of a reusable skill workflow.

**Fix:** Re-check whether the work belongs in a skill.

### Issue 3: Duplicate Content

**Symptoms:** Same information in SKILL.md and references/

**Fix:** Information should live in ONE place only. Keep procedural instructions in SKILL.md, move detailed reference material to references/.

### Issue 3b: Append-only Growth

**Symptoms:** New sections keep getting added, but old ones are never rewritten.

**Fix:**

1. Check whether the new rule can update an existing section
2. Merge overlapping warnings or checklists
3. Move deep detail out before adding more top-level text
4. Add a new section only if no existing structure can hold it cleanly

### Issue 4: Missing Trigger Conditions

**Symptoms:** Skill doesn't activate when expected

**Fix:** Add specific triggers to description:

- File patterns (`.pdf`, `.agent.md`)
- Task keywords ("extract text", "rotate page")
- Context conditions ("when working with...")

### Issue 5: Silent Invocation Bugs

**Symptoms:** Skill exists but does not load or appears inconsistent.

**Fix:**

1. Confirm `name` matches folder name
2. Quote descriptions containing colons
3. Remove optional frontmatter fields that were copied blindly
4. Verify links are relative

## Review Template

```markdown
## SKILL.md Review: {skill-name}

### Metrics

- [ ] Line count: \_\_\_ (target: < 150)
- [ ] Frontmatter valid: Yes/No
- [ ] Description has triggers: Yes/No

### Structure

- [ ] Progressive disclosure applied
- [ ] No auxiliary docs (README, CHANGELOG)
- [ ] References properly linked
- [ ] No append-only growth smell in main SKILL

### Content

- [ ] Single responsibility (SRP)
- [ ] No duplicate information
- [ ] Examples minimal but sufficient
- [ ] Delete / merge / move considered before add

### Action Items

1. ...
2. ...
```
