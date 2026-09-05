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

- Use one short read probe. `Page.getFrameTree` can also stall; switching from JavaScript to another page command does not exclude a browser-chrome modal.
- For a known leave-site confirmation on the owned target, try `Page.handleJavaScriptDialog({accept: false})` once. A `No dialog is showing` response describes that CDP session, not the entire browser window. If page commands still stall, inspect native UI before asking the user to intervene.
- Keep `Page.enable`, dialog events and command responses on the same WebSocket session when using event-driven recovery; dispatch responses by command ID instead of dropping dialog notifications.
- While a browser-chrome prompt is visible, `/json/list` can show the destination URL before navigation commits. Verify the actual address and same-target DOM after dismissal; do not infer navigation or save success from the target list.
- Do not close tabs, kill the browser, clear profiles or blindly send Escape/Enter to recover a dirty editor. If safe ownership and dialog matching cannot be established, request manual Cancel/Stay and preserve the stopped state.

### Windows Browser-Chrome Leave-Site Prompt

Use native UI Automation only to cancel an identified leave-site prompt, not as a generic consent handler. Cancellation preserves the form; Leave can discard it.

1. Resolve the loopback CDP listener's owning process and verify the expected browser executable and dedicated profile. Pin the target ID and the application's owned resource identity. Enumerate only that process's top-level windows with `UIAutomationClient` / `UIAutomationTypes`.
2. In that window, match the selected-tab address bar through `ValuePattern` against the approved origin and resource route. A matching process or generic window title alone is insufficient. Refuse unrelated URLs, multiple candidates or an unavailable address.
3. Require an exact leave-site dialog title, unsaved-changes warning, and one visible enabled Cancel/Stay button in that dialog subtree, using labels actually observed for the current locale. Edge can expose the dialog as a `RootView` window while CDP reports none. Treat class names as observed hints, not universal version guarantees.
4. Default to dry-run. On explicit apply within the authorized browser task, recheck the candidate and invoke its `InvokePattern` once. Do not click coordinates, accept Leave, target permission/authentication prompts, or operate another tab.
5. Verify both dialog disappearance and `Runtime.evaluate` response on the same owned target. A repeat with no matching dialog must not click anything. If readback fails, record dismissal and page recovery separately rather than claiming success.

Keep screenshots, capture time and sanitized recovery results; protect exact addresses and identifiers in private records. Read persisted settings separately: Cancel leaves a dirty form dirty. Use a clean work tab for subsequent server-state reads and never overwrite the original evidence.

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
