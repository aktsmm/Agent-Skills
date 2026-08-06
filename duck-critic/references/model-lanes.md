# Model Lanes

Use lanes to choose the kind of critic. Do not hardcode exact model names in portable skill instructions.

## Lane Selection

| Lane                    | Use When                                                | Focus                                                         |
| ----------------------- | ------------------------------------------------------- | ------------------------------------------------------------- |
| `general-critic`        | Default second opinion                                  | Goal fit, blind spots, hidden assumptions                     |
| `architecture-critic`   | Design, workflow, infrastructure, broad changes         | Boundaries, coupling, data flow, runtime risk                 |
| `implementation-critic` | Code or planned edits                                   | Logic bugs, edge cases, contracts, maintainability            |
| `security-critic`       | Auth, inputs, file paths, network, secrets, permissions | Exploitability, data exposure, trust boundaries               |
| `test-critic`           | Tests or verification plan                              | Missing assertions, false positives, weak checks, flaky paths |

Use one lane by default. Use multiple lanes only when the work is broad, risky, security-sensitive, architecture-heavy, or has already failed repeatedly.

## Critic Model Selection

The producer and the critic must be different model families whenever the harness allows it. A second opinion from the same model as the producer mostly echoes the producer's own blind spots, so a same-family critic is a last resort to note explicitly, not the default.

Never hardcode model IDs. Model names churn faster than this skill does, so resolve the critic at run time from the harness's own model list, using signals that outlive individual names.

### 1. Discover

Read the harness's current model list at run time; see [harness adapters](./harness-adapters.md) for how each harness exposes it. Never assume a name from memory or from an earlier session. Discover once per session and reuse the result.

### 2. Exclude

Prefer any capability metadata the harness exposes. When only names are available, drop models whose name carries a lightweight or specialized signal — `mini`, `nano`, `lite`, `small`, `flash`, `haiku`, `fast`, `turbo`, `code` / `codex`, `embed` — and drop any auto-router entry whose family cannot be determined. Compare against whole tokens after splitting the name on spaces, hyphens, dots, and parentheses, so a future flagship is not dropped for merely containing those letters. This is a conservative filter, not a capability test: a weak model carrying no signal will survive it, so never read a surviving name as proof of frontier tier.

### 3. Rank

**Preferred critic families.** This list is the only thing to revisit when new frontier families ship:

- OpenAI GPT family
- Anthropic Claude flagship line — the top general tier, not the mid or small tier

Fall back in this order and stop at the first step that works:

1. Frontier model from a preferred family that is a **different family** than the producer.
2. Same family as the producer, fresh instance — report as `same-family`, so the weaker second opinion is visible.
3. Self-critique — report as `self-review` and run the [reviewer rubric](./reviewer-rubric.md) against your own artifact as an explicit critic pass.

Never auto-select a family outside the preferred list; use one only when the user names it explicitly. A same-family critic from a preferred family beats an unvetted family.

### 4. Resolve the tier

Within the chosen family, take the highest generation available. Prefer a stable entry over one marked `preview` or `experimental` at the same generation. Same-generation variants that nothing distinguishes are equivalent for this purpose: pick one deterministically — the first in the harness's own ordering — and report the exact name, so a choice that depends on list order stays auditable.

### 5. Report

Report the exact resolved model string, its family, and `different-family | same-family | self-review`. If you did not pass an explicit model to the harness, you inherited the producer's model: report that as `same-family`. If selection itself failed — the model list could not be read, or the resolved name was rejected — say so and name the fallback step you landed on.

Never block the loop on model choice. If the user gave no model instruction, resolve and proceed instead of stopping to ask. Pause only when the choice is genuinely ambiguous or costly, such as a deep multi-lane review on expensive models.

## Context Independence

Model diversity is only one axis of independence. The other is instruction independence: the critic must not inherit the producer's custom agent instructions, `AGENTS.md`, or full system prompt. Native Rubber Duck enforces this by running without the producer's custom agent instructions; reproduce it in other harnesses by handing the critic only the artifact, goal, constraints, and evidence. A critic that shares both the producer's model family and its project instructions stops being a second opinion at all. See `references/critic-packets.md` for what to include in the handoff.

## Reviewer Depth

| Depth      | Use When                                                        | Expected Output                                           |
| ---------- | --------------------------------------------------------------- | --------------------------------------------------------- |
| `quick`    | Small plan or single-file change                                | 0-5 high-signal findings                                  |
| `standard` | Normal implementation or test review                            | Findings by severity plus next actions                    |
| `deep`     | Multi-file, architecture, deploy, security, or repeated failure | Lane-specific critique with explicit assumptions and gaps |

Default to `standard`. Use `deep` only when the extra cost is justified.

## Avoid

- Do not choose a more expensive model for trivial edits.
- Do not run many reviewer lanes just to increase confidence.
- Do not accept comments that are only stylistic unless they affect correctness, security, or verification.
- Do not hide model uncertainty. If the model could not be controlled, say so.
