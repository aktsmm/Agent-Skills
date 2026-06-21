# CDP Setup

This skill assumes **Edge + CDP + manual ESXP login**.

## Launch Edge

Preferred launch shape (profile directory name with a space, e.g. `Profile 2`):

```powershell
Start-Process 'msedge.exe' `
  -ArgumentList '--remote-debugging-port=9222','--remote-allow-origins=*','"--profile-directory=Profile 2"'
```

Guidelines:

- If the profile directory name contains a space, **inner-quote the whole flag value**: `'"--profile-directory=Profile 2"'`. Passing `'--profile-directory=Profile 2'` (no inner quotes) is NOT enough: even though PowerShell hands it over as one arg, Edge re-splits on the space, reads `--profile-directory=Profile`, and opens a DIFFERENT profile (the one whose dir is `Profile`), silently dropping the ` 2`. Symptom: the wrong account / an un-logged-in profile keeps opening no matter how often you relaunch, and `last_used` rewrites do not help.
- Verify the actual launched value: `Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | ? { $_.CommandLine -match 'profile-directory' -and $_.CommandLine -notmatch '--type=' }`. It must read `--profile-directory="Profile 2"`.
- 既存の wrong profile を流用しない
- Week View が見えるまで手動ログインする

## Required Environment Variables

- `ESXP_CDP_PORT`: CDP port, default `9222`
- `ESXP_USER_ALIAS`: alias used in labor API, default depends on your environment
- `ESXP_EXPECTED_ACCOUNT`: optional, for profile verification

Example:

```powershell
$env:ESXP_CDP_PORT = '9222'
$env:ESXP_USER_ALIAS = 'youralias'
$env:ESXP_EXPECTED_ACCOUNT = 'you@company.com'
```

## Verify The Session

Run this before any mutation:

```powershell
python scripts/verify_esxp_profile.py --strict-account --expected-account you@company.com
```

Failure meanings:

- `Home`: wrong Edge profile or wrong parent account
- `sign-in page`: authentication not finished
- expected text missing: not on the intended request or week view page

## Capture Fresh Auth Headers

`labor_api_tools.py` works only after ESXP Week View has already triggered the submitter API at least once.

Practical health check:

```powershell
python scripts/labor_api_tools.py fetch-week --start-date 2026-06-15 --end-date 2026-06-21 --format table
```

If that fails with no captured API response:

1. reload Week View manually
2. wait for the page to finish
3. rerun `fetch-week`

Capture stability notes:

- An **empty stdout** from an `add-*` / `fetch-week` run does NOT prove failure. PowerShell does not flush a piped/redirected python stdout until the process exits, and the process may still have POSTed. Before retrying a mutation, **verify with `fetch-week` first** to avoid double-posting.
- Capture binds to the first responsive ESXP tab. Commands that reload/iterate many tabs/weeks (e.g. `list_dispatches --all`) degrade the page and make later capture hang. Keep one clean Week View tab; if capture starts failing, close stale ESXP tabs and reopen a single fresh Week View, then continue.
- A slow `/json/list` (10s+) or repeated empty output is a sign the tab is degraded; reopen a fresh Week View rather than retrying the same command.

## Safe Operating Rules

- Do not mix Playwright automation and these Python scripts on the same CDP port at the same time.
- Do not reload the page while there are unsaved draft changes or beforeunload dialogs.
- If the browser looks blocked, check the visible page first. ESXP dialog state often blocks CDP even when the socket is healthy.
