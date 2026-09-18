# Existing Browser CDP

Use this when reusing an already-authenticated browser profile through CDP.

## Start and Verify

Start a headed browser with a debugging port only when no suitable CDP endpoint exists. Launch can activate a window; apply the Skill's foreground-exception rule before launching rather than promising a silent start:

```powershell
Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  -ArgumentList '--remote-debugging-port=9222', '"--profile-directory=Profile 2"'
```

Before using an endpoint, verify both the port owner and browser identity:

```powershell
$conn = Get-NetTCPConnection -LocalPort 9222 -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) {
  Get-CimInstance Win32_Process -Filter "ProcessId=$($conn.OwningProcess)" |
    Select-Object ProcessId, Name, CommandLine
}
(Invoke-WebRequest "http://localhost:9222/json/version" -UseBasicParsing).Content |
  ConvertFrom-Json | Select-Object Browser
```

If CDP startup may already be automated, inspect its owner before adding another startup path. On Windows, read the existing scheduled task's `Actions`, `Triggers`, principal, and settings first. For a time-only change, update only the trigger with `Set-ScheduledTask`, preserve the action/profile flags, then read the task back and verify `StartBoundary` and `Actions`.

## Rules

- Treat "port is open" and "right profile is logged in" as separate checks.
- Verify listener PID and process arguments before connecting, then corroborate the owned endpoint with `/json/version` and target URLs. A launched browser may fail to bind while another answers; disagreement is an ownership failure, not permission to drive whichever endpoint responds.
- Quote the whole `--profile-directory=<name>` switch when the profile name contains a space. An unquoted one can be split by the shell into `--profile-directory=<first word>` plus a bare trailing token, which silently selects a different existing profile and can be opened as a URL instead (a window titled `0.0.0.2` is one observed signature of a trailing `2`). Verify which profile actually resolved rather than that a window appeared.
- Terminate only the instance you started: match on the PID or process tree you launched, or on the PID owning the CDP port. Do not match by process name or image path, which also hits the user's own browser. Giving your instance a unique `--user-data-dir` makes a command-line filter unambiguous; the default profile has no such switch to match on.
- Closing every window may still leave the profile locked. Chrome can keep a windowless background process launched with `--no-startup-window`, and a window-based close never reaches it, so a relaunch with a debugging port joins the locked instance instead of opening the port.
- Do not trust an endpoint value from an environment variable or previous run without `/json/version` and process command-line verification.
- Treat a task-update command's success as provisional until `Get-ScheduledTask` read-back confirms the trigger and browser action. Distinguish retiming an existing owner from creating a new task.
- Inventory listener ownership and dedicated profiles through OS metadata before querying CDP. Exclude other sessions and unknown owners from endpoint discovery; neither the first open port nor `Default` proves the intended account.
- Isolation requires an unused user-data-dir and a free port, not just another profile-directory. Verify both against active process arguments/listeners before launch, then verify the new listener, profile, account and owned target. Do not stop another browser to free a port or clone its credentials.
- Another profile within the same user-data-dir can join the existing process. Use this only for explicitly coordinated reuse, never to isolate concurrent controllers.
- If Edge is already running **without** any debug port, a new `--remote-debugging-port` launch joins the existing portless process and the port never opens (`/json/version` keeps failing). Close all Edge processes first, then relaunch with the port. Closing all Edge is destructive (drops every open tab), so confirm with the user before `Stop-Process -Name msedge`.
- A range-scanning launcher must exclude other sessions before probing. Reuse only verified owned listeners; for isolation, constrain discovery to a verified free port and specify a different user-data-dir. A launch exit code does not prove the requested port opened.
- After sign-in, a stale tab can still show the pre-auth URL. Use the background work-tab procedure below to re-verify the authenticated state before declaring the session unusable or relaunching anything.
- A single `location.href` read is not evidence either way. A tab can still show the requested URL while the sign-in redirect is in flight, so an early read reports authenticated and the tab lands on the login page seconds later. Wait for the URL to stop changing, then confirm an authenticated control on the page.
- When a helper connects from Node, pass `http://127.0.0.1:<port>` rather than `localhost`. `localhost` can resolve to IPv6 `::1` while the CDP endpoint listens on IPv4, so PowerShell reaches it but Node `fetch` fails with `fetch failed`.
- Pass the verified endpoint and owned target explicitly to helpers. Test that CLI options reach the client instead of being replaced by defaults; preserve documented environment fallback for callers without explicit options. Disable profile re-resolution after binding, and reject missing/drifted targets rather than picking the first domain match.
- On a shared authenticated browser, bind an explicitly owned work tab and address every raw-CDP call by that exact target ID. Re-check URL, route, and query before writes. Cleanup must preserve dirty or user-owned tabs and the last tab of a shared browser.

## Background Work Tab

