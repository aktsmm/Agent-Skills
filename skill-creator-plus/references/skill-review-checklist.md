# SKILL.md Review Checklist

Checklist for reviewing and improving SKILL.md files.

## Quick Check (5 items)

```markdown
- [ ] SKILL.md is under 150 lines? (GitHub guideline: "2 pages or less")
- [ ] Frontmatter has name + description?
- [ ] Self-authored skills have license + metadata.author?
- [ ] Description clearly states WHEN to use (trigger conditions)?
- [ ] Detailed content moved to references/ (Progressive Disclosure)?
- [ ] No README.md or auxiliary docs in skill folder?
- [ ] The skill fits one primary archetype, or the split is intentional?
- [ ] Non-obvious gotchas are captured where they affect correctness?
- [ ] Success can be verified by scripts, assertions, artifacts, or explicit checks?
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

### Skill Archetype Fit

Before reviewing wording, identify the primary kind of skill:

- Library / API reference
- Product verification
- Data fetching / analysis
- Business process automation
- Code scaffolding / templates
- Code quality / review
- CI/CD / deployment
- Runbook / debugging
- Infrastructure operations

If it claims several at once, split it or move secondary behavior into references. A skill can depend on another skill, but its own responsibility should stay crisp.

### Frontmatter

```yaml
---
name: skill-name # Required
description: "..." # Required - include trigger conditions
license: CC BY-NC-SA 4.0 # Required for self-authored skills
metadata: # Required for self-authored skills
  author: yamapan (https://github.com/aktsmm)
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

### Gotchas and Verification

High-signal skill content is usually specific failure avoidance, not obvious process narration.

Check for:

- common field-name mismatches, API quirks, stale state, or misleading success responses
- verification steps that inspect real state, not just command exit codes
- scripts or assertions for fragile workflows such as UI flows, deployments, data pulls, or interactive CLIs
- setup state such as `config.json` when a missing channel, environment, or destination should trigger a user question

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

### Issue 5: Obvious Guidance Without Gotchas

**Symptoms:** The skill says what any capable agent would already do, but omits the edge cases that caused past failures.

**Fix:** Replace generic advice with specific gotchas, verification checks, or reusable scripts.

Good examples:

- "A UI success banner can appear before backend processing finishes; verify the persisted state."
- "Two systems expose similar request identifiers; document the canonical join key."
- "Append-only history tables need an explicit rule for choosing the active row."

## Review Template

```markdown
## SKILL.md Review: {skill-name}

### Metrics

- [ ] Line count: \_\_\_ (target: < 150)
- [ ] Frontmatter valid: Yes/No
- [ ] Description has triggers: Yes/No
- [ ] Primary archetype: **\_\_**

### Structure

- [ ] Progressive disclosure applied
- [ ] No auxiliary docs (README, CHANGELOG)
- [ ] References properly linked

### Content

- [ ] Single responsibility (SRP)
- [ ] No duplicate information
- [ ] Examples minimal but sufficient
- [ ] Gotchas are specific and actionable
- [ ] Verification path is explicit

### Action Items

1. ...
2. ...
```
