# Validation Lanes

Choose the lightest lane that proves the change. A Skill does not need Python
or packaging merely because another Skill has a helper script.

## Baseline Lane: Every Skill

Inspect the actual files and record this compact completion record in the
review response or run artifact. Do not place machine paths or timestamps in
the packaged Skill.

```text
lane: baseline
files inspected: <relative paths>
frontmatter and triggers: pass | fail
self-contained paths: pass | fail
license and provenance evidence: <relative paths or legacy warning>
success-contract evidence: <what proves the workflow is complete>
commands skipped: <command> - <why it is not relevant>
```

For a no-helper Skill, this lane is sufficient when the record passes.

When host-specific frontmatter is present, record the target hosts and fallback
in the baseline review. A local host-aware validator can accept extensions such
as `context`, but strict common-spec compliance requires a separate validator
that rejects or explicitly excludes those extensions.

## Tool-Assisted Lane: Conditional

Run a bundled helper only when its behavior changed or is needed to prove the
requested outcome. Run `package_skill.py` only when producing a `.skill`
archive. Each helper owns its own dependency manifest; installing Python, uv,
or a package helper is never a general authoring prerequisite.

When a command is skipped, say why. When it runs, report the command's result
and inspect the produced artifact where one exists.

For bundled CLI helper changes, import-based tests alone are insufficient:

- Exercise the documented entry point in a subprocess with the intended interpreter, including a safe path that reaches helper functions; `--help` alone does not cover definition-order or runtime failures.
- Test malformed or unapproved input rejection before external access, and register new tests in the normal test entry point. Use isolated fixtures or doubles, not production writes.
- Separate read-only checks from repair/apply modes. Verify both reported state and absence of unintended mutation, and name unexecuted live or recovery paths rather than treating unit-test success as end-to-end proof.
