# CDP Setup

This skill assumes **Edge + CDP + manual ESXP login**.

## Launch Edge

Preferred launch shape:

```powershell
Start-Process 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' `
  -ArgumentList '--remote-debugging-port=9222','--remote-allow-origins=*','--profile-directory=Profile 2'
```

Guidelines:

- `--profile-directory` に空白があるなら 1 引数として渡す
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

## Safe Operating Rules

- Do not mix Playwright automation and these Python scripts on the same CDP port at the same time.
- Do not reload the page while there are unsaved draft changes or beforeunload dialogs.
- If the browser looks blocked, check the visible page first. ESXP dialog state often blocks CDP even when the socket is healthy.
