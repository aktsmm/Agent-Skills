# CDP Recovery and Context Selection

## Disconnection Recovery

When the browser closes or crashes (`Target page, context or browser has been closed`):

1. Check the port: `Invoke-WebRequest -Uri 'http://localhost:<port>/json/version' -TimeoutSec 5`.
2. If refused, verify whether the owned process exited. Restart only an authorized owned instance, applying the foreground-exception rule before launch; never restart a user's browser or another session's process automatically.
3. Confirm `/json/version` returns `Browser`.
4. Reconnect using the tool's verified attachment semantics; `browser_close` is not a generic disconnect. Re-establish the owned target identity, authentication, and durable state before any write.
5. If another helper is needed, stop the owned controller and detach without destroying tabs. If safe detachment is unavailable, retain the current route or stop. Reconnection never resets the logical operation's recovery budget.

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
4. Default to dry-run. On explicit apply within the authorized browser task, recheck the candidate and invoke its `InvokePattern` once. Do not activate the window or send global keystrokes to make matching succeed; announce any necessary activation under the foreground-exception rule. Do not click coordinates, accept Leave, target permission/authentication prompts, or operate another tab.
5. Verify both dialog disappearance and `Runtime.evaluate` response on the same owned target. A repeat with no matching dialog must not click anything. If readback fails, record dismissal and page recovery separately rather than claiming success.

Keep screenshots, capture time and sanitized recovery results; protect exact addresses and identifiers in private records. Read persisted settings separately: Cancel leaves a dirty form dirty. Use a clean work tab for subsequent server-state reads and never overwrite the original evidence.

## A Widget Stops Responding After Many Operations

A single component can wear out while the rest of the page stays healthy: a type-ahead that stops returning suggestions after a few dozen lookups, a picker that no longer opens, an editor that stops accepting input. The page answers `Runtime.evaluate` normally, so none of the dialog checks above apply.

- Reloading often does **not** clear it. When the app restores its state from the server or session storage, the reloaded page rebuilds the same wedged component. A passing reload is not evidence that the component recovered.
- A fresh owned background tab may rebuild the component. Choose this as the single recovery after the initial failure, not an extra attempt after two failures. Preserve the original dirty tab and verify the replacement's authentication and resource identity.
- Assert the widget's actual success signal. Before replaying a write, establish non-application or use duplicate protection; unknown outcomes stop the operation. No new tab, tool, or script resets the shared two-attempt budget.
- For long loops, persist completed item IDs and the last verified stage. Resume only unresolved work after ownership and state checks, and do not confuse healthy asynchronous progress with another failed attempt.

## Context / Page Selection

`connect_over_cdp()` can expose multiple browser contexts and profiles. Never assume `contexts[0].pages[0]` is the right page.

Safe selection:

1. Enumerate contexts/pages only to identify the approved profile and workload; domain matches are candidates, not ownership evidence.
2. Reuse an explicitly designated target or create a dedicated background work tab using [the existing-browser procedure](cdp-existing-browser.md#background-work-tab).
3. Verify login, authorization, origin, resource route, and required controls. Pin that context and target ID for the run.
4. Before writes, re-check route, resource/item identity, and absence of competing user editing. Pause on drift or ownership uncertainty; do not silently choose another matching tab.
5. If identity or readiness cannot be established, return a compact stopped state with sanitized URL/title and reason. After a crash, rebind explicitly instead of pretending the old target ID is still valid.
