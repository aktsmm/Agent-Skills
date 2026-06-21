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
`different-family | same-family | self-review` — name the critic model/family when known.

**Rounds**
`<N> round(s)` — `stopped on PASS | accepted PASS_WITH_NOTES | max-rounds fail-safe | 0 rounds (critic skipped)`

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
- Always report how many rounds the loop ran and why it stopped (`PASS`, accepted `PASS_WITH_NOTES`, the max-rounds fail-safe, or `0 rounds` when the critic was skipped). See [loop protocol](./loop-protocol.md) for the stop conditions.
- If the loop stopped on the max-rounds fail-safe, list the unresolved blocking findings under Blocking Issues.
- Put blocking issues first.
- Use `None found` when a section has no items.
- Mention model or harness uncertainty when relevant.
- State the critic model family. If the critic ended up `same-family` or `self-review` because a different family was unavailable, say so explicitly so the second opinion's strength is clear. See the model fallback chain in [model lanes](./model-lanes.md).
- Include file paths only when the reviewer actually inspected those files.
- For fallback routes, explicitly say the output is Rubber Duck-equivalent, not native Rubber Duck.

## Verdict Guide

| Verdict           | Meaning                                                                            |
| ----------------- | ---------------------------------------------------------------------------------- |
| `PASS`            | No blocking or meaningful non-blocking issues found.                               |
| `PASS_WITH_NOTES` | No blockers, but at least one non-blocking issue or suggestion matters.            |
| `NEEDS_CHANGES`   | At least one blocking issue must be addressed before proceeding.                   |
| `BLOCKED`         | The critic cannot evaluate because required context, tools, or access are missing. |
