# Pre-check

- Confirm the workspace contract before build: `.config/config.json`, `.config/`, `scripts/`, `template/`, and `{date}/manifest/`.
- Run `scripts/Test-AzureUpdateWorkspace.ps1` before build or re-apply.
- Missing `{date}/logs/` is a warning, not a bootstrap failure; scripts may create or use logs as needed.
- Do not overwrite customer config during bootstrap unless explicitly requested.
- PowerPoint automation should open/close only the target presentation; do not kill all PowerPoint processes except as a last resort.
- If a deck exists and manifest JSON changed, prefer `Run-CustomerPptxPipeline.ps1 -SkipBuild`.

