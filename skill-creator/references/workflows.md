# Workflow Patterns

## Sequential Workflows

For complex tasks, break operations into clear, sequential steps. It is often helpful to give Claude an overview of the process towards the beginning of SKILL.md:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

## Conditional Workflows

For tasks with branching logic, guide Claude through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## Skill Improvement Workflow

When improving an existing skill (not creating from scratch), follow this streamlined workflow:

### When to Improve a Skill

- Users report missing features or unclear instructions
- Skill doesn't trigger when expected (description needs update)
- New best practices should be incorporated
- Agent Instructions section is missing or incomplete

### Improvement Checklist

1. **Review current state**

   - Read SKILL.md and understand current structure
   - Check if Agent Instructions section exists
   - Verify frontmatter description is comprehensive

2. **Identify improvement areas**

   - Missing workflows or use cases
   - Unclear or verbose instructions
   - Outdated references or scripts
   - Missing Agent Instructions for AI behavior

3. **Make targeted changes**

   - Update SKILL.md body (keep under 500 lines)
   - Add/update references/ files for detailed content
   - Update frontmatter description if triggers need improvement

4. **Validate changes**
   - Run `quick_validate.py` to check structure
   - Test skill on real tasks if possible

### Agent Instructions Section

Every skill should include an Agent Instructions section at the end of SKILL.md. This section provides guidance specifically for AI agents (Copilot, Claude, etc.) on how to behave when using the skill.

**Template:**

```markdown
---

## Agent Instructions

> This section provides guidance for AI agents (Copilot, Claude, etc.).

### Workflow

1. [Primary action when skill is triggered]
2. [Secondary actions or fallbacks]
3. [Follow-up suggestions to offer users]

### Output Format

[Describe expected output format, tables, code blocks, etc.]

### Additional Actions

After completing the primary task, suggest:

- [Related command or feature]
- [Alternative approach]
- [Next steps for user]
```

**Key principles for Agent Instructions:**

- Use imperative form ("Do X" not "You should do X")
- Be specific about when to suggest alternatives
- Include fallback behaviors when primary approach fails
- Specify follow-up actions to propose to users
