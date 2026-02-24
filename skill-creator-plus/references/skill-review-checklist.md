# SKILL.md Review Checklist

Checklist for reviewing and improving SKILL.md files.

## Quick Check (5 items)

```markdown
- [ ] SKILL.md is under 150 lines? (GitHub guideline: "2 pages or less")
- [ ] Frontmatter has name + description only?
- [ ] Description clearly states WHEN to use (trigger conditions)?
- [ ] Detailed content moved to references/ (Progressive Disclosure)?
- [ ] No README.md or auxiliary docs in skill folder?
```

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

### Body Structure

| Section          | Required      | Notes                      |
| ---------------- | ------------- | -------------------------- |
| `# Title`        | ✅            | Match skill name           |
| `## When to Use` | ✅            | Trigger conditions (brief) |
| Core workflow    | ✅            | Main instructions          |
| `## References`  | If applicable | Links to references/ files |

### What NOT to Include

→ See [skill-structure.md > What NOT to Include](skill-structure.md#what-not-to-include) for the complete list.

## References Organization

### When to Create references/

| Condition                 | Action                       |
| ------------------------- | ---------------------------- |
| Section > 50 lines        | Move to references/          |
| Multiple variants/options | Split by variant             |
| Domain-specific schemas   | Separate reference file      |
| Detailed examples         | Move to references/examples/ |

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

### Issue 3: Duplicate Content

**Symptoms:** Same information in SKILL.md and references/

**Fix:** Information should live in ONE place only. Keep procedural instructions in SKILL.md, move detailed reference material to references/.

### Issue 4: Missing Trigger Conditions

**Symptoms:** Skill doesn't activate when expected

**Fix:** Add specific triggers to description:

- File patterns (`.pdf`, `.agent.md`)
- Task keywords ("extract text", "rotate page")
- Context conditions ("when working with...")

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

### Content

- [ ] Single responsibility (SRP)
- [ ] No duplicate information
- [ ] Examples minimal but sufficient

### Action Items

1. ...
2. ...
```
