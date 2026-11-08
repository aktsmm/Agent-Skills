# Hooks Guide

Hooks are deterministic lifecycle automation (VS Code Preview). The examples below retain the **legacy Local** format, not a new Copilot schema. Use the [current Copilot workflow](https://code.visualstudio.com/docs/agent-customization/hooks) for new hooks. Harness selection, not model selection or a shared `.github/hooks` location, determines events, payloads, and decisions.

Use hooks when workflow behavior must run, block, ask, or inject context at a known event. Do not use hooks for guidance that can remain conversational.

## When to Use

### Good fit

- block dangerous commands before execution
- require confirmation at specific lifecycle events
- inject standard runtime context at session start
- run validation or formatting after successful tool use

### Bad fit

- style guidance that can live in instructions
- role specialization that belongs in an agent
- reusable workflows with assets that belong in a skill

## Guidance vs Enforcement

| Need                         | Use                                  |
| ---------------------------- | ------------------------------------ |
| Encourage preferred behavior | Prompt / Instruction / Skill / Agent |
| Guarantee lifecycle behavior | Hook                                 |

If the requirement includes "always block", "must ask", "auto-run", or "inject at session start", evaluate Hook first.

## Locations (Local harness)

| Path                                                   | Scope                                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------------ |
| `.github/hooks/*.json`                                 | Workspace (subject to Workspace Trust)                                   |
| `.claude/settings.json`, `.claude/settings.local.json` | Workspace, Claude format (needs `chat.useClaudeHooks`; matchers ignored) |
| `~/.copilot/hooks/*.json`                              | User                                                                     |
| `~/.claude/settings.json`                              | User, Claude format (needs `chat.useClaudeHooks`)                        |
| `hooks:` in `.agent.md` frontmatter                    | Agent-scoped; Local and Copilot support it (see below)                    |

`chat.useHooks` (default on) controls Local hook execution; `chat.hookFilesLocations` adds or disables locations. These settings do not configure Agent Host harnesses.

Prefer workspace hooks for team policy. Keep personal automation outside the repo when it should not be shared.

## Lifecycle Events (Local)

| Event              | Trigger                                                                      |
| ------------------ | ---------------------------------------------------------------------------- |
| `SessionStart`     | First prompt of a new session                                                |
| `UserPromptSubmit` | User submits a prompt                                                        |
| `PreToolUse`       | Before tool invocation                                                       |
| `PostToolUse`      | After successful tool invocation                                             |
| `PreCompact`       | Before context compaction                                                    |
| `SubagentStart`    | Subagent starts                                                              |
| `SubagentStop`     | Subagent is about to stop                                                    |
| `Stop`             | Current agent execution is about to stop (not necessarily the whole session) |

## Minimal Shape (Local)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "./scripts/validate-tool.sh",
        "timeout": 15
      }
    ]
  }
}
```

Native format uses PascalCase event names and `command`, OS overrides (`windows`, `linux`, `osx`), and `timeout`. The hook receives JSON on stdin and may write JSON to stdout to add context or block/ask; see the [Local hooks reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference) for the full schema and exit codes.

### Agent-scoped hooks (Local example)

```yaml
---
name: Strict Formatter
hooks:
  PostToolUse:
    - type: command
      command: "./scripts/format-changed-files.sh"
---
```

In Local, these add to user/workspace hooks, require `chat.useHooks` and workspace trust, and a subagent's `Stop` fires as `SubagentStop`. Copilot also supports agent-scoped hooks; VS Code preserves their scope during conversion, including plugin-provided agents. Do not move them to repo/plugin-wide hooks as a migration shortcut.

### Copilot migration gate

Check the [Copilot contract](https://docs.github.com/en/copilot/reference/hooks-reference) and [migration procedure](https://code.visualstudio.com/docs/agent-customization/migrate-customizations#_migrate-hooks):

- `preToolUse` supplies `toolName`/`toolArgs`; the `PreToolUse` alias supplies snake_case fields and can use Claude-style tool names. Neither guarantees old Local arguments. Local ignores matcher values; verify destination matching.
- Copilot command hooks use `timeoutSec`, with `command`, platform `bash`/`powershell`, or shell-free `exec`/`args`. Resolve script paths, `cwd`, and `env` dependencies on the runtime host; do not assume editor variables or copy secret values.
- Local `chat.useHooks`/`chat.hookFilesLocations` do not disable/configure Copilot. Preserve disabled state in destination sources and check duplicate user/repo/plugin hooks before enabling.
- Copilot command `preToolUse` errors deny the call, but timeouts fall through to normal permissions, including policy hooks. Other events/HTTP hooks differ; test failures, not only success. `ask` needs an interactive approval flow.
- Verify the scoped event and intended denial in a trusted destination session before relying on it; editor schema validation is not execution proof.

## Decision Heuristic

Choose Hook only if all of these are true:

1. The behavior must happen at a specific lifecycle event
2. Guidance alone is insufficient
3. A shell command can evaluate or enforce the rule safely

If any of the three is false, prefer prompt / instruction / skill / agent.

## Core Principles

1. Keep hooks small and auditable
2. Prefer explicit block/ask rules over opaque automation
3. Avoid hardcoded secrets or environment-specific values
4. Do not let long-running hooks stall normal workflow

## Common Patterns

### Ask before dangerous tool use

Use `PreToolUse` when a command or tool category needs human confirmation.

### Auto-validate after edits

Use `PostToolUse` when formatting, linting, or policy checks should run after successful file changes.

### Inject startup context

Use `SessionStart` when the agent should receive deterministic context before normal work begins.

### Session-scoped guardrails

For safeguards that would be too noisy as always-on policy, prefer agent-scoped hooks (above) on the agent that does the risky work.

Good fits:

- stricter destructive-command blocking while touching production or infrastructure
- write-freeze rules during debugging or audit-only work
- temporary validation that belongs to one workflow but not normal chat

Keep these hooks narrow, visible, and easy to disable when the workflow ends.

### Lightweight telemetry

Hooks can also record small routing or workflow signals when you need evidence for improvement.

Good fits:

- skill name or workflow name
- manual vs automatic trigger
- success, fallback, or blocked outcome
- missing expected trigger, when the platform exposes it

Use local append-only logs or aggregated counters. Do not log prompt text, secrets, personal data, customer data, or raw tool payloads.

## Anti-patterns

- using hooks for soft preferences that belong in instructions
- building large workflow logic inside hooks
- creating hooks before you can name the lifecycle event they depend on
- running slow hooks that make ordinary tasks feel broken
- making a high-friction hook always-on when it only belongs to one risky workflow
- collecting telemetry broadly without a concrete routing or quality question
