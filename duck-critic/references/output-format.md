# Output Format

Use this format for the final reconciled review.

## Route Values

Use these route values as the SSOT for `Route Used`.

| Route                     | Use When                                                             |
| ------------------------- | -------------------------------------------------------------------- |
| `native-rubber-duck`      | GitHub Copilot CLI native Rubber Duck actually ran.                  |
| `fallback-custom-agent`   | An existing custom reviewer agent handled the critique.              |
| `fallback-subagent`       | A forked subagent or isolated reviewer context handled the critique. |
| `fallback-separate-model` | Another model session was used manually.                             |
| `manual-critic-packet`    | No tool route exists and only a reusable packet was prepared.        |

```markdown
**Route Used**
`native-rubber-duck | fallback-custom-agent | fallback-subagent | fallback-separate-model | manual-critic-packet`

**Critic Model**
`<exact model string>` — `<family>` — `different-family | same-family | self-review`

**Checkpoint**
`plan | mid-implementation | tests | retry-after-failure | hard-to-reverse-decision | post-change`

**Rounds**
`<N> round(s)` — `stopped on PASS | accepted PASS_WITH_NOTES | max-rounds fail-safe | critic unusable (BLOCKED) | 0 rounds (critic skipped)` — blocking per round: `<n1>, <n2>, ...` — discarded dispatches: `<n>`

**Verdict**
`PASS | PASS_WITH_NOTES | NEEDS_CHANGES | BLOCKED`

**Blocking Issues**

- None found.

**Non-blocking Issues**

- None found.

**Suggestions**

- None.

**Rejected/Low-signal Notes**

- None.

**Next Actions**

- Concrete action 1.
```

## Rules

- Keep findings short and actionable.
- One report per checkpoint. A feature that gated its plan and then its implementation ran two loops, and collapsing them into a single round count hides which artifact was actually reviewed and which stop condition applied to it. Name the checkpoint, and report each loop's own rounds and blocking counts.
- Always report how many rounds the loop ran and why it stopped (`PASS`, accepted `PASS_WITH_NOTES`, the max-rounds fail-safe, or `0 rounds` when the critic was skipped). See [loop protocol](./loop-protocol.md) for the stop conditions.
- On `0 rounds`, put `not applicable — critic skipped` in Critic Model and Checkpoint, and say in one line why skipping was the right call. Never invent a model string to fill the field: a fabricated header is worse than an honest empty one, and the reason is the part a reader needs. A skipped critic is not `BLOCKED` — `BLOCKED` means the loop tried and could not evaluate.
- Report the blocking count for each round. It is what shows the loop converged rather than stalled, and it is the only auditable justification for running past the 3-round fail-safe.
- Count only rounds that came back with a blocking count, and report discarded dispatches separately. A checkpoint that reads as one clean round while three returned nothing is a different checkpoint.
- If the loop stopped on the max-rounds fail-safe, list the unresolved blocking findings under Blocking Issues.
- Put blocking issues first.
- Use `None found` when a section has no items.
- Mention model or harness uncertainty when relevant.
- Report the exact model string the critic actually ran on, plus its family. If the critic ended up `same-family` or `self-review` because a different family was unavailable, say so explicitly so the second opinion's strength is clear. If no model was passed to the harness, the producer's model was inherited: report `same-family`. See the selection rules in [model lanes](./model-lanes.md).
- Include file paths only when the reviewer actually inspected those files.
- For fallback routes, explicitly say the output is Rubber Duck-equivalent, not native Rubber Duck.

## Verdict Guide

These four values are the **producer's** verdict for the whole loop, decided during reconcile. They are not a vocabulary for the critic: a critic reports findings and a blocking count, and anything it offers as an overall grade is mapped, not copied. See [reviewer rubric](./reviewer-rubric.md) for the label discipline.

| Verdict           | Meaning                                                                            |
| ----------------- | ---------------------------------------------------------------------------------- |
| `PASS`            | No blocking or meaningful non-blocking issues found.                               |
| `PASS_WITH_NOTES` | No blockers, but at least one non-blocking issue or suggestion matters.            |
| `NEEDS_CHANGES`   | At least one blocking issue must be addressed before proceeding.                   |
| `BLOCKED`         | The critic cannot evaluate because required context, tools, or access are missing. |
