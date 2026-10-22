# Copilot User Profile

## Allowed Targets

- Shared principles: `~/.copilot/copilot-instructions.md`.
- Domain instructions: `~/.copilot/instructions/**/*.instructions.md`.
- Personal task Skills: `~/.copilot/skills/**/SKILL.md`.
- Role definitions: `~/.copilot/agents/**/*.agent.md`.
- Deterministic hooks: `~/.copilot/hooks/**/*.json`.
- Related configuration is limited to `~/.copilot/config.json`,
  `~/.copilot/settings.json`, `~/.copilot/permissions-config.json`,
  `~/.copilot/mcp-config.json`, and `~/.copilot/mcp-oauth-config/**` only where
  directly related to customization. Never expose credential-bearing values.

Local Copilot customization copies may be edited directly within that scope.
They are not a private Skill repository authoring source. If the requested
outcome belongs to the private Skill source, hand it off without editing here.
Managed local edits may be overwritten by updates; report that risk and the
need to return changes to their verified source. Do not synchronize or publish.

## Gates

- Require a reusable personal rule; workspace/repository-only content is a
  handoff, not permission to edit a repository.
- Never target `command-history-state.json`, `session-store.db`,
  `vscode.session.metadata.cache.json`, `session-state/**`, `logs/**`, `pkg/**`,
  `crash-context/**`, or `restart/**`.
- No memory target: `/memories/**`, user, session and repository memories remain
  out of scope. A request to use memory needs a separately confirmed task.
- Confirm a self-contained result and actual primitive support. For example,
  a host that does not load prompt files cannot use a prompt as a working entry.
- A missing file or directory may be created in safe-auto only after its exact
  proposed path and reason are stated, no existing owner fits, and scope,
  visibility and sensitive defaults are clear.

## Validation

Inspect the changed section, check frontmatter/JSON or other relevant syntax,
and verify no unrelated changes were included. Preserve the global-entry versus
domain-file distinction. Report source-sync requirements in the review
checkpoint without committing, pushing, or running a synchronization workflow.
