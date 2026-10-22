# Codex User Profile

## Allowed Targets and Exclusions

- Durable user-wide behavior belongs in the existing user-level
  `~/.codex/AGENTS.md` or another supported user-level Codex instruction file.
- Supported runtime settings belong in `~/.codex/config.toml` or another
  verified user-level Codex configuration file. Verify ownership before editing.
- Never create, edit, rename, or delete installed Skills under
  `~/.codex/skills/**` or `~/.agents/skills/**`; they are mirrors, not authoring
  sources. A Skill lesson is a handoff to its verified private source.
- Never edit repositories, workspace instructions, memories, session databases,
  logs, caches, generated state, or plugin caches.
- Never publish, synchronize, commit, or push from this workflow.

## Configuration Rules

- Verify each setting against the installed Codex version or current official
  documentation. Never invent keys from another client.
- For startup failures, distinguish process timeout, executable discovery,
  package-manager launch overhead, authentication, and server runtime failure
  before changing configuration.
- Prefer bounded values and explain non-default timeouts/retries.
- Preserve TOML types, table placement, quoting, comments and unrelated settings.
  A text match is not syntax validation.
- Never print full environment-variable values or credential-bearing
  configuration during diagnosis.

## Validation and Reporting

Read the current target before writing; reconcile state after an interrupted
mutation instead of repeating it. Inspect the changed section, parse TOML or use
a supported read-only command, and check that only intended files changed.
Report configuration saved, syntax checked, and runtime behavior verified as
separate facts. List unperformed publication, Skill installation, commit, push
and other gated actions explicitly.
