# Hooks Guide

Hooks are deterministic lifecycle automation for agent sessions. VS Code hooks are Preview; this guide follows the **Local harness** ([VS Code hooks docs](https://code.visualstudio.com/docs/agent-customization/hooks), verified 2026-10).

The selected harness (Local / Copilot / Claude / Codex on Agent Host) owns events, payloads, and output decisions. A shared file such as `.github/hooks/*.json` does not make behavior identical across harnesses; test in the destination harness before reusing a hook.

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
| `hooks:` in `.agent.md` frontmatter                    | Custom agent only (Preview, Local only)                                  |

`chat.useHooks` (default on) controls Local hook execution; `chat.hookFilesLocations` adds or disables locations. These settings do not configure Agent Host harnesses.

Prefer workspace hooks for team policy. Keep personal automation outside the repo when it should not be shared.

## Lifecycle Events

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

## Minimal Shape

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

### Agent-scoped hooks (Preview, Local only)

```yaml
---
name: Strict Formatter
hooks:
  PostToolUse:
    - type: command
      command: "./scripts/format-changed-files.sh"
---
```

They run in addition to user/workspace hooks, require `chat.useHooks` and a trusted workspace, and a subagent's `Stop` hook fires as `SubagentStop`.

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
