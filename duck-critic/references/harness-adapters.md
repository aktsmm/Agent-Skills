# Harness Adapters

Choose the strongest route available in the current environment. Prefer native Rubber Duck only when the harness actually supports it.

## GitHub Copilot CLI

Use native Rubber Duck first when available.

Preferred prompts:

```text
/rubber-duck What edge cases, design flaws, or verification gaps are missing?
```

```text
Rubber duck your plan before implementation.
```

If native Rubber Duck is unavailable or does not trigger:

- Use a read-only custom critic agent if one exists.
- Ask for a second opinion in a separate model session.
- Use the fallback critic packet from [critic packets](./critic-packets.md).
- State `Route Used` with a route value from [output format](./output-format.md).

Do not present fallback output as built-in Rubber Duck output.

## VS Code

Use the skill inline as the orchestrator. If the workspace or user profile already has suitable reviewer agents, select one as the fallback reviewer lane.

Keep companion `.agent.md` files outside this skill. If the user later asks for click-selected reviewer agents, treat that as a separate customization request with its own scope, plan, and verification.

Recommended VS Code flow:

1. Run `/duck-critic <target>`.
2. Choose the route and reviewer lane.
3. Invoke an existing read-only reviewer agent, subagent, or separate model session.
4. Reconcile the feedback in the main conversation.

## Claude Code

Claude Code supports Agent Skills and has additional fields such as `context: fork`, `agent`, `model`, and `effort`.

Portable option:

- Copy this skill to `.claude/skills/duck-critic/` or install it as a shared skill.
- Keep the standard `SKILL.md` portable unless a Claude-specific variant is intentionally created.

Claude-specific variant, if desired:

```yaml
context: fork
agent: general-purpose
model: inherit
```

Use exact model names only after checking the target Claude Code environment. If using a Claude Opus-class reviewer, pair it with work produced by a different model family when possible.

## Generic Agent Harnesses

Use the same critic packet with any available reviewer that can stay read-only.

Examples of acceptable fallback patterns:

- Separate model session with a top-reasoning model.
- Read-only custom reviewer agent.
- Forked subagent with no edit or shell mutation permissions.
- Manual review prompt pasted into another harness.

Examples of unacceptable claims:

- Reporting the native route when the harness has no native Rubber Duck.
- Saying a specific model reviewed the work without verifying that model was selected.
- Letting the critic silently change files.

## Route Values

Route values are defined in [output format](./output-format.md). Use that file as the SSOT when reporting `Route Used`.
