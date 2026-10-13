# Pre-check

- Confirm the workspace contract before build: `.config/config.json`, `.config/`, `scripts/`, `template/`, and `{date}/manifest/`.
- For a new customer or redesigned deck, confirm the template has passed human design review and template-contract review before any content build.
- Run `scripts/Test-AzureUpdateWorkspace.ps1` before build or re-apply; confirm the selected build entry, interpreter, and current manifest schema are usable. A missing or incompatible entry blocks execution; do not label it running.
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

## Resume Evidence

- Distinguish planned, delegated, running, blocked, and verified. Record target, entry, start/update times, progress, owned process identity, deadline, and actual exit code in run-local logs. Emit progress while executing; enforce a deadline on the owned process tree, never a shared runner or all Office processes.
- After interruption or a progress inquiry, reconcile current artifact hashes/timestamps, logs, and owned processes. Process survival or CPU activity alone does not prove healthy progress; absent launch evidence, report unstarted rather than waiting indefinitely.
- Resume only the missing phase from the last passing gate on current inputs. Preserve completed outputs; do not start an unscoped shared runner or stop another run's processes.

## Dependency And Smoke Check

- Before the meeting, install locked local dependencies and exercise the selected engine, template, fonts, renderer, and direct PDF parser. Do not depend on editor-extension internals, implicit default templates, or on-the-day installs; stop on missing components rather than repeat failed download paths.
- Use the production rendering functions to build a small temporary deck covering long titles, dense body text, conditional regions, comparisons, and tables. Verify saved OpenXML, measured bounds/fonts, PDF export, nonblank images, and page-local text. Preserve approved inputs and delivery artifacts; dependency presence alone is not a smoke PASS.
- Keep smoke on the normal build path and test valid and rejected controls: missing text/images, stale hashes, dependency mismatch, hidden-slide policy, and timeout. Record exactly which path passed; smoke does not replace full delivery QA or human review.

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
