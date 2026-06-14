# CDP Recovery and Context Selection

## Disconnection Recovery

When the browser closes or crashes (`Target page, context or browser has been closed`):

1. Check the port: `Invoke-WebRequest -Uri 'http://localhost:<port>/json/version' -TimeoutSec 5`.
2. If refused, restart the browser with the same debugging port and profile/user-data-dir.
3. Confirm `/json/version` returns `Browser`.
4. Reconnect MCP: `browser_close` -> `browser_navigate`.
5. For authenticated sites, release MCP before running Python login helpers, then reconnect for verification.

## Unresponsive but Still Connected

If `/json/list` works but `Runtime.evaluate` or `Page.enable` times out, suspect a JS dialog, beforeunload prompt, reload confirmation, or in-page modal.

- Probe with `Runtime.evaluate({expression: '1+1'})` and a short timeout.
- Try `Page.handleJavaScriptDialog({accept: false})`.
- If no native dialog exists, close in-page overlays with DOM/Escape.
- Browser system dialogs may not be controllable by CDP; ask the user to cancel rather than retrying blindly.

## Context / Page Selection

`connect_over_cdp()` can expose multiple browser contexts and profiles. Never assume `contexts[0].pages[0]` is the right page.

Safe selection:

1. Iterate all contexts.
2. Rank pages by target domain or management URL.
3. Run preflight for login, authorization, and target screen readiness.
4. Use only the first page that passes preflight.
5. If none pass, return compact JSON with URL, title, and failure reason.

Preflight must confirm target domain, no login redirect, and required controls/API visibility.
