# Harness Adapters

Choose the strongest route available in the current environment. Prefer native Rubber Duck only when the harness actually supports it.

## GitHub Copilot CLI

Use native Rubber Duck for ordinary `standard` checkpoints: you keep producing the work and call Rubber Duck at each checkpoint defined in [loop protocol](./loop-protocol.md), then revise and re-consult until it passes. Native Rubber Duck already runs the critic on a different model family, so it fits the loop directly.

Native Rubber Duck does not expose a tier-pinned model selection. Use it for ordinary `standard` checkpoints and report `tier=uncontrolled`; use a read-only fallback route with an explicitly selected model when a quick deterministic-gate audit or a high-risk / `deep` review needs a pinned tier.

Preferred prompts:

```text
/rubber-duck What edge cases, design flaws, or verification gaps are missing?
```

```text
Rubber duck your plan before implementation.
```

### Large Markdown artifacts on Windows

Do not inline a large Markdown body into `copilot -p`, and do not use `--attachment` for `.md`. Send a short native Rubber Duck prompt naming one exact workspace-relative file, run Copilot CLI with `--available-tools=view --allow-tool=view`, and state: review only that file; do not inspect Git, `git diff`, `git status`, or other files. This avoids Windows command-line length limits while preserving the critic's read-only, artifact-scoped boundary; when the review requires supporting material, name each additional exact path instead of enabling broad tools. Reuse the same boundary for revision rounds.

If native Rubber Duck is unavailable or does not trigger:

- Use a read-only custom critic agent if one exists.
- Ask for a second opinion in a separate model session.
- Use the fallback critic packet from [critic packets](./critic-packets.md).
- State `Route Used` with a route value from [output format](./output-format.md).

If native Rubber Duck returns findings about unrelated worktree changes despite a scoped packet, treat that consultation as scope-drifted rather than valid feedback. Do not reconcile those findings. Use a read-only fallback critic with an explicit target file list and a prohibition on inspecting `git diff`, `git status`, or unrelated changes.

Do not present fallback output as built-in Rubber Duck output.

## VS Code

You (the main conversation) are the **producer** and keep owning the plan, code, and tests. The **critic** is a separate read-only subagent run via `runSubagent`, ideally on a different model family. Do not delegate the whole task to the subagent — only the review of your current checkpoint.

Keep companion `.agent.md` files outside this skill. If the user later asks for click-selected reviewer agents, treat that as a separate customization request with its own scope, plan, and verification.

Recommended VS Code loop:

1. Run `/duck-critic <target>` and keep producing the artifact yourself up to the first checkpoint from [loop protocol](./loop-protocol.md).
2. Pick the critic route, reviewer lane, and `quick` / `standard` / `deep` depth. Resolve the critic family first, then its tier with [model lanes](./model-lanes.md), and pass the exact live picker string explicitly.
3. Send the critic packet to a read-only `runSubagent` reviewer (or an existing read-only reviewer agent / separate model session). The subagent only reviews — it must not edit files or run mutating commands.
4. Reconcile the findings in the main conversation, revise the artifact yourself, and re-consult the critic. Repeat until a stop condition in [loop protocol](./loop-protocol.md) is met.

### Resolving the critic model

`runSubagent` inherits the producer's model when `model` is omitted, so leaving it out silently produces a same-family critic. Always pass `model` explicitly, copying the model string exactly as the harness lists it, including the vendor suffix.

Passing `model` selects a model; it does not override the lane policy. Before dispatch, reject and re-resolve any explicitly selected non-preferred family unless the user explicitly requested that family for an experiment.

After dispatch, apply the family/tier verification and single-retry rule in [model lanes](./model-lanes.md). Do not override it in this harness.

To read the live model list, call `runSubagent` once with an obviously invalid `model` value that cannot collide with a real name. The rejection normally names every selectable model (`Requested model '...' not found. Available models: ...`). Apply the [model lanes](./model-lanes.md) selection rules to that list, then run the real critic with the resolved name. Probe once per session and reuse the result; do not probe before every round.

Proceed only when the rejection actually returns a list. If it does not, or the resolved name is itself rejected, treat model selection as failed: never invent or half-remember a name, fall back per [model lanes](./model-lanes.md), and report the step you landed on. The list reflects current entitlement and rollout, so treat it as this session's answer rather than a durable fact.

Subagent choice is separate from model choice. A read-only exploration subagent cannot write files, so ask that kind of critic to return its findings in its reply rather than to a review file.

### What a subagent still inherits

A `runSubagent` critic does not see the producer's conversation, but it is not a clean room: user- and workspace-level instruction files still apply to it. The visible tell is a critic answering in the language a user instruction file mandates when the packet never asked for it.

### Verify the critic stayed read-only

`read-only` is a packet instruction, not a capability the harness enforces. A write-capable critic subagent will edit files outside the review target and drop scratch files at the workspace root. Fingerprint the artifact set before dispatch and compare after, and include untracked paths: a status listing alone hides mutation of a file that was already modified.

An unexplained delta after dispatch means the round is contaminated. Identify what the critic created or changed, restore only that without clobbering pre-existing edits, and re-run against the original artifact or a write-incapable route before reconciling any finding from that round.

A write-incapable exploration subagent removes the risk but usually cannot reach documentation or web tools, so a fact-checking lane may still need a write-capable critic. Choose per lane, not per session.

Treat the isolation as conversation isolation only. Anything that must bind the critic belongs in the packet, and anything the producer's own instruction files push toward is a bias the critic may quietly share — which is the blind spot a different model family was chosen to avoid.

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

Resolve family first and then the `quick` / `standard` / `deep` tier before setting `model`. Use exact model names only after checking the target Claude Code environment. Inheriting the producer's model is a last resort to call out explicitly, since a same-family critic mostly echoes the producer's blind spots.

## Generic Agent Harnesses

Use the same critic packet with any available reviewer that can stay read-only.

Resolve family first and then the `quick` / `standard` / `deep` tier before dispatch. Examples of acceptable fallback patterns:

- Separate model session with the tier resolved from [model lanes](./model-lanes.md).
- Read-only custom reviewer agent.
- Forked subagent with no edit or shell mutation permissions.
- Manual review prompt pasted into another harness.

Examples of unacceptable claims:

- Reporting the native route when the harness has no native Rubber Duck.
- Saying a specific model reviewed the work without verifying that model was selected.
- Letting the critic silently change files.

## Route Values

Route values are defined in [output format](./output-format.md). Use that file as the SSOT when reporting `Route Used`.
