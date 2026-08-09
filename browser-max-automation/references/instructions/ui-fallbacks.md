# UI Fallbacks and Fast Paths

Use these patterns after the normal MCP snapshot/click flow has established the page model.

## Hidden File Input Upload

- If `connectOverCDP()` times out but `/json/list` exposes a page WebSocket URL, use raw CDP.
- For editors with hidden `input[type=file]`, target the existing editor tab and use `DOM.setFileInputFiles`.
- Do not navigate an unsaved draft tab to a new URL. Open a separate new tab for a fresh draft if needed.
- Capture existing asset URLs from every active editor surface (textarea, CodeMirror/contenteditable, rendered HTML), call `DOM.setFileInputFiles` once, then require a newly inserted URL. Do not dispatch duplicate `input` / `change` events unless the first upload produced no URL; double dispatch can upload the same file twice.
- If upload creates a persistent temporary draft/entity, return its exact URL or ID as cleanup evidence. Delete only that entity after the downstream article/save is verified; never infer a cleanup target from title or recency alone.
- After deleting that exact entity, reload a clean list/detail view and verify the ID is absent. Dialog dismissal and the pre-delete list DOM are not durable-state evidence because client-side rows can remain stale.

## Native File Chooser (button opens OS picker, no reachable input)

Some flows (e.g. a multi-step "アップロード" wizard) only reveal the `input[type=file]` after a button click that ALSO opens the OS file picker. The native picker blocks the renderer, so any later `Runtime.evaluate` hangs until it is dismissed.

Intercept it instead of letting the OS dialog open:

1. `Page.setInterceptFileChooserDialog({enabled: true})`.
2. Click the button, but **raw-send** the `Input.dispatchMouseEvent` over the WebSocket without consuming responses in an id-matching loop (otherwise the loop swallows the event).
3. Wait for the `Page.fileChooserOpened` CDP event and read its `backendNodeId`.
4. `DOM.setFileInputFiles({backendNodeId, files: [path]})`.
5. `Page.setInterceptFileChooserDialog({enabled: false})`.

For download buttons, set `Browser.setDownloadBehavior({behavior: 'allow', downloadPath: <dir>, eventsEnabled: true})` before clicking so the file lands where you expect instead of the default Downloads folder.

## Shadow-DOM / Material widgets: rect comes back (0,0)

In Angular-Material / web-component UIs (GCP Console, YouTube Studio), many buttons live in shadow DOM and `el.getBoundingClientRect()` returns `{x:0, y:0, width:0}` to page-level JS, so a JS-computed click misses. Click by screenshot pixel coordinates with `Input.dispatchMouseEvent` instead. Also scope element queries to the form region (x/y bounds): a generic `document.querySelector('mat-select,[role=combobox]')` often grabs the page's top search box and opens a search overlay — press Escape to dismiss, then retry within the form area.

## Click times out on "visible, enabled and stable"

Playwright's actionability check can never settle when the browser window is backgrounded or minimized, so `click()` times out even though the element resolved. The snapshot and `fill()` still work because they skip that check.

Fall back to a JS click on the resolved node (`el.click()` on the submit button, or submit the form) instead of retrying the same call. Two consecutive timeouts on the same target mean the route is wrong, not the selector. Some widgets only accept trusted input events and ignore a JS click, so verify the resulting state change rather than the call returning.

## Hiding sensitive UI before a capture

When a selector suppresses something that must not appear in a published image (account avatar, notification badge, tenant name), a zero-match must be an error. Helpers that loop over `querySelectorAll` and hide each hit succeed silently on zero elements, so a renamed class ships the very thing you meant to remove. Return the match count and fail the run when it is 0. Split the selectors into must-hide and optional so localization or A/B variants that legitimately lack an element do not fail every run.

Prefer `visibility: hidden` over `display: none` so the surrounding layout does not reflow; neighbouring content you wanted to keep stays where the recorded crop expects it.

## VS Code Web (Codespaces, github.dev)

- Toggle shortcuts such as `Ctrl+Alt+B` for the secondary side bar flip state on every run. Detect whether the pane is actually visible before pressing, otherwise a rerun undoes what the previous run achieved.
- Shortcuts are swallowed while a preview iframe holds focus. Click the editor area first, then send the key.
- The workbench renders in the browser's UI language, so consent, workspace-trust, and pane labels differ per machine. Match both the English and the localized label when driving buttons.
- The color theme follows the signed-in GitHub account's Appearance setting, and the workbench reads the OS preference rather than a page attribute. With `Sync with system` it opens light on a light OS. Emulate `prefers-color-scheme` over CDP (`Emulation.setEmulatedMedia`); attribute injection that works on GitHub.com pages does nothing here.
- **Browser zoom is per-origin.** A codespace gets a fresh domain on every start, so manual zoom never carries over and cannot be reproduced from a recorded procedure. Drive magnification with the window size instead.
- `workbench.action.zoomIn` is desktop-only and does nothing on the web build. Substituting CDP `Emulation.setDeviceMetricsOverride` is worse: the page stops filling the window, and `page.mouse` coordinates shift so terminal input lands in the wrong place.
- `https://github.dev/<owner>/<repo>` answers 302 to `https://vscode.dev/github/<owner>/<repo>`, so the address bar shows `vscode.dev`. Say so in any caption that promises github.dev.

### CLI prerequisite

`gh codespace` subcommands need the `codespace` scope. On a `gh` OAuth login, `gh auth refresh -h github.com -s codespace` adds it, but that opens a browser authorization and widens the saved authorization, so ask the user before running it. A PAT login needs the scope on the token instead. HTTP 403 "Must have admin rights to Repository" is one symptom of the missing scope, not proof of it.

## evaluate + fetch
When a logged-in session exposes a REST API, prefer `page.evaluate(() => fetch(...))` for bulk read/write. It avoids navigation instability and uses existing cookies with `credentials: 'same-origin'`.

Rules:

- Use UI for login, preflight, and before/after evidence.
- Keep business logic in Python or the main script; let JavaScript execute fetch/write only.
- Complete fetch -> decision -> update -> result return in one evaluation when possible.

## Minimal UI Write Fallback

If API write fails with stale state, guardrail refusal, or route mismatch:

1. Confirm the UI save path is stable.
2. Use the shortest path: search -> select row -> required fields -> save.
3. Verify with list/detail/status text or a read API after save.
4. Record state precisely, such as `saved in UI / pending submit`.

Do not change the business classification just because API automation failed. Change the operation path, then verify the intended destination.

## Slow Transactional Forms

Some enterprise forms keep a separate active-row state, right-pane state, and pending-save state. D365-style expense forms are a common example.

- Treat one row edit as one transaction: select row -> wait for right-pane Amount/Merchant to match -> fill all required fields -> save -> re-read that same row.
- Do not infer success from a button click, toast, or report-level summary. Verify the durable cell/status that represents the real outcome.
- If a pending overlay such as `fastEditRailsMode`, `ShellBlockingDiv`, or `Your last action is still being worked on` appears, stop issuing new writes until it disappears.
- Prefer screenshots plus targeted DOM reads for verification. Large snapshots can be stale or too noisy, while DOM-only reads can miss visually obvious row/detail mismatches.
