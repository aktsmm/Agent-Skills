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
- When the port owner's process name and `/json/version` disagree, believe `/json/version` and `/json/list`: they describe the endpoint you will actually drive. A browser you just launched can fail to bind while an unrelated one keeps answering on that port, so a matching entry in the process table is not proof you are attached to your own instance. Read the open tabs before the first action, because the wrong endpoint is usually someone's real session.
- Quote the whole `--profile-directory=<name>` switch when the profile name contains a space. An unquoted one can be split by the shell into `--profile-directory=<first word>` plus a bare trailing token, which silently selects a different existing profile and can be opened as a URL instead (a window titled `0.0.0.2` is one observed signature of a trailing `2`). Verify which profile actually resolved rather than that a window appeared.
- Terminate only the instance you started: match on the PID or process tree you launched, or on the PID owning the CDP port. Do not match by process name or image path, which also hits the user's own browser. Giving your instance a unique `--user-data-dir` makes a command-line filter unambiguous; the default profile has no such switch to match on.
- Closing every window may still leave the profile locked. Chrome can keep a windowless background process launched with `--no-startup-window`, and a window-based close never reaches it, so a relaunch with a debugging port joins the locked instance instead of opening the port.
- Do not trust an endpoint value from an environment variable or previous run without `/json/version` and process command-line verification.
- Treat a task-update command's success as provisional until `Get-ScheduledTask` read-back confirms the trigger and browser action. Distinguish retiming an existing owner from creating a new task.
- Before launching a new, `Default`, or copied profile, enumerate active CDP endpoints and known dedicated profiles. Query `/json` on each candidate; prefer one explicitly tied to the target workload or already showing the target domain, then verify its login state. Do not pick the first open port or assume `Default` is the right profile. If no candidate is verified, require an explicit profile choice or manual login before using a temporary copy.
- If another browser owns the intended port, use a free port; do not close that browser to free the port.
- If the same Edge user-data-dir already has a CDP port, launch another profile without `--remote-debugging-port`; the window joins the existing process and remains visible through the existing CDP endpoint.
- If Edge is already running **without** any debug port, a new `--remote-debugging-port` launch joins the existing portless process and the port never opens (`/json/version` keeps failing). Close all Edge processes first, then relaunch with the port. Closing all Edge is destructive (drops every open tab), so confirm with the user before `Stop-Process -Name msedge`.
- A launcher that owns a port _range_ must scan the whole range for a listener before deciding "no session exists" and starting a browser. Probing only the first port and relaunching makes the new process join the existing one, exit with code 0, and never open the requested port — the failure reads like a startup bug but the session was already up on a neighbouring port.
- After sign-in, a stale tab can still show the pre-auth URL. Use the background work-tab procedure below to re-verify the authenticated state before declaring the session unusable or relaunching anything.
- A single `location.href` read is not evidence either way. A tab can still show the requested URL while the sign-in redirect is in flight, so an early read reports authenticated and the tab lands on the login page seconds later. Wait for the URL to stop changing, then confirm an authenticated control on the page.
- When a helper connects from Node, pass `http://127.0.0.1:<port>` rather than `localhost`. `localhost` can resolve to IPv6 `::1` while the CDP endpoint listens on IPv4, so PowerShell reaches it but Node `fetch` fails with `fetch failed`.
- Pass the verified CDP URL explicitly to helpers so later scripts do not re-guess a different endpoint. If a helper already has a verified CDP URL, disable profile re-resolution and strip stale profile-query environment variables unless you intentionally want the helper to launch/resolve a different browser profile.
- On a shared authenticated browser, bind an explicitly owned work tab and address every raw-CDP call by that exact target ID. Re-check URL, route, and query before writes. Cleanup must preserve dirty or user-owned tabs and the last tab of a shared browser.

## Background Work Tab

- Verify the endpoint, profile/context, and ownership before creating a target. On a compatible browser-level CDP connection, use `Target.createTarget` with the intended URL, `background: true`, and `newWindow: false`; retain the returned target ID. Do not create a new browser context when the goal is to reuse its existing login.
- The protocol's optional `focus: false` is experimental: check support before relying on it. Do not assume `/json/new`, a CLI tab command, or an MCP navigation call preserves tab selection or OS focus. If no verified non-activating route exists, use the foreground-exception rule rather than silently dropping the background requirement.
- Attach to the pinned target without `Target.activateTarget` or `Page.bringToFront`. Navigation, DOM queries, scoped input, and capture are candidates for background execution, not a guarantee for every browser/widget. Do not minimize the browser as a substitute; rendering may be throttled.
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
- If password login is the approved fallback, require an explicit opt-in flag for each run. Read secrets from a runtime secret source, never print them, stop on MFA/additional verification, and provide a login-only smoke test that exits before uploads or other writes.
- For `/json/new?<url>`, URL-encode the full target URL. Unencoded `&state=...` or callback parameters are parsed by the CDP endpoint and disappear from the site URL.
- Close only owned, clean stale auth tabs before retrying expired OAuth or callback flows; do not close the user's tab or the last shared-browser tab.
- When the existing Edge is running **without** a debug port and killing every Edge process is not acceptable (open tabs, dirty editors, other workflows), do not force-close it. Escape hatch: `robocopy` the target profile (e.g. `Default`) to a temporary `%TEMP%\edge-cdp-<purpose>` and launch a separate instance with `--user-data-dir=<tmp> --profile-directory=Default --remote-debugging-port=<new-port>`. The original Edge stays untouched. The copied profile may still need a fresh login because some cookies, OAuth refresh tokens, or device-bound credentials do not survive the copy — accept manual re-login as part of the flow. After the session, kill the msedge processes bound to the new port and remove the temporary `user-data-dir`. To keep the copy small (full profiles are often 1–2 GB), exclude transient caches: `robocopy <src>\Default <dst>\Default /E /XJ /XD Cache Cache2 CacheData "Code Cache" GPUCache "Service Worker" Crashpad ShaderCache "Default Cache"`. Cleanup one-liner: `Get-NetTCPConnection -State Listen -LocalPort <port> | %{ Stop-Process -Id $_.OwningProcess -Force }; Remove-Item "$env:TEMP\edge-cdp-<purpose>" -Recurse -Force`.
