---
name: retro-user
description: "Reflect verified incident or session learnings into personal Copilot or Codex instructions and configuration. Invoke explicitly for Retro User, user-wide retrospective, 個人設定の知見反映, or global customization improvements. Not for workspace rules or private Skill source authoring."
argument-hint: "学び・ログ・diff・会話要約、対象ホスト（copilot / codex）、mode（safe-auto / PLAN / review-only / dry-run）"
disable-model-invocation: true
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Retro User

Turn verified evidence into a minimal update to user-level customization. Share
the learning workflow, not the write permissions of different hosts.

## Host and Mode Gate

- Explicit invocation only. Prefer the requested target host; otherwise use the
  current execution host only when unambiguous. Ask before writing if unclear.
- Never choose a host merely because its files exist. Cross-host work requires an
  explicit target; modifying both hosts requires an explicit request for both.
- Read the selected profile before choosing or changing a target:
  [Copilot](references/copilot-profile.md) or [Codex](references/codex-profile.md).
  Another host's profile grants no permission.
- Default `safe-auto`: apply small or medium, clearly owned changes after all
  gates pass; no repeated approval for that bounded work.
- `PLAN`, `review-only`, `dry-run`, `確認だけ`, or `プレビュー`: inspect and propose;
  do not create, edit, rename, delete, or change configuration.
- Confirm unclear scope, new privileges, approval policy, sandboxing,
  authentication, external destinations, visibility, default models, other
  sensitive defaults, destructive deletion, or uncertain sensitive data unless
  the current request already authorizes that exact change. Holds take priority.

## Hard Boundaries

- Never edit repository/workspace assets, private Skill sources, memories,
  session databases, logs, caches, runtime/generated state, or plugin caches.
- Never edit installed Codex Skills, including `~/.codex/skills/**` and
  `~/.agents/skills/**`. Copilot local customization exceptions are limited to its
  own profile and never authorize Codex mirror edits.
- Never publish, synchronize, commit, or push from this workflow. Report source
  synchronization needs without performing them.
- Never persist secrets, credentials, tokens, account identifiers, customer or
  personal data, machine-specific absolute paths, transient paths, or raw logs
  and conversation transcripts. Generalize necessary evidence before writing.
- Workspace-only lessons and private Skill authoring are handoffs, not fallback
  write targets. Use the host-provided active workspace for a workspace handoff;
  do not create or propose an unrelated project folder.
- Match verified, committed implementation, not a local draft. Defer unsupported
  operations rather than inventing settings, tools, or capabilities.

## Workflow

1. **Collect evidence.** Require at least one log, diff/commit, conversation,
   terminal history, existing asset, or incident description. Treat nonzero exit,
   interruption, repeated commands, and long runs as observations, not conclusions.
   Stop and request input when none is available.
2. **Extract learnings.** Write `Learning / Evidence / Impact` for each candidate;
   prioritize by impact and recurrence (P1/P2/P3). Consider design/SSOT/idempotency,
   workflow, prompt/context design, and error patterns. Stop for unsupported,
   one-off, already-covered, environment-only, typo-only, or non-actionable items.
3. **Choose the owner.** Confirm the selected host profile, personal scope, file
   ownership and writability. Prefer the most specific existing file/section.
   Instructions hold principles, Skills task procedures, agents role separation,
   and hooks deterministic behavior. Explain the target choice.
4. **Run the safety gate.** Check reusable abstraction, minimal non-sensitive
   evidence, no duplicate/conflicting rule, no forbidden target, and a
   self-contained result that does not require another file or local environment
   to remain available. Respect the actual host's primitive/tool support.
5. **Inspect before writing.** Read current content; preserve comments, unrelated
   changes, types and unsaved notes. After interruption or an uncertain write,
   reconcile current state before retrying the mutation. If the edit tool is
   blocked by eDLP (`os error 449`) on an external-drive source, stage a copy on
   the internal drive, edit, `Copy-Item` back and compare hashes; stop after two
   failed staged writes instead of bypassing the control.
6. **Integrate minimally.** Delete only unnecessary, self-evident or duplicate
   text whose removal preserves normal/exception/stop decisions; then merge,
   compact, move detail, and add missing guidance. Preserve evidence, URLs,
   nontrivial procedures, scope, approvals, required examples, metadata,
   unverified requirements and failure/recovery conditions. Age alone does not
   obsolete history; verify its original is retained before removing it.
7. **Validate the actual artifact.** Inspect the changed section and scoped diff;
   check instruction placement, syntax and supported settings with a read-only
   parser/command where available. Verify intended paths only, no sensitive
   additions, and no lost behavior. Distinguish saved configuration from runtime
   verification; report unavailable checks rather than claiming success.

## Integration Decisions

- Prefer one specific owner. A cross-cutting principle may update several
  independently owning files as a tiny, self-contained judgment in each; do not
  copy a long block or make another Skill a required dependency.
- Prefer existing integration over a new file. Create a new file only when no
  existing role fits; explain its proposed path and `Target Rationale`.
- Files under 50 lines usually need no change or only a minimal edit unless
  there is clear value. Do not create a catch-all for a small rule or pointer.

## Output

Use `## Learnings`, `## Changes`, `## Target Rationale`, and
`## Review Checkpoint`. Identify the target host and mode, evidence and impact,
applied versus proposed changes, target file or handoff owner, validation and
unverified checks, and actions not performed.

The checkpoint confirms authorized safe-auto or explicit gated approval,
selected-host scope, no duplicates, writable targets, safety/scope checks, no
memory target, and no Codex mirror edit. State source-sync needs separately.
List at most three scoped read-only follow-ups; honor holds and visibility and
never turn a suggestion into wider authoring, commit/push, or distribution work.
