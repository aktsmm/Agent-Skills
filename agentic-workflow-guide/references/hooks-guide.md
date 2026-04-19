# Hooks Guide

Hooks are deterministic lifecycle automation for agent sessions.

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

## Locations

| Path                   | Scope     |
| ---------------------- | --------- |
| `.github/hooks/*.json` | Workspace |

Prefer workspace hooks for team policy. Keep personal automation outside the repo when it should not be shared.

## Lifecycle Events

| Event              | Trigger                          |
| ------------------ | -------------------------------- |
| `SessionStart`     | First prompt of a new session    |
| `UserPromptSubmit` | User submits a prompt            |
| `PreToolUse`       | Before tool invocation           |
| `PostToolUse`      | After successful tool invocation |
| `PreCompact`       | Before context compaction        |
| `SubagentStart`    | Subagent starts                  |
| `SubagentStop`     | Subagent ends                    |
| `Stop`             | Agent session ends               |

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

Each command can define platform-specific overrides, `cwd`, `env`, and `timeout`.

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

## Anti-patterns

- using hooks for soft preferences that belong in instructions
- building large workflow logic inside hooks
- creating hooks before you can name the lifecycle event they depend on
- running slow hooks that make ordinary tasks feel broken
