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
- While a browser-chrome prompt is visible, `/json/list` can show the destination URL before navigation has completed. Do not treat target URL/title changes as success; re-check `Runtime.evaluate` and durable DOM after the prompt is closed.
- Hard reset when a native dialog has wedged the renderer: closing the wedged tab releases the dialog. But closing the LAST tab via `/json/close/<id>` exits the whole browser process and the debug port closes — relaunch the browser with the same port + profile to recover. Keep a second blank tab open if you want to close a wedged tab without killing the browser.

## A Widget Stops Responding After Many Operations

A single component can wear out while the rest of the page stays healthy: a type-ahead that stops returning suggestions after a few dozen lookups, a picker that no longer opens, an editor that stops accepting input. The page answers `Runtime.evaluate` normally, so none of the dialog checks above apply.

- Reloading often does **not** clear it. When the app restores its state from the server or session storage, the reloaded page rebuilds the same wedged component. A passing reload is not evidence that the component recovered.
- Opening a **new tab** on the same URL usually does, because it constructs a fresh component instance. Prefer that over restarting the browser or clearing the profile.
- Detect the condition instead of retrying blindly: assert the widget's own success signal (a suggestion list appears, the value committed) and treat two consecutive failures as the trigger to move to a fresh tab, once.
- For long unattended loops, build the fresh-tab step into the tool so a run does not stall at the operation count where the widget gives out.

## Context / Page Selection

`connect_over_cdp()` can expose multiple browser contexts and profiles. Never assume `contexts[0].pages[0]` is the right page.

Safe selection:

1. Iterate all contexts.
2. Rank pages by target domain or management URL.
3. Run preflight for login, authorization, and target screen readiness.
4. Use only the first page that passes preflight.
5. If none pass, return compact JSON with URL, title, and failure reason.

Preflight must confirm target domain, no login redirect, and required controls/API visibility.
