# Windows Subprocess and CDP Stability

Use this when running Playwright/CDP automation from a CLI helper on Windows.

## PIPE Deadlock

`subprocess.Popen(stdout=PIPE)` + `communicate()` can deadlock because Playwright's Node/browser process tree keeps pipe handles open. Redirect stdout/stderr to files and poll the process instead.

```python
with open(stdout_path, "w", encoding="utf-8") as fout, open(stderr_path, "w", encoding="utf-8") as ferr:
    proc = subprocess.Popen(cmd, stdout=fout, stderr=ferr, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
```

## Terminal Interference

- VS Code shared terminals can send unexpected `SIGINT` to long-running helpers. Ignore SIGINT in the runner or launch with `Start-Process -Wait`.
- Prefer JSON status artifacts over terminal text for completion decisions.

```python
result = json.loads(Path(output_json).read_text(encoding="utf-8"))
if result.get("final_status") != "passed":
    raise RuntimeError(f"runner failed: {result.get('final_status')}")
```

## Cleanup

- CDP helpers often spawn Node/browser child trees. `proc.kill()` may leave grandchildren.
- Use tree kill only for the owned helper PID: `taskkill /F /T /PID <pid>`.
- For helpers that use a per-CDP lock file, treat a stuck lock as evidence, not as an automatic retry signal. Check whether the recorded PID still exists and whether it matches the current helper command. Delete only stale locks whose owner process is gone; if duplicate helpers are alive on the same CDP endpoint, stop the duplicate owned helper before retrying.
- If the terminal exits ambiguously but the JSON artifact shows the intended final state, use a fresh read-only verification pass before rerunning the mutating step. Avoid replaying upload/publish just because stdout or exit reporting was incomplete.
