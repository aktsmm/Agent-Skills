# Harness Adapters

Choose the strongest route available in the current environment. Prefer native Rubber Duck only when the harness actually supports it.

## GitHub Copilot CLI

Use native Rubber Duck as the critic step of the loop: you keep producing the work and call Rubber Duck at each checkpoint defined in [loop protocol](./loop-protocol.md), then revise and re-consult until it passes. Native Rubber Duck already runs the critic on a different model family, so it fits the loop directly.

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

You (the main conversation) are the **producer** and keep owning the plan, code, and tests. The **critic** is a separate read-only subagent run via `runSubagent`, ideally on a different model family. Do not delegate the whole task to the subagent — only the review of your current checkpoint.

Keep companion `.agent.md` files outside this skill. If the user later asks for click-selected reviewer agents, treat that as a separate customization request with its own scope, plan, and verification.

Recommended VS Code loop:

1. Run `/duck-critic <target>` and keep producing the artifact yourself up to the first checkpoint from [loop protocol](./loop-protocol.md).
2. Pick the critic route and reviewer lane. For the subagent critic, prefer a different model family than the producer; pass the `model` parameter to `runSubagent` to pin a different-family reviewer when one is available, and verify the exact model name first.
3. Send the critic packet to a read-only `runSubagent` reviewer (or an existing read-only reviewer agent / separate model session). The subagent only reviews — it must not edit files or run mutating commands.
4. Reconcile the findings in the main conversation, revise the artifact yourself, and re-consult the critic. Repeat until a stop condition in [loop protocol](./loop-protocol.md) is met.

## Claude Code

Claude Code supports Agent Skills and has additional fields such as `context: fork`, `agent`, `model`, and `effort`.

Portable option:

- Copy this skill to `.claude/skills/duck-critic/` or install it as a shared skill.
- Keep the standard `SKILL.md` portable unless a Claude-specific variant is intentionally created.

Claude-specific variant, if desired:

```yaml
context: fork
agent: general-purpose
# Set model to a different family than the producer; do not inherit the
# producer's model, which would make the critic same-family.
model: <different-family-model>
```

Use exact model names only after checking the target Claude Code environment. Inheriting the producer's model is a last resort to call out explicitly, since a same-family critic mostly echoes the producer's blind spots.

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
