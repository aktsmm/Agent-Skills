# Existing Browser CDP

Use this when reusing an already-authenticated browser profile through CDP.

## Start and Verify

Start Edge with a debugging port only when no suitable CDP endpoint exists:

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
- Do not trust an endpoint value from an environment variable or previous run without `/json/version` and process command-line verification.
- Treat a task-update command's success as provisional until `Get-ScheduledTask` read-back confirms the trigger and browser action. Distinguish retiming an existing owner from creating a new task.
- Before launching a new, `Default`, or copied profile, enumerate active CDP endpoints and known dedicated profiles. Query `/json` on each candidate; prefer one explicitly tied to the target workload or already showing the target domain, then verify its login state. Do not pick the first open port or assume `Default` is the right profile. If no candidate is verified, require an explicit profile choice or manual login before using a temporary copy.
- If Chrome owns the intended Edge port, use another port or close Chrome before starting Edge.
- If the same Edge user-data-dir already has a CDP port, launch another profile without `--remote-debugging-port`; the window joins the existing process and remains visible through the existing CDP endpoint.
- If Edge is already running **without** any debug port, a new `--remote-debugging-port` launch joins the existing portless process and the port never opens (`/json/version` keeps failing). Close all Edge processes first, then relaunch with the port. Closing all Edge is destructive (drops every open tab), so confirm with the user before `Stop-Process -Name msedge`.
- When a helper connects from Node, pass `http://127.0.0.1:<port>` rather than `localhost`. `localhost` can resolve to IPv6 `::1` while the CDP endpoint listens on IPv4, so PowerShell reaches it but Node `fetch` fails with `fetch failed`.
- Pass the verified CDP URL explicitly to helpers so later scripts do not re-guess a different endpoint. If a helper already has a verified CDP URL, disable profile re-resolution and strip stale profile-query environment variables unless you intentionally want the helper to launch/resolve a different browser profile.

## Authentication Gotchas

- Prefer headful existing profile + CDP over temporary `--user-data-dir` for sites that rely on cookies or device auth.
- For `/json/new?<url>`, URL-encode the full target URL. Unencoded `&state=...` or callback parameters are parsed by the CDP endpoint and disappear from the site URL.
- Close stale auth tabs before retrying expired OAuth or callback flows.
- When the existing Edge is running **without** a debug port and killing every Edge process is not acceptable (open tabs, dirty editors, other workflows), do not force-close it. Escape hatch: `robocopy` the target profile (e.g. `Default`) to a temporary `%TEMP%\edge-cdp-<purpose>` and launch a separate instance with `--user-data-dir=<tmp> --profile-directory=Default --remote-debugging-port=<new-port>`. The original Edge stays untouched. The copied profile may still need a fresh login because some cookies, OAuth refresh tokens, or device-bound credentials do not survive the copy — accept manual re-login as part of the flow. After the session, kill the msedge processes bound to the new port and remove the temporary `user-data-dir`. To keep the copy small (full profiles are often 1–2 GB), exclude transient caches: `robocopy <src>\Default <dst>\Default /E /XJ /XD Cache Cache2 CacheData "Code Cache" GPUCache "Service Worker" Crashpad ShaderCache "Default Cache"`. Cleanup one-liner: `Get-NetTCPConnection -State Listen -LocalPort <port> | %{ Stop-Process -Id $_.OwningProcess -Force }; Remove-Item "$env:TEMP\edge-cdp-<purpose>" -Recurse -Force`.
