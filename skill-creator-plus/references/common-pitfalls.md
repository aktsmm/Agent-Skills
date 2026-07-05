# Common Pitfalls

These issues often cause silent failures or poor skill routing.

## Discovery and Triggering

### Weak Description

Bad descriptions explain what the skill is, but not when it should trigger.

```yaml
description: "Helpful skill for productivity"
```

Prefer explicit trigger phrases and task context.

```yaml
description: "Create and review Agent Skills. Use when creating a new skill, updating SKILL.md, or fixing weak skill triggers."
```

### Missing User Phrases

Add phrases users actually say: file names, verbs, and common shorthand.

- `SKILL.md`
- `create skill`
- `review skill`
- domain-specific phrases

### Method-First Names

Skill names that foreground an implementation detail (tool, input format, intermediate artifact) make slash commands harder to find and reuse. Lead with the user-visible task or outcome; keep techniques in `description` and `## When to Use`.

Example: `review-security-structure` for a security review skill — mention AST, structure maps, call graphs, Source/Sink in description only.

## YAML and Frontmatter

### Unquoted Colons

Descriptions containing colons can break YAML if left unquoted.

```yaml
description: "Use when: reviewing skills"
```

### Name Mismatch

`name` must match the folder name exactly. A mismatch breaks discovery.

### Boilerplate Optional Fields

Do not add `argument-hint`, `user-invocable`, or `disable-model-invocation` unless they change behavior.

### Accidental Prompt Tool Restrictions

In VS Code prompt files, `tools:` is not harmless metadata. It overrides the default agent's enabled tools for that prompt run and can appear in the tools picker as a current-session-only configuration.

Use `tools:` in `*.prompt.md` only when the prompt must deliberately narrow capabilities. If the prompt should inherit the user's normal Agent tools, omit `tools:` entirely.

Prefer custom agents for stable role/tool boundaries. Use prompt-level `tools:` only for narrow slash commands where losing unrelated built-in, extension, or MCP tools is intentional.

## Structure Problems

### Monolithic SKILL.md

If the body grows past the quick-start workflow, move details into `references/`.

### Wrong Primitive

If the content spends most of its space describing prompts, instructions, agents, or hooks, you may be designing the wrong asset.

→ Re-check [customization-primitives.md](customization-primitives.md)

### Deep or Brittle Links

Use relative links and keep referenced files shallow and predictable.

Good:

- `[references/creation-process.md](creation-process.md)` from inside `references/`
- `[references/creation-process.md](references/creation-process.md)` from `SKILL.md`

Avoid absolute paths or workspace-specific locations.

### Brittle Evaluation Assets

Eval files, graders, or review prompts can silently rot when they depend on one recorded session.

Avoid:

- temporary workspace paths
- machine-specific absolute paths
- long exact-string output assertions that encode one specific run

Prefer:

- headings or schema checks
- tool-usage checks
- stable identifiers such as file basenames or declared section names

## Review Smells

- The description cannot be understood without reading the whole body.
- The skill includes README-like marketing content.
- The workflow has no validation step.
- The skill cannot explain why it is a skill instead of a prompt or agent.
- Example triggers are missing from both description and `## When to Use`.
- Eval assets only pass for one captured session and break after simple renames.
