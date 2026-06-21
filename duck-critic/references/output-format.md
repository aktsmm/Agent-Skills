# Output Format

Use this format for the final reconciled review.

## Route Values

Use these route values as the SSOT for `Route Used`.

| Route | Use When |
| --- | --- |
| `native-rubber-duck` | GitHub Copilot CLI native Rubber Duck actually ran. |
| `fallback-custom-agent` | An existing custom reviewer agent handled the critique. |
| `fallback-subagent` | A forked subagent or isolated reviewer context handled the critique. |
| `fallback-separate-model` | Another model session was used manually. |
| `manual-critic-packet` | No tool route exists and only a reusable packet was prepared. |

```markdown
**Route Used**
`native-rubber-duck | fallback-custom-agent | fallback-subagent | fallback-separate-model | manual-critic-packet`

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
- Put blocking issues first.
- Use `None found` when a section has no items.
- Mention model or harness uncertainty when relevant.
- Include file paths only when the reviewer actually inspected those files.
- For fallback routes, explicitly say the output is Rubber Duck-equivalent, not native Rubber Duck.

## Verdict Guide

| Verdict           | Meaning                                                                            |
| ----------------- | ---------------------------------------------------------------------------------- |
| `PASS`            | No blocking or meaningful non-blocking issues found.                               |
| `PASS_WITH_NOTES` | No blockers, but at least one non-blocking issue or suggestion matters.            |
| `NEEDS_CHANGES`   | At least one blocking issue must be addressed before proceeding.                   |
| `BLOCKED`         | The critic cannot evaluate because required context, tools, or access are missing. |
