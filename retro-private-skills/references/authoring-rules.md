# Authoring Rules

## Edit Rules

- Before writing a new rule, check whether the repository already implements the same decision in scripts, generated assets, or another skill. A rule that contradicts working code makes the next run "fix" assets that were already correct.
- A single negative observation is not a rule. Before writing "the feature is absent here", rule out authentication state, extension activation, and mode: a half-initialised client renders its surrounding UI while omitting the entries you were looking for. If you cannot rule them out, record the observation with its conditions rather than as an absolute.
- Compaction targets the minimum information the model needs to act; human readability is secondary.
- Use this refactor order: delete text unnecessary for normal/exception/stop decisions -> merge/compact needed text -> move long detail to `references/` -> add missing guidance. Age alone does not obsolete history; confirm its original is preserved before removal and retain unsaved notes.
- Do not add generic or obvious process advice; prefer gotchas, verification checks, and failure-avoidance rules that change future behavior.
- Preserve non-obvious decision criteria, gotchas, done criteria, and failure-avoidance rules.
- Do not repeat the same `Learning / Evidence / Impact` in different wording.
- Classify every learning so none stays unprocessed. An out-of-scope learning is `handoff` when its recommended destination is confirmed and `確認待ち` otherwise, never `見送り` merely for being out of scope. A `review-only` proposal is `提案のみ`, never reported as reflected.

## Apply Details

- For new skills, create at minimum `SKILL.md` with frontmatter: `name`, `description`, `argument-hint`, `user-invocable`, `license`, and `metadata.author` when the repo convention uses them.
- Verify table/formatter drift; group relevant formatting with the owning skill's small change. Separate unrelated normalization; never blanket-stage or split one bounded improvement into repeated pushes.

## Report Template

Use this compact report:

```markdown
# Retro: [Title]
- Target: <private-repo>/.github/skills/<skill>/...
- Learnings: <what changed behavior>
- Outcomes: <each learning -> 反映済み / 既存で充足 / 見送り / handoff / 確認待ち / 承認待ち / 提案のみ>
- Changes: <files changed>
- Commit: <hash or none>
- Gate: pass / stop reason
```
