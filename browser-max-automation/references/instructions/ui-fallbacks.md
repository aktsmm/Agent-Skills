# UI Fallbacks and Fast Paths

Use these patterns after the normal MCP snapshot/click flow has established the page model.

## Hidden File Input Upload

- If `connectOverCDP()` times out but `/json/list` exposes a page WebSocket URL, use raw CDP.
- For editors with hidden `input[type=file]`, target the existing editor tab and use `DOM.setFileInputFiles`.
- Do not navigate an unsaved draft tab to a new URL. Open a separate new tab for a fresh draft if needed.
- Verify upload by checking the new file URL in page HTML or editor text.

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