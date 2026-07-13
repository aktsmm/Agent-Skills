---
name: export-session-log
description: "Export the current chat session as a structured Markdown work timeline or blog-draft seed. Use when the user asks for a session log, work log, timeline, 作業ログ, ブログネタ, blog draft, article seed, Zenn, Qiita, or はてな. Do not use for verbatim dialogue export or distilled reusable knowledge only."
argument-hint: "Topic, purpose (standard/blog), and optional destination"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: aktsmm
---

# Export Session Log

Turn the available conversation, tool results, changed files, and commands into a concise Markdown work log that supports handoff, resumption, or article drafting.

## When to Use

- The user asks for a `session log`, `work log`, `timeline`, `作業ログ`, or to save the current session.
- The user asks for `ブログネタ`, a `blog draft`, an `article seed`, or material for Zenn, Qiita, or Hatena.
- The work history, decisions, validation results, and next steps need to be preserved for later use.

## Do Not Use For

- A transcript that reproduces every message in dialogue order.
- Knowledge extraction that intentionally omits the session history.
- Reconstructing work that is not present in the available conversation or evidence.

## Workflow

1. Infer the topic, standard or blog intent, and any explicit destination from the request.
2. Read the current local time from the system and use the actual value in `yyyy-MM-ddTHH:mm:ss` format. With PowerShell, run `Get-Date -Format "yyyy-MM-ddTHH:mm:ss"`.
3. Resolve the output root using the priority rules below. Ask before creating anything only when no root can be resolved.
4. Extract the summary, phases, changed files, learnings, useful commands, references, outcome, and unfinished work from available evidence.
5. Create or append the log using [session-log-template.md](references/session-log-template.md).
6. Read the saved file back and verify its frontmatter, title, Timeline, actual `exported_at`, and any required References.
7. Report the saved path and the final `success`, `partial`, or `failed` status.

## Output Root Resolution

An explicit destination always wins. Otherwise resolve by intent:

| Intent | Environment variable | Workspace fallback |
| --- | --- | --- |
| Standard | `EXPORT_SESSION_LOG_DIR` | `{workspace}/output_sessions/` |
| Blog | `EXPORT_SESSION_BLOG_DIR` | Existing `{workspace}/drafts_topic/` |

- For blog output, ask for a destination when the environment variable is unset and `drafts_topic/` does not exist.
- Ask for a destination when there is no workspace and the applicable environment variable is unset.
- Do not create a directory or file before resolving the output root.

## File Naming And Append Rules

- Name new files `YYYYMMDD-NN--{topic}.md`.
- Use a short, descriptive, lowercase kebab-case topic.
- Append to an existing same-day, same-topic file in the resolved destination.
- Otherwise increment the highest same-day `NN`; start at `01` when none exists.
- When appending, preserve the existing frontmatter and body, then add the append block from the template.

## Content Rules

- Choose `type` from `coding`, `research`, `debug`, `design`, or `discussion`.
- Record only tools that were actually used.
- Use `Phase N - {phase name}` headings rather than invented timestamps.
- Compress three or more repeated attempts into `N attempts` plus the final resolution.
- Prefer workspace-relative Markdown links for changed files.
- When external pages informed a conclusion, list only the pages actually used, with title and URL, under References.
- When another workspace file informed the work or is needed to resume it, list a sufficiently identifying path under References.
- Include only reusable commands. Remove secrets, tokens, passwords, personal data, and sensitive local values.
- Never present guessed times, unexecuted commands, unused search candidates, or hidden reasoning as session evidence.

## Success Contract

- The Markdown file exists at the resolved destination and follows the requested intent and naming rules.
- The log captures the current session outcome, verification evidence, and remaining work at a resumable level.
- External sources and cross-workspace files have corresponding References when they were used.
- The result contains no secrets, sensitive data, or hidden reasoning.
