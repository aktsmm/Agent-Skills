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

Prefer a reviewer from a different model family than the producer when available.

Examples:

- Work produced by a GPT/OpenAI-family model: ask a Claude Opus-class or Claude Sonnet-class reviewer when available.
- Work produced by a Claude-family model: ask a GPT/OpenAI top-reasoning-class reviewer when available.
- Work produced by an unknown model: choose the strongest available read-only reviewer and state the uncertainty.

These are role lanes, not fixed model IDs. Exact local names vary by product, license, and rollout. Verify the model picker or CLI configuration before storing a `model` value in handoffs or harness-specific configuration.

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
