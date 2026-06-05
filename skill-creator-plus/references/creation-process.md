# Skill Creation Process

Detailed guide for each step of skill creation.

## Overview

0. Route by skill archetype
1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Package the skill (run package_skill.py)
6. Iterate based on real usage

## Step 0: Route by Skill Archetype

Before writing, check whether the skill fits one primary category. Skills that straddle several categories often become confusing.

| Archetype                    | Use When                                                       | Typical Resources                                 |
| ---------------------------- | -------------------------------------------------------------- | ------------------------------------------------- |
| Library / API reference      | Correct usage of an internal library, CLI, SDK, or service API | snippets, API notes, gotchas                      |
| Product verification         | Proving that UI, CLI, or product behavior works                | Playwright drivers, assertions, screenshots, logs |
| Data fetching / analysis     | Pulling from known data sources or monitoring stacks           | query helpers, schema notes, dashboard IDs        |
| Business process automation  | Repeating a team process with formatted output                 | templates, config, append-only run logs           |
| Code scaffolding / templates | Creating framework-specific boilerplate                        | assets, starter files, generators                 |
| Code quality / review        | Finding defects or enforcing review standards                  | checklists, scripts, deterministic linters        |
| CI/CD / deployment           | Building, releasing, monitoring, or rollback workflows         | runbooks, smoke tests, rollout checks             |
| Runbook / debugging          | Starting from symptoms and producing findings                  | symptom maps, query patterns, report templates    |
| Infrastructure operations    | Routine or risky maintenance tasks                             | guardrails, dry-run scripts, confirmation gates   |

If the candidate does not fit one category, split it or choose another primitive before adding scope.

Source inspiration: Anthropic, "Lessons from building Claude Code: how we use skills" - https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills

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
3. Capturing the non-obvious gotchas that caused past failures
4. Deciding how the skill will verify success, especially for UI, CLI, deployment, or data workflows

**Examples:**

| Skill             | Analysis                                            | Resource                     |
| ----------------- | --------------------------------------------------- | ---------------------------- |
| pdf-editor        | Rotating PDF requires rewriting same code           | `scripts/rotate_pdf.py`      |
| webapp-builder    | Same boilerplate HTML/React each time               | `assets/hello-world/`        |
| big-query         | Re-discovering table schemas each time              | `references/schema.md`       |
| checkout-verifier | UI state is misleading without backend confirmation | `scripts/verify_checkout.py` |

Prefer code or structured files when they reduce repeated reasoning:

- `scripts/` for deterministic steps, assertions, or reusable fetch helpers
- `references/` for gotchas, schemas, command maps, and usage patterns
- `assets/` for templates, starter files, or reusable output shapes
- `config.json` when the skill needs user-specific setup such as channels, environments, or default destinations
- append-only logs when previous runs are part of the workflow contract, such as standups or recurring reports
- named skill dependencies only when another installed skill owns a separate responsibility; include a fallback if it may be missing

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

When updating, prefer adding one precise gotcha or one verification helper over broad reminders. The strongest skill updates usually come from observed misses, not generic best practices.

For skills where routing quality matters, optionally track lightweight usage signals:

- manual invocation vs model-triggered invocation
- expected-but-not-triggered cases
- success, fallback, or abandoned outcome
- description or `## When to Use` phrase that needs adjustment

Keep logs append-only and minimal. Do not store full prompts, secrets, personal data, customer data, or machine-specific paths.
