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

The producer and the critic must be different model families whenever the harness allows it. This offers another perspective, not proof of better findings or independent evidence; a same-family critic remains a disclosed fallback, not the default.

Never hardcode model IDs. Model names churn faster than this skill does, so resolve the critic at run time from the harness's own model list, using signals that outlive individual names.

### 1. Discover

Read the harness's current model list at run time; see [harness adapters](./harness-adapters.md) for how each harness exposes it. Never assume a name from memory or from an earlier session. Discover once per session and reuse the result.

### 2. Exclude

Prefer any capability metadata the harness exposes. When only names are available, drop models whose name carries a lightweight or specialized signal — `mini`, `nano`, `lite`, `small`, `flash`, `haiku`, `fast`, `turbo`, `code` / `codex`, `embed` — and drop any auto-router entry whose family cannot be determined. Compare against whole tokens after splitting the name on spaces, hyphens, dots, and parentheses, so a future flagship is not dropped for merely containing those letters. This is a conservative filter, not a capability test: a weak model carrying no signal will survive it, so never read a surviving name as proof of frontier tier.

Do not exclude a candidate that the resolved family's tier ladder explicitly selects in step 4; the tier policy takes precedence over label heuristics.

### 3. Rank

**Preferred critic families.** This list is the only thing to revisit when new frontier families ship:

- OpenAI GPT family
- Anthropic Claude family

Resolve family before tier. Fall back in this order and stop at the first step that works:

1. A model from a preferred family that is a **different family** than the producer.
2. Same family as the producer, fresh instance — report as `same-family`, so the weaker second opinion is visible.
3. Self-critique — report as `self-review` and run the [reviewer rubric](./reviewer-rubric.md) against your own artifact as an explicit critic pass.

Never auto-select a family outside the preferred list; use one only when the user names it explicitly. A same-family critic from a preferred family beats an unvetted family.

### 4. Resolve the tier

After resolving the family, prefer a stable entry over one marked `preview` or `experimental`. Apply the tier ladder only within that resolved family:

- GPT: `quick` uses the balanced tier; `standard` / `deep` and high-risk decisions use the flagship tier. Resolve current tier membership from live capability metadata or primary provider/harness documentation, not a memorized release label. If that selected current-generation tier is unavailable, use the prior stable GPT tier as a fallback, not as the default.
- Claude: `quick` / `standard` uses the highest stable general tier (current label: `Sonnet`); `deep` and high-risk decisions use the highest stable flagship tier (current label: `Opus`).

Tier labels are not portable IDs: resolve the exact picker string at run time and report it. If the family fallback in step 3 selected the producer's family, report `same-family` regardless of tier. Do not infer that a later generation or a cheaper tier is always better for every review; verify applicable official pricing before claiming savings, and treat flagship escalation as a task-specific cost/quality tradeoff.

When the user explicitly requests the latest model in a named tier, resolve that tier's newest available compatible entry from the live catalog; do not pin an older generation from memory. Availability does not prove image-input support or review quality. If the requested model cannot be used, disclose the limitation rather than silently substituting an older tier or generation.

If the resolved tier is unavailable or rejected, use the documented fallback in that family; for Claude, use the next stable tier in the resolved family. Only then continue to the family fallback in step 3.

### Deterministic Gate Audit

Run deterministic checks first; they remain the PASS/FAIL source of truth. Add a `quick` critic audit when a checker is new or changed, returns an unexpected zero or count swing, or its result will drive a mutation or release. Give the critic the check command with its bounded input and output as text to reason about — it does not run them — and ask only about input scope, assumptions, exceptions, and a plausible false positive or false negative. The critic raises a concern; it does not override the checker without reproducible evidence.

### 5. Report

Report the exact resolved model string, family, depth, high-risk flag, tier, and `different-family | same-family | self-review`. Omitted `model` means `same-family` only when the harness inherits the producer's model; a native route that guarantees a different-family critic reports `different-family` and `tier=uncontrolled`. If selection itself failed — the model list could not be read, or the resolved name was rejected — say so and name the fallback step you landed on.

After dispatch, distinguish the requested model in the invocation from the effective model exposed by host metadata; a critic's self-identification is not runtime evidence. Record unavailable effective identity as `unknown`, not as the requested name. Verify the actual family and tier when metadata permits. A known non-preferred family or wrong tier is not a valid pass unless explicitly requested or an uncontrolled native route was approved; re-dispatch once, then use only an allowed disclosed fallback. If effective-model proof is a required gate, missing metadata blocks that gate.

Never block the loop on model choice. If the user gave no model instruction, resolve and proceed instead of stopping to ask. Pause only when the choice is genuinely ambiguous or costly, such as a deep multi-lane review on expensive models.

## Calibration After Missed Defects

- Do not attribute a missed defect to model weakness from the current scheduler assignment; retain historical runtime identity as unknown when receipts are absent.
- To separate model and rubric effects, compare baseline/candidate models against baseline/revised rubrics on the same frozen inputs and neutral brief in fresh contexts. Hide expected labels and producer verdicts; disclose reconstructed-baseline limitations.
- Include known defective cases and scoped controls. Score objective blocker misses separately from unsupported objections and subjective art judgments; rejecting every control is not a successful reviewer.
- For image reviews, establish that the actual images were opened, not merely listed as paths. Bind findings to image/source hashes, viewport/scale/language, rubric version and affected regions; inaccessible images are an evidence gap, not a pass.
- Cap the pilot before dispatch and compare actionable findings, latency and observed usage. A small calibration supports a bounded rollout, not universal superiority; preserve unknown prices and metadata.

## Context Independence

Model diversity is only one axis of independence. The other is instruction independence: a critic that shares both the producer's model family and its project instructions has stopped being a second opinion at all. Hand it only the artifact, goal, constraints, and evidence. See [critic packets](./critic-packets.md) for what that packet contains, and [harness adapters](./harness-adapters.md) for how much isolation each harness actually delivers — withholding instructions is not the same as the critic never seeing any.

## Reviewer Depth

| Depth      | Use When                                                        | Expected Output                                           |
| ---------- | --------------------------------------------------------------- | --------------------------------------------------------- |
| `quick`    | Small plan or single-file change                                | 0-5 high-signal findings                                  |
| `standard` | Normal implementation or test review                            | Findings by severity plus next actions                    |
| `deep`     | Multi-file, architecture, deploy, security, or repeated failure | Lane-specific critique with explicit assumptions and gaps |

Default to `standard`. Use `deep` only when the extra cost is justified. Use `quick` for a bounded low-risk judgment or deterministic gate audit; do not dispatch an LLM merely to repeat an established low-risk checker.

## Avoid

- Do not choose a more expensive model for trivial edits.
- Do not run many reviewer lanes just to increase confidence.
- Do not accept comments that are only stylistic unless they affect correctness, security, or verification.
- Do not hide model uncertainty. If the model could not be controlled, say so.
