# UI Fallbacks and Fast Paths

Use these patterns after the normal MCP snapshot/click flow has established the page model.

## Hidden File Input Upload

- If `connectOverCDP()` times out but `/json/list` exposes a page WebSocket URL, use raw CDP.
- For editors with hidden `input[type=file]`, target the existing editor tab and use `DOM.setFileInputFiles`.
- Do not navigate an unsaved draft tab to a new URL. Open a separate new tab for a fresh draft if needed.
- Verify upload by checking the new file URL in page HTML or editor text.

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