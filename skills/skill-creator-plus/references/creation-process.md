# Skill Creation Process

Detailed guide for each step of skill creation.

## Overview

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Package the skill (run package_skill.py)
6. Iterate based on real usage

## Step 1: Understanding with Concrete Examples

To create an effective skill, clearly understand concrete examples of how the skill will be used.

**Questions to ask:**

- "What functionality should this skill support?"
- "Can you give some examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

**Tip:** Avoid asking too many questions in a single message. Start with the most important questions.

## Step 2: Planning Reusable Contents

Analyze each example by:

1. Considering how to execute from scratch
2. Identifying helpful scripts, references, and assets

**Examples:**

| Skill          | Analysis                                  | Resource                |
| -------------- | ----------------------------------------- | ----------------------- |
| pdf-editor     | Rotating PDF requires rewriting same code | `scripts/rotate_pdf.py` |
| webapp-builder | Same boilerplate HTML/React each time     | `assets/hello-world/`   |
| big-query      | Re-discovering table schemas each time    | `references/schema.md`  |

## Step 3: Initializing the Skill

Run `init_skill.py` for new skills:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory
- Generates SKILL.md template with frontmatter
- Creates example `scripts/`, `references/`, `assets/` directories

## Step 4: Edit the Skill

### Design Patterns

Consult these guides:

- **Multi-step processes**: See [workflows.md](workflows.md)
- **Output formats**: See [output-patterns.md](output-patterns.md)

### Implement Resources

1. Start with scripts, references, assets identified in Step 2
2. Test scripts by running them
3. Delete unused example files

### Write SKILL.md

**Frontmatter:**

```yaml
---
name: skill-name
description: "What it does. Use when [trigger conditions]."
---
```

**Body:** Write instructions using imperative/infinitive form.

## Step 5: Packaging

```bash
scripts/package_skill.py <path/to/skill-folder>
# Optional: specify output directory
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The script:

1. **Validates** - YAML format, naming, structure, description quality
2. **Packages** - Creates `.skill` file (zip with .skill extension)

## Step 6: Iterate

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify needed updates
4. Implement changes and test again
