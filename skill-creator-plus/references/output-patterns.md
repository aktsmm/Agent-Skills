# Output Patterns

Use these patterns when skills need to produce consistent, high-quality output.

## Template Pattern

Provide templates for output format. Match the level of strictness to your needs.

**For strict requirements (like API responses or data formats):**

```markdown
## Report structure

ALWAYS use this exact template structure:

# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```

**For flexible guidance (when adaptation is useful):**

```markdown
## Report structure

Here is a sensible default format, but use your best judgment:

# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]

## Recommendations
[Tailor to the specific context]

Adjust sections as needed for the specific analysis type.
```

## Examples Pattern

For skills where output quality depends on seeing examples, provide input/output pairs:

```markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

Follow this style: type(scope): brief description, then detailed explanation.
```

Examples help Claude understand the desired style and level of detail more clearly than descriptions alone.

## Comparison and Mode Selection Tables

Use a comparison table when the user must choose between multiple valid paths before execution.

Good fit:

- setup mode selection
- browser or provider choice
- local vs remote execution
- attached vs managed workflows

Recommended columns:

| Mode | Best For | Pros | Cons |
| ---- | -------- | ---- | ---- |
| Default mode | Most users | Low setup cost | Less control |
| Advanced mode | Existing environment reuse | More flexible | More prerequisites |

This is better than prose when the agent needs to surface trade-offs quickly.

## Output Pairs and Variant Naming

Use an output pair when the workflow should leave both a source artifact and a publishable artifact.

Example:

```text
name.ext
name-rendered.ext
name-ja.ext
name-en.ext
```

Add a short rule block near the example:

- Keep editable and publishable outputs aligned
- Prefer predictable suffixes over ad hoc filenames
- Do not overwrite language or format variants

This pattern is useful when downstream docs, embeds, or reviews depend on stable filenames.

## Signal Detection Tables

Use a detection table when the output is a review, audit, or classification result.

Recommended columns:

| Category | Signal | Action |
| -------- | ------ | ------ |
| Style | Repeated filler phrase | Remove or rewrite |
| Structure | Same opener repeated 3 times | Vary sentence shape |

Why it works:

- Keeps the scan criteria explicit
- Ties each detection to a concrete next action
- Scales better than a long unordered bullet list

## Quality Gates and Score Bands

When a skill needs retry or escalation logic, define the gate in the output contract.

```markdown
## Quality gate

| Score | Action |
| ----- | ------ |
| 90-100 | Proceed |
| 70-89 | Fix and retry |
| 50-69 | Simplify |
| 0-49 | Ask user |
```

Use this pattern when you want the model to stop looping and make a clear next decision.

## Architecture and Data Flow Sketches

If the output explains a multi-stage pipeline, add a compact ASCII flow before the detailed steps.

```text
Input
	-> Normalize
	-> Classify
	-> Transform
	-> Output
	-> Fallback branch
```

This is worth including when the workflow has more than 3 transformations, or when fallback/quarantine paths matter.

## Pattern Selection Heuristic

Use the lightest structure that removes ambiguity.

| Need | Pattern |
| ---- | ------- |
| Strict final document shape | Template Pattern |
| Multiple valid setup paths | Comparison Table |
| Review or audit output | Signal Detection Table |
| Retry threshold | Quality Gate |
| Multi-stage transformation | Architecture Sketch |

If a section can be understood from 2 short bullets, do not add a table just to make it look structured.