- Verify the endpoint, profile/context, and ownership before creating a target. On a compatible browser-level CDP connection, use `Target.createTarget` with the intended URL, `background: true`, and `newWindow: false`; retain the returned target ID. Do not create a new browser context when the goal is to reuse its existing login.
- The protocol's optional `focus: false` is experimental: check support before relying on it. Do not assume `/json/new`, a CLI tab command, or an MCP navigation call preserves tab selection or OS focus. If no verified non-activating route exists, use the foreground-exception rule rather than silently dropping the background requirement.
- Attach to the pinned target without `Target.activateTarget` or `Page.bringToFront`. Navigation, DOM queries, scoped input, and capture are candidates for background execution, not a guarantee for every browser/widget. Do not minimize the browser as a substitute; rendering may be throttled.
- Do not use `requestAnimationFrame` as the only readiness wait on a background target; it can be throttled indefinitely. Use a bounded protocol/timer wait, or apply the documented foreground exception before an interaction that truly requires rendering.
- Monitor foreground changes throughout a safe pilot (for example, a passive OS foreground-event listener) and verify the user's selected tab remains unchanged. `document.hasFocus()` and before/after window snapshots cannot exclude a brief OS focus steal. Attribute user-initiated switches separately from automation.

Protocol: https://chromedevtools.github.io/devtools-protocol/tot/Target/#method-createTarget

## Screenshot Capture

- In `connect_over_cdp()` workflows, `page.screenshot()` can ignore the emulated `deviceScaleFactor` and save at 1x even when the override succeeded. When you need a deterministic DPR, send `Page.captureScreenshot` on a CDP session and pass the scale inside the clip: `{"format": "png", "captureBeyondViewport": True, "clip": {**rect, "scale": dpr}}`. Keep `Emulation.setDeviceMetricsOverride` at `deviceScaleFactor: 1` so layout stays in CSS pixels. That combination can itself re-lay out the page, returning a capture at a different rendered width with regions blank. When it does, invert the split: pin `Emulation.setDeviceMetricsOverride` at the target `deviceScaleFactor`, let layout settle, and capture with `clip.scale` at 1. Drop `captureBeyondViewport` when the region already fits the viewport.
- Promotional and experiment banners that render inside a component are not toasts, so clearing notifications leaves them in the frame. Find the container by class, remove it from the DOM before capturing, and record what was removed.
- Capture without activation first and inspect the saved image. If a background capture is incomplete, use one bounded readiness/scroll recovery on the owned target. Only if activation is necessary, explain the foreground exception before that step; never routinely call `page.bring_to_front()`.
- Lazily rendered or virtualized regions can remain blank even with `captureBeyondViewport`. Re-measure after scrolling and check the saved file. Both capture attempts share the recovery budget; if still incomplete, report unverified capture. A previous image may be retained as historical evidence, never presented as proof of the current state.
- Injecting a theme attribute (for example `data-color-mode`) only switches the theme when the matching stylesheet was already shipped, so the account's Appearance setting decides whether it works. An account pinned to a single theme never loads the other one: backgrounds flip while text colors stay from the original theme and produce an unreadable hybrid. An account left on `Sync with system` ships both, so injection works and you can leave the account alone. Check which case you are in first; only change the account setting when injection produces the hybrid, and record the original value so you can restore it.
- Disable animations before capturing: `page.add_style_tag(content="*, *::before, *::after { animation: none !important; transition: none !important; }")`.
- Prefer selecting the capture region and any highlight frames by CSS selector over hand-counted pixel offsets. Selector-based clipping stays reproducible when the page reflows.
- Both `page.screenshot()` and `Page.captureScreenshot` capture page content only, so the address bar and window chrome are lost. When the point of the figure is that something runs _in a browser_, capture the window with Windows `PrintWindow(hwnd, hdc, 2)` (PW_RENDERFULLCONTENT), which avoids z-order dependence when the call succeeds. Check the return value, because a failure silently produces a blank bitmap, and inspect the saved image as well since some apps still render incompletely. Window chrome carries avatars, notification badges, bookmarks, and URLs, so review it before publishing: crop the tab strip off, mask the extension icon cluster, and validate those coordinates against the source size so a resized window does not leave them visible.

## Authentication Gotchas

- Prefer headful existing profile + CDP over temporary `--user-data-dir` for sites that rely on cookies or device auth.
- Chrome 136+ ignores `--remote-debugging-port` / `--remote-debugging-pipe` against its default data directory and requires a non-standard `--user-data-dir`; check other Chromium browsers separately. Do not treat a renamed path, junction, or copied profile as proof that an authenticated session is reusable. Source: https://developer.chrome.com/blog/remote-debugging-port
- Copied profile cookies can be app-bound or device-bound and may decrypt only in the original profile context. After any profile copy, verify the target site URL and authenticated controls; a cookie row existing on disk is not login evidence.
- Treat a temporary profile directory as a single-owner lifecycle: copy, launch, use, stop, then delete. Never copy, delete, or launch the same directory in parallel; a partial copy or competing process can create misleading authentication state.
- If password login is the approved fallback, require an explicit opt-in flag for each run. Read secrets from a runtime secret source, never print them, stop on MFA/additional verification, and provide a login-only smoke test that exits before uploads or other writes.
- For `/json/new?<url>`, URL-encode the full target URL. Unencoded `&state=...` or callback parameters are parsed by the CDP endpoint and disappear from the site URL.
- Close only owned, clean stale auth tabs before retrying expired OAuth or callback flows; do not close the user's tab or the last shared-browser tab.
- When the active browser cannot be reused, prefer an unused dedicated profile and free port without closing or copying the active profile. An owned clean tab's expired-session Reload/Relaunch may restore its own SSO; verify live authenticated controls afterward. Notify the user immediately for credentials/MFA. Cleanup only the process/directory created for this run, preserving reusable profiles and other sessions.
