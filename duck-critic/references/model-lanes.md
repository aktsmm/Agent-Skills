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

## Model Diversity

The producer and the critic must be different model families whenever the harness allows it. A second opinion from the same model as the producer mostly echoes the producer's own blind spots, so a same-family critic is a last resort to note explicitly, not the default.

Examples:

- Work produced by a GPT/OpenAI-family model: ask a Claude Opus-class or Claude Sonnet-class reviewer when available.
- Work produced by a Claude-family model: ask a GPT/OpenAI top-reasoning-class reviewer when available.
- Work produced by an unknown model: choose the strongest available read-only reviewer and state the uncertainty.

These are role lanes, not fixed model IDs. Exact local names vary by product, license, and rollout. Verify the model picker or CLI configuration before storing a `model` value in handoffs or harness-specific configuration.

## Model Fallback

A different-family critic is preferred, not required. When one cannot be selected, fall back in this order and never block the loop on model choice:

1. **Different family, explicitly chosen** — the user named a model/family, or a different family is available. Use it.
2. **Different family, auto-selected** — no model was specified, but the harness exposes a different family than the producer. Pick the strongest available read-only one.
3. **Same family, different instance/session** — only the producer's family is available. Use a fresh read-only critic on it and **state in the output that the critic is same-family**, so the second opinion is known to be weaker.
4. **Self-critique** — no separate critic is available at all. Run the [reviewer rubric](./reviewer-rubric.md) against your own artifact as an explicit critic pass, and clearly label it self-review, not an independent second opinion.

If the user gave no model instruction, default to step 2: do not stop and ask — auto-select a different-family critic and report which route was used. Only pause for the user when the choice is genuinely ambiguous or costly (for example, a deep multi-lane review on expensive models).

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
