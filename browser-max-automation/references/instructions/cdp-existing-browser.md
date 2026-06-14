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

## Rules

- Treat "port is open" and "right profile is logged in" as separate checks.
- Do not trust an endpoint value from an environment variable or previous run without `/json/version` and process command-line verification.
- If Chrome owns the intended Edge port, use another port or close Chrome before starting Edge.
- If the same Edge user-data-dir already has a CDP port, launch another profile without `--remote-debugging-port`; the window joins the existing process and remains visible through the existing CDP endpoint.
- Pass the verified CDP URL explicitly to helpers so later scripts do not re-guess a different endpoint.

## Authentication Gotchas

- Prefer headful existing profile + CDP over temporary `--user-data-dir` for sites that rely on cookies or device auth.
- For `/json/new?<url>`, URL-encode the full target URL. Unencoded `&state=...` or callback parameters are parsed by the CDP endpoint and disappear from the site URL.
- Close stale auth tabs before retrying expired OAuth or callback flows.