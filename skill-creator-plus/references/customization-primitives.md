# Customization Primitive Selection

Choose the right customization primitive before creating files.

## Decision Matrix

| Need | Best Fit | Why | Avoid When |
| ---- | -------- | --- | ---------- |
| Project-wide defaults that should apply to most work | Workspace instructions | Always-on guidance with low ceremony | The rule only matters for one task or one file type |
| File-scoped or task-scoped guidance | File instructions | On-demand discovery or `applyTo` matching | The content is really a reusable workflow |
| Single focused slash command | Prompt | Fast invocation with optional parameters | The task needs bundled scripts or rich assets |
| Reusable multi-step workflow with bundled scripts, templates, or references | Skill | Best balance of reuse, discovery, and progressive loading | You only need a one-off command or always-on rule |
| Persona with tool restrictions, delegation, or handoffs | Custom agent | Lets you control role boundaries and tools | The need is procedural, not persona-based |
| Deterministic enforcement or lifecycle automation | Hook | Runtime guarantees, blocking, auto-validation | Simple instructions are sufficient |

## Questions to Ask First

1. Is this guidance needed in most conversations, or only for a specific task?
2. Does the user need a reusable slash command, or always-on behavior?
3. Does the solution need bundled scripts, templates, or detailed references?
4. Is persona or tool restriction the core requirement?
5. Must the behavior be enforced deterministically?

## Scope Selection

Choose scope before creating the file.

| Scope | Use When | Typical Location |
| ----- | -------- | ---------------- |
| Workspace | Shared with a team or tied to one repo | `.github/` |
| User profile | Personal preference across repos | user profile customization folder |

Default to workspace only when the behavior should be shared through version control.

## Fast Rules of Thumb

- If the request starts with "always", it is usually an instruction.
- If the request starts with "when I type /", it is usually a prompt or skill.
- If the request needs scripts, templates, or structured references, lean toward a skill.
- If the request is about a specialist persona or safe tool boundaries, lean toward a custom agent.
- If the request is about blocking commands or auto-running checks, use a hook.

## Escalation Pattern

If you discover mid-design that the file type is wrong:

1. Stop editing the wrong primitive.
2. Explain the mismatch briefly.
3. Create or update the correct primitive.
4. Leave a short note in the related asset if cross-linking helps future maintenance.