---
name: teams-photo-export
description: Export photos and inline images from Microsoft Teams chats or channel threads into dated local folders. Use when the user shares a Teams chat URL, channel/thread URL, Teams title, or asks to save/download/extract Teams photos/images. Triggers on "Teams photos", "Teams images", "Teams画像保存", "Teams写真抽出", "チャット画像", "Teams URLから画像".
argument-hint: "Teams URL or title; optional output root/date range"
user-invocable: true
disable-model-invocation: true
license: CC BY-NC-SA 4.0
metadata:
  author: aktsmm
---

# Teams Photo Export

Extract images from Microsoft Teams conversations into organized local folders.

## When to Use

- User provides a Teams chat URL, channel/thread URL, or chat title and wants images/photos saved.
- User asks to export, extract, download, collect, or organize Teams photos/images.
- User wants the output under the configured work-photo folder.
- Manual invocation only (`/teams-photo-export`); the skill reads private chat content, so it is never started implicitly.

## Default Output Root

Resolve the output root in this order: `--output-root`, the user environment variable `TEAMS_IMAGE_EXPORT_ROOT`, then `<user pictures folder>\Teams Photo Export`. Ask the user when the destination matters (for example a cloud-synced work-photo folder), and set `TEAMS_IMAGE_EXPORT_ROOT` only with their agreement.

Output folders should be named:

```text
YYYY-MM-DD_<Teams chat/thread/project title>
```

Sanitize Windows-invalid characters: `\ / : * ? " < > |`.

## Strategy

Prefer the no-admin path first.

1. **Teams Web CDP path (default)**: open Teams Web in a dedicated Edge profile, attach Playwright over CDP, scroll the conversation, and save visible `img[alt="メディア"]` / `img[alt="Media"]` blob images.
2. **ASM full-size enhancement (not implemented in the script)**: capturing `asm.skype.com/.../views/imgpsh_fullsize*` responses would give originals instead of preview blobs; today the script saves the rendered blob images only.
3. **Graph hostedContents path (only if consent works)**: use `Chat.Read` or `ChannelMessage.Read.All` and `hostedContents/$value` for original-quality download.
4. **SPO/OneDrive attachment path**: use when `attachments[].contentUrl` points to a file in SharePoint/OneDrive. Inline pasted images usually are not stored there.

Do not rely on native Teams UI Automation as the main path; it is slower and less stable than Teams Web CDP.

## Workflow

1. Parse the input.
   - Chat URL example: extract `19:...@thread.v2` as `chatId`.
   - Channel URLs may need Teams Web navigation; do not assume Graph channel IDs are available.
   - If title search returns multiple candidates, ask the user to choose.
2. Create a dry-run plan.
   - Source URL/title
   - Output root and final folder
   - Date range or scroll limit
   - Expected naming pattern
3. Ask for confirmation before a large export.
4. Run `scripts/export_visible_teams_images.py` for the Teams Web path.
5. Verify saved file count and list the output folder.

## Script Usage

Start or reuse an Edge instance with CDP:

```powershell
python "%USERPROFILE%\.copilot\skills\teams-photo-export\scripts\export_visible_teams_images.py" `
  --url "https://teams.microsoft.com/l/chat/..." `
  --title "Project or chat title" `
  --date "2026-07-02"
```

Useful options:

```text
--output-root <path>     Override TEAMS_IMAGE_EXPORT_ROOT
--max-scrolls <n>        Limit virtual-scroll attempts
--dry-run                Show target folder and detected images without writing
--keep-browser-open      Do not close the dedicated Edge
```

## Safety Rules

- Only export content the signed-in user can access.
- Never send, forward, or share exported images automatically.
- Keep outbound summaries generic; images and chat metadata are private user data.
- Do not log bearer tokens or authenticated Graph URLs.
- Prefer a dedicated Edge user-data-dir so regular browser sessions are not disturbed.
- Do not overwrite existing files; use hashes to skip duplicates and sequence numbers for new files.

## References

- See `references/implementation-notes.md` for Graph/SPO/WebView2 tradeoffs and source URLs.
