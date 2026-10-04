# Pre-check

- Confirm the workspace contract before build: `.config/config.json`, `.config/`, `scripts/`, `template/`, and `{date}/manifest/`.
- For a new customer or redesigned deck, confirm the template has passed human design review and template-contract review before any content build.
- Run `scripts/Test-AzureUpdateWorkspace.ps1` before build or re-apply.
- Missing `{date}/logs/` is a warning, not a bootstrap failure; scripts may create or use logs as needed.
- Do not overwrite customer config during bootstrap unless explicitly requested.
- PowerPoint automation should open/close only the target presentation; do not kill all PowerPoint processes except as a last resort.
- If a deck exists and manifest JSON changed, prefer `Run-CustomerPptxPipeline.ps1 -SkipBuild`.

## Workspace Contract

Moved from SKILL.md "Execution Model". A usable workspace must have:

- `.config/config.json`
- `.config/customer-keywords.json`, `.config/customer-profile.md`, `.config/exclude-keywords.json`
- `scripts/*.ps1` and `scripts/PptxCommon.psm1`
- Python engine only: `scripts/python/build_customer_pptx.py`, dependency lock, template contract, and render style
- `template/*.pptx`
- `{MMDD}/manifest/` and `{MMDD}/logs/`

## Bootstrap Options

Moved from SKILL.md "Bootstrap".

If you also want a ready-to-use VS Code workspace MCP config, add `-CopyMcpSample`. This writes `.vscode/mcp.json` with the Microsoft Learn Docs and MRC remote MCP endpoints unless the file already exists.

Rules: keep existing customer config by default, write starter conflicts as `.new`, use `-UpdateScripts` for runtime script refresh, and use `-ForceConfig` only for intentional config replacement.

## Fast Re-apply

Moved from SKILL.md "Standard Run". Fast re-apply after manifest-only changes:

```powershell
& ".\scripts\Run-CustomerPptxPipeline.ps1" -DateFolder ".\0704" -SkipBuild
```

## Preflight Command

Moved from SKILL.md "Validation". Run preflight before build/re-apply:

```powershell
& ".\scripts\Test-AzureUpdateWorkspace.ps1" -TargetRoot "." -DateFolder ".\0704"
```
