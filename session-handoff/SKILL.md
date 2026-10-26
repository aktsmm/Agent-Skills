---
name: session-handoff
description: "Create a compact handoff note for another session. Use for セッションを閉じる, 引き継ぎを作る, 伝言を作る, create/export a handoff, or resume later. Do not create another handoff when a pasted note asks the current agent to resume work."
argument-hint: "引き継ぐ作業、完了条件、再開先へ渡す制約"
user-invocable: true
disable-model-invocation: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Session Handoff

Create one paste-ready continuation note, not a transcript or permanent operating rule.

## Intent And Approval

- Distinguish creating a note from consuming one. Ask one short question only when intent, purpose or resume target is ambiguous; a clear request needs no purpose reconfirmation.
- The latest explicit resume request wins over an older acknowledge-and-wait instruction. A target name, TODO, candidate list, recommendation or acknowledgement alone is not authorization to execute.
- By default the receiving session acknowledges and summarizes, then waits for explicit approval before commands, edits or external operations. An explicit request to resume a specific task permits only that scope; retain all prohibitions and additional high-risk approval gates.
- Offer A/B only for genuinely different next actions. With one sensible path, state that path and request approval rather than inventing a choice. Selecting a candidate approves only its scope; correcting or accepting a summary is not execution approval.
- Do not publish, push, delete, deploy, send, purchase, rewrite history, change auth/permissions, update production or stop a shared process without the required explicit approval. Put applicable unapproved operations under Must NOT near the top.

## Build The Note

1. Carry the original overarching objective from the initiating request or inherited handoff. Keep the current overarching objective separately only if direction changed; do not substitute this session's incidental work. User correction wins. Preserve at most these two objectives, plus this session's goal, requested outcome and concrete artifact.
2. Capture completed, pending, blocked and unknown state, relevant assumptions, exact scope and wording constraints, files, commands and validation outcomes. Mark guesses `仮説` and unknowns `未確認`; never turn implemented-but-unverified work into completion.
3. Save unsent drafts or comment bodies to an authorized file and cite it; chat-only text may disappear. Identify your dirty paths and unrelated changes that must not be staged or reverted.
4. Record date, repository/workspace, branch and HEAD, plus inherited session lineage extended with this session's ID. Keep root and the two most recent non-root IDs: `root: <id> → … → this session: <id>`. Do not invent missing IDs or a count of omitted entries; omit private log paths.
5. If a direct-entry workflow applies, make its invocation the next path, subject to the approval rule above. Include state and requirements it does not own, not a duplicate of its lifecycle.
6. Use [handoff-template.md](references/handoff-template.md), omitting irrelevant fields. Keep one Next Action section and end with done/stop criteria.
7. Remove secrets, credentials, private account identifiers, sensitive URLs, duplicate logs and obsolete TODOs. Use relative artifact paths when the receiver can resolve the workspace; otherwise confirm read capability and provide a verified local path or say which file the user must attach. Never claim an attachment was sent.

For shared targets, record the observation point for the other owner's completion, permitted read-only probes, and queues, schedulers and single-writer resources the receiver must not operate. If the terminal is unreliable, identify trusted artifacts instead of relying on stdout.

## Recover Missing Evidence

- Recover unsaved drafts from the originating session store, not memory. Inspect the available schema first (for SQLite, `SELECT sql FROM sqlite_master`), then filter by session ID and a distinctive phrase; avoid whole-turn dumps.
- Recovered text is an unapproved draft. Check claims against current files and repository state before reuse. If source evidence or required files cannot be read, mark the gap, blocker and resume condition; do not claim recovery or validation succeeded.
- Keep exact failure text when it changes the next action, attempted routes, unresolved verification and concrete stop/resume conditions.

## Optional Suggestions

Only when requested, suggest a session name or model. For names, use the known original title or a short goal-derived fallback; only trailing ` Re` / ` Re<number>` is a handoff suffix (replace with ` Re2` / increment, otherwise append ` Re`). Do not search for a missing title.

For a model suggestion, verify a current display name, give one-line reasoning and mark it advisory; the receiver rechecks availability. Use `unspecified` if unverifiable. Session history alone proves neither current availability nor absence.

## Final Check And Output

For nontrivial handoffs or requested rubber-duck review, perform a second pass:

- Are objective lineage, predecessor/root and described repository revision recoverable?
- Are normal, ambiguous, immediate-resume and blocked cases governed by the same approval boundaries?
- Are next actions real choices, with scope, prohibited actions, verification gaps and stop conditions preserved?
- Can the receiver find artifacts and distinguish facts, drafts, hypotheses and other actors' edits?

Return the complete note in one fenced `markdown` block, starting by identifying it as a prior-session handoff and specifying the applicable acknowledgement/resume behavior. Do not phrase it as a request to generate another handoff.
