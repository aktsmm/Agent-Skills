---
name: review-report
description: Report review using IMPACT framework (results-oriented evaluation and improvement). Use when explicitly
  requesting /review-report.
argument-hint: report-path daily|weekly|monthly [focus area]
disable-model-invocation: true
user-invocable: true
compatibility: Requires manual skill invocation and dispatch to the named configured workspace agent; otherwise
  stop explicitly.
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Review Report

## Dispatch Contract

1. Resolve the configured `report-reviewer` custom agent from `.github/agents/report-reviewer.agent.md` and verify that the host can dispatch to that exact configured agent.
2. Read [the complete report contract](references/report-contract.md). Invoke the host's agent-dispatch tool with `agentName: "report-reviewer"` (or its configured-agent selector). Pass the complete contract content, its workspace-relative path, the workspace root, and all user arguments verbatim as the task. Do not summarize the contract or discard date, period, path, language, or focus arguments.
3. If the agent, dispatch tool, contract, or capabilities required by the contract are unavailable, report an explicit error and stop. Never run the report inline, substitute a general-purpose agent, widen tools, or bypass the configured role.

The configured reviewer uses `[read, search]`: no report editing and no new data collection. Return IMPACT feedback and the verdict only. Contract integration examples describe revisions by report-generator, never by this reviewer invocation.
