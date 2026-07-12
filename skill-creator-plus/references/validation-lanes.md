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

## Tool-Assisted Lane: Conditional

Run a bundled helper only when its behavior changed or is needed to prove the
requested outcome. Run `package_skill.py` only when producing a `.skill`
archive. Each helper owns its own dependency manifest; installing Python, uv,
or a package helper is never a general authoring prerequisite.

When a command is skipped, say why. When it runs, report the command's result
and inspect the produced artifact where one exists.
