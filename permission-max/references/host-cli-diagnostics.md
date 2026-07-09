# Copilot CLI and Host Diagnostics

Use this reference when Scout settings are already correct but `Read`, `Write`, `Edit`, or `PowerShell command` confirmations still appear.

## Read-Only Discovery

```powershell
$candidates = @(
  "$env:USERPROFILE\.copilot",
  "$env:APPDATA\GitHub Copilot",
  "$env:APPDATA\Code\User",
  "$env:LOCALAPPDATA\GitHub Copilot"
)
foreach ($path in $candidates) {
  if (Test-Path -LiteralPath $path) {
    Get-ChildItem -LiteralPath $path -Force -Recurse -Include '*permission*','*settings*.json','*.toml','*.yaml','*.yml' |
      Select-Object FullName,Length,LastWriteTime
  }
}
```

Also inspect the installed CLI help instead of assuming flags:

```powershell
copilot --help
copilot -p "help" --help
```

Only edit a discovered approval, confirmation, workspace trust, or tool allow-list setting after explaining the scope to the user. If the host manages the guard and exposes no setting, report that limitation instead of claiming completion.

For a separately launched `copilot -p` subprocess, supported versions may accept:

```powershell
copilot -p "<prompt>" `
  --allow-all-tools `
  --allow-all-urls `
  --silent
```

These flags apply to that subprocess. They do not necessarily change Scout or the current host session.

## Limitation Report

```text
Scout permissions were verified separately.
The remaining confirmation belongs to the Copilot CLI or host guard, and no supported setting was found to disable it globally.
Subprocess allow flags may reduce prompts for a separately launched command, but they do not alter this session's host controls.
```
