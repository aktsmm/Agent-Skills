# Isolated VS Code Capture via CDP

Use when screenshots or demo material must be saved as files from VS Code desktop (Electron), including Copilot Chat walkthroughs and PoC evidence. Desktop-control tools only return images to the conversation and cannot save screenshot files, and capturing through shell or other routes is typically prohibited by tool rules, so drive and capture through CDP instead.

## Launch (isolated)

```powershell
code --user-data-dir=<throwaway-profile> --remote-debugging-port=<unused-port> --remote-allow-origins=* --new-window --disable-workspace-trust <folder>
```

- A throwaway `--user-data-dir` keeps the user's own VS Code window and settings untouched; a port that is already taken joins the wrong process, so check it is unused first.
- Pin the page target from `/json/list` (`type == page`), then use direct WebSocket CDP ([cdp-direct-websocket.instructions.md](cdp-direct-websocket.instructions.md)).
- Call `Emulation.setDeviceMetricsOverride` (for example 1440x900) before shooting so coordinates and framing stay consistent.
- Save with `Page.captureScreenshot` (PNG) to files; `Input.insertText` types text; click by DOM text rather than guessing coordinates.
- Check the integrated terminal before assuming it is unavailable; it has opened fine in an isolated profile.

## Step-file helper

Keep a small helper that executes a JSON step list (ops such as `emu`, `wait`, `clicktext`, `click`, `key`, `type`, `shot`) so each run stays short.

- A synchronous shell call that waits longer than roughly 60-90 s may be moved to the background by the host. Split long scenarios into several short step files and read results in later calls.
- A just-written PNG may briefly appear missing to a viewer; re-open it once after the command completes.
- Delete helper files by explicit name, never with wildcards.
- `clicktext` matches visible elements (width > 0) whose `innerText` starts with the label. The default selector misses dialog buttons; pass `a,button,.monaco-button`.

## Copilot sign-in in a fresh profile

- Click the chat or status-bar `Sign In` (`.monaco-button`, text match), then `Continue with GitHub` (first `.monaco-button`).
- The default browser opens the GitHub authorization page. Stop and ask the human to approve; never automate credentials or MFA. After approval Chat shows a Sessions list.

## Driving Copilot Chat

- Click the chat input by coordinates (about x=1290, y=781 at 1440x900), `Input.insertText`, press Enter, wait 40-60 s, then capture.
- Save each step's full prompt text to a file so the final report can list the prompts in order.
- Agent mode raises dialogs such as "Allow reading file outside of workspace?" and `Allow Once / Skip / Allow All`. Capture before and after each approval, click `Allow Once` one at a time (not `Allow All`), and record each as a human-intervention point.
- Toasts (for example an MCP prompt) are dismissed with `No thanks` after capturing.

## Privacy and provenance

- The isolated window can inherit instruction files from parent folders and show the user's other chat sessions and private text. Mark such screenshots "mask required before sharing" in the material catalog.
- If helper files (modules, README) already exist in the opened folder at start, that is legitimate reuse; record which assets pre-existed in the catalog and final report so viewers understand the demo.
