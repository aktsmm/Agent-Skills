---
name: monthly-report
description: Monthly report generation from weekly reports and activity logs. Use when explicitly requesting /monthly-report.
argument-hint: YYYY-MM [report language or focus]
disable-model-invocation: true
user-invocable: true
compatibility: Requires manual skill invocation and dispatch to the named configured workspace agent; otherwise
  stop explicitly.
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Monthly Report

## Dispatch Contract

1. Resolve the configured `report-generator` custom agent from `.github/agents/report-generator.agent.md` and verify that the host can dispatch to that exact configured agent.
2. Read [the complete report contract](references/report-contract.md). Invoke the host's agent-dispatch tool with `agentName: "report-generator"` (or its configured-agent selector). Pass the complete contract content, its workspace-relative path, the workspace root, and all user arguments verbatim as the task. Do not summarize the contract or discard date, period, path, language, or focus arguments.
3. If the agent, dispatch tool, contract, or capabilities required by the contract are unavailable, report an explicit error and stop. Never run the report inline, substitute a general-purpose agent, widen tools, or bypass the configured role.

The configured generator uses `[read, edit, search, agent]`. Preserve its mandatory independent report-reviewer/approval loop (maximum 3 iterations) and the contract's output paths. Follow report-specific evidence/preflight, PTO, and weekend/holiday rules before generic agent guidance. If mandatory collection cannot run with configured capabilities, stop explicitly rather than adding execute permissions or treating unavailable evidence as verified zero.
