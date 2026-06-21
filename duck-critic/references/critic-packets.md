# Critic Packets

Use these packet shapes when routing the review. Keep them compact and fill only fields that matter for the current request.

## Native GitHub Copilot CLI Rubber Duck

Use this prompt shape only when asking GitHub Copilot CLI's built-in Rubber Duck:

```text
/rubber-duck Review this plan/code/test/design as a constructive critic.
Goal: <goal>
Current approach: <short plan or diff summary>
Constraints: <constraints>
Evidence: <tests, logs, checks, or none>
Focus on blocking issues, non-blocking issues, and useful suggestions. Ignore style-only comments.
```

If slash invocation is unavailable but Copilot CLI can still consult Rubber Duck, use natural language:

```text
Rubber duck this plan before implementation. Use a different-model critic if available, stay read-only, and report only issues that affect success.
```

## Fallback Reviewer Packet

Use this shape when the harness does not expose native Rubber Duck:

```text
You are a read-only constructive critic providing a Duck Critic second opinion.

Route: <one route value from output-format.md>
Reviewer lane: <architecture-critic | implementation-critic | security-critic | test-critic | general-critic>
Goal: <goal>
Acceptance criteria: <criteria or unknown>
Current approach or diff: <summary>
Assumptions: <assumptions>
Constraints and must-not rules: <constraints>
Evidence already collected: <tests/logs/checks or none>
Questions for critic: <specific concerns>

Report only real issues. Classify each finding as blocking, non-blocking, or suggestion. Ignore style-only comments. Do not edit files or run mutating commands.
```

## Packet Rules

- Keep packets short enough to paste into another model session.
- Do not include secrets, credentials, private tokens, or unrelated logs.
- Do not include hidden reasoning or full transcripts.
- Say when native Rubber Duck was not available.