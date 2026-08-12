---
name: session-handoff
description: "Create a compact handoff note so a new chat/session can first acknowledge the current state before work resumes. Use when the user asks to close the current session, make a message for the next session, create/export a handoff, resume later, セッションを閉じる, 引き継ぎを作る, or 伝言を作る. Do not use for pasted handoff notes that instruct the current agent to resume work; consume those as instructions instead."
argument-hint: "引き継ぎたい作業、完了条件、再開先セッションへ渡したい制約"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Session Handoff

現在の作業を一度閉じ、新しいセッションでまず状態を認識できるように、貼り付け可能な伝言を作る。
成果物は「次の agent が最初に読むべき最小コンテキスト」であり、作業ログの全文でも即時実行指示でもない。

## When to Use

- ユーザーが `セッションを閉じる` / `引き継ぎを作る` / `伝言を作る` / `handoff を作成` / `resume later` と、次セッション用メッセージの作成を依頼した。
- 長い作業の途中で context が重くなり、次セッションに必要な状態だけを渡したい。
- 未完了タスク、作業中ファイル、検証状況、次に実行するコマンドを残す必要がある。

## Do Not Use For

- ユーザーが handoff 風の本文を貼っただけ、または `次のセッションでは...` で始まる作業指示を現在の agent に実行してほしい場合。これは handoff 作成ではなく、指示の消費・再開として扱う。
- 通常の進捗報告や完了報告だけで足りる小さな依頼。
- 永続的な運用ルールの保存。ルール化が必要なら instruction / skill / repo docs を検討する。
- 秘密情報、トークン、個人情報、認証済み URL を次セッションへそのまま渡す用途。

## Workflow

1. Confirm the user is asking to create a handoff note, not asking this agent to consume an existing handoff-like instruction and continue work now. If ambiguous, ask one short clarification before drafting.
2. Identify the objective and the resume target. Carry at most two objectives: the original one the first request was for, and the current one when the direction has since changed. Inherit both from the handoff that started this session and never swap in whatever this session happened to work on, because that substitution is how a chain of handoffs drifts off the point. Reconstruct the original from the first request when no handoff exists. Confirm the current overarching objective (大目的・現在) with the user in one line before finalizing even when you are confident, folding it into step 1's clarification when both are needed. Until the answer arrives, do not emit the handoff; the user correction wins. Record both with the field rules in [references/handoff-template.md](references/handoff-template.md). Capture this session's goal, requested outcome, and the nearest concrete artifact separately from them.
3. Capture only state needed to continue: touched files, commands already run, validation results, blockers, assumptions, and pending decisions. Write unsent deliverables such as reply drafts, comment bodies, and mail drafts to files and cite the relative path in the note; text quoted only in chat is lost to context compaction.
4. If the repo has uncommitted changes from more than one actor, say which dirty paths are yours and which must not be staged. Otherwise the next session commits someone else's half-finished edits.
5. Separate facts from guesses. Mark uncertain items as `未確認` or `仮説`.
6. Preserve user constraints that still matter, including wording, scope limits, and prohibited actions.
7. When a relevant direct-entry workflow exists, make its invocation the primary candidate selected after explicit approval, whether the target is fixed here or selected by the workflow. Do not restate its phases, lifecycle, acceptance criteria, or operational contract; include only resume state and requirements the workflow does not own.
8. Write a paste-ready handoff using [references/handoff-template.md](references/handoff-template.md).
9. Review the handoff before finalizing: remove secrets, private account identifiers, sensitive URLs, absolute personal paths unless necessary for local continuation, duplicate logs, and stale TODOs.
10. If the user asked for rubber-duck review, or the handoff is non-trivial, run a second-pass review against the checklist below.

## Recovering a Thin Handoff

When a pasted note points at a draft that was never saved to a file, the text may still sit in the local session store. Query it instead of rewriting the draft from memory.

- Read the schema first (`SELECT sql FROM sqlite_master`) and use the real column names. Guessing them costs a failed round trip.
- Filter by the originating session ID from the note, then narrow by a distinctive phrase. Returning whole turns floods context.
- Treat what you recover as a starting draft, not as approved text. Re-verify every claim against the current working tree before reusing it.

## Rubber-Duck Review Checklist

- Does the first line say this is a handoff note pasted from another session, and the current agent should acknowledge and summarize the state plus present A/B choices before taking action?
- Would a fresh agent know the goal without reading the old session?
- Are the original and current objectives both kept, stated separately from this session's goal, rather than replaced by the last session's work?
- Are the A/B candidates and the action after selection unambiguous?
- Are completed, pending, blocked, and unknown items separated?
- Are file paths workspace-relative when possible?
- Are verification results stated with command names and outcomes?
- Are secrets, credentials, and irrelevant transcript details omitted?
- Is the message concise enough to paste as a new-session prompt?
- Are the suggested session name and model presented as suggestions, with `unspecified` when the model cannot be verified?
- Can the next session locate the root session, its immediate predecessor, and the exact repository revision this note describes?

## Output Rules

- Put the paste-ready handoff itself in one fenced `markdown` block so the user can copy it without surrounding commentary.
- Start the block with a self-identifying line: it is a handoff note from another session, and the current agent should first acknowledge and summarize the state plus present A/B next-action choices.
- Do not instruct the next agent to start work immediately. Tell it to wait for explicit user approval before editing files, running commands, or operating external services.
- Avoid wording that sounds like a request to create another handoff, such as starting only with `次のセッションでは...`.
- Prefer bullets over narrative history.
- Include exact commands only when they are safe and likely to be rerun.
- Record the session lineage, the date, and the repository state near the top. Without them the next session cannot pull the original log when the summary turns out to be thin, and cannot tell which revision the described state belongs to. Identifiers are log keys, not credentials, so they are safe to carry; log paths are not, and stay out.
- Build the lineage by inheriting it from the handoff that started this session and appending the current identifier; the root holds the original request that later summaries drop. Write it as `root: <id> → … → this session: <id>`, keeping the root plus the two most recent non-root entries. Never record how many entries the ellipsis hides — an inherited count cannot be recomputed, so requiring one forces the next session to guess.
- Suggest a name for the next session near the top so the user can rename in one step. Use the original session title when known; a title can be absent even when session metadata carries a summary, so fall back to a short goal-derived name instead of searching for one.
- Treat only a trailing ` Re` or ` Re<number>` as a handoff suffix. Replace ` Re` with ` Re2`, increment `<number>` for ` Re<number>`, and otherwise append ` Re`. Present the result as a suggestion, not a unique identifier.
- Suggest one model display name verified in the current environment plus a one-line reason. Mark it advisory: the next session rechecks availability before selecting it. Write `unspecified` when you cannot verify one.
- Do not infer model availability from session history alone; an absent model was not observed in that history, not proven unavailable.
- Include no more than one `Next Candidates` section.
- Include prohibited actions and stop conditions near the top when user safety or external systems are involved.
- End with the expected stop condition or done criteria.

## References

- [handoff-template.md](references/handoff-template.md): Paste-ready structure for the next-session message.
