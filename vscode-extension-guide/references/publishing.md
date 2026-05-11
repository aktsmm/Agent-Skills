# Publishing to Marketplace

Complete guide for publishing your VS Code extension.

## Prerequisites

1. **Publisher account** at [marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage)
2. **Personal Access Token (PAT)** from Azure DevOps
3. **vsce CLI** installed: `npm install -g @vscode/vsce`

## Creating a Publisher

1. Go to [marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage)
2. Sign in with Microsoft account
3. Click "Create publisher"
4. Fill in:
   - **ID**: Unique identifier (used in extension ID)
   - **Name**: Display name
   - **Description**: Optional

## Getting Personal Access Token (PAT)

1. Go to [dev.azure.com](https://dev.azure.com)
2. Sign in → User Settings (top right) → **Personal access tokens**
3. Click **New Token**
4. Configure:
   - **Name**: "VS Code Marketplace" (or any descriptive name)
   - **Organization**: **All accessible organizations** ← Critical!
   - **Expiration**: Up to 1 year
   - **Scopes**: Custom defined → **Marketplace** → ✅ **Manage**
5. Click **Create** and **copy token immediately** (shown only once)

## Login and Publish

```bash
# Login (first time or when token expires)
npx @vscode/vsce login <publisher-id>
# Paste PAT when prompted

# Verify login
npx @vscode/vsce ls-publishers

# Publish new version
npx @vscode/vsce publish

# Publish an already-built VSIX (prevents packaging the wrong artifact)
npx @vscode/vsce publish -i ./my-extension-1.0.0.vsix

# Confirm an already-published version without failing the release script
npx @vscode/vsce publish -i ./my-extension-1.0.0.vsix --skip-duplicate

# Publish with version bump
npx @vscode/vsce publish minor  # 0.1.0 → 0.2.0
npx @vscode/vsce publish patch  # 0.1.0 → 0.1.1
```

> `vsce` option names vary by version. If `--packagePath` is rejected, check the local `vsce publish --help` and prefer the supported package input option such as `-i`. Do not paste help output into public logs if it displays PAT defaults.

## Pre-publish Checklist

| Item                        | Check                               |
| --------------------------- | ----------------------------------- |
| `publisher` in package.json | Matches your publisher ID           |
| `version`                   | Incremented from previous           |
| `README.md`                 | Exists (lowercase!) and has content |
| `LICENSE`                   | Included                            |
| `icon`                      | 128x128 PNG, path in package.json   |
| `.vscodeignore`             | Excludes unnecessary files          |

## package.json Requirements

```json
{
  "name": "my-extension",
  "displayName": "My Extension",
  "description": "Brief description for Marketplace",
  "version": "1.0.0",
  "publisher": "your-publisher-id",
  "icon": "images/icon.png",
  "repository": {
    "type": "git",
    "url": "https://github.com/user/repo"
  },
  "categories": ["Other"],
  "keywords": ["keyword1", "keyword2"]
}
```

## Valid Categories

```
Programming Languages, Snippets, Linters, Themes, Debuggers,
Formatters, Keymaps, SCM Providers, Other, Extension Packs,
Language Packs, Data Science, Machine Learning, Visualization,
Notebooks, Education, Testing, AI, Chat
```

## Version Constraints

- ✅ Valid: `1.0.0`, `1.2.3`, `0.0.1`
- ❌ Invalid: `1.0.0-beta.1`, `1.0.0-rc1` (prerelease tags rejected)
- Use GitHub Releases for beta distribution instead

## Inspect Package Before Publishing

```bash
# List files that will be included
npx @vscode/vsce ls

# Create VSIX without publishing (for inspection)
mkdir -p artifacts/vsix
npx @vscode/vsce package --out artifacts/vsix/my-extension-1.0.0.vsix
```

If the project has a repository-specific release hygiene test, treat that test as the source of truth for payload safety. `vsce ls` flags differ between CLI versions, while a project test can assert the exact entrypoint and excluded files required by that extension.

## Local VSIX Artifact Hygiene

Store generated `.vsix` files under `artifacts/vsix/` rather than the repository root. This keeps the root readable, makes cleanup scriptable, and reduces the chance of attaching or inspecting the wrong local file.

```powershell
New-Item -ItemType Directory -Force artifacts/vsix | Out-Null
npx @vscode/vsce package --out artifacts/vsix/my-extension-1.0.0.vsix
npx @vscode/vsce publish -i ./artifacts/vsix/my-extension-1.0.0.vsix
```

When you keep historical local builds, set a retention rule and prune old archives automatically. Keeping only the latest 10 local VSIX files is usually enough for rollback and spot-checking.

```powershell
$vsixDir = "artifacts/vsix"
Get-ChildItem $vsixDir -Filter "my-extension-*.vsix" |
  Sort-Object { [version]($_.BaseName -replace '^my-extension-', '') } -Descending |
  Select-Object -Skip 10 |
  Remove-Item -Force
```

If the project ships multiple package variants such as a release VSIX and a dev/coexistence VSIX, keep **all** of them under `artifacts/vsix/` except the one release artifact you intentionally attach. Apply the same hygiene checks to every variant so the smaller test build does not silently diverge from the release payload.

## .vscodeignore

Minimize package size:

```ignore
**
!package.json
!README.md
!LICENSE
!CHANGELOG.md
!out/**
!images/icon.png

src/**
test/**
node_modules/**
*.ts
tsconfig*.json
.github/**
.vscode/**
*.vsix
artifacts/**
```

## Updating Published Extensions

```bash
# Increment version and publish
npx @vscode/vsce publish patch

# Or manually update version first
npm version patch
npx @vscode/vsce publish
```

## Unpublishing

```bash
# Unpublish specific version
npx @vscode/vsce unpublish <publisher>.<extension> --version <version>

# Unpublish entire extension (use with caution!)
npx @vscode/vsce unpublish <publisher>.<extension>
```

## Common Errors

| Error                      | Cause                        | Fix                                                   |
| -------------------------- | ---------------------------- | ----------------------------------------------------- |
| `Missing publisher`        | No publisher in package.json | Add `"publisher": "your-id"`                          |
| `Personal Access Token...` | PAT invalid or expired       | Regenerate PAT with correct scopes                    |
| `version already exists`   | Same version published       | Increment version number                              |
| `README not found`         | File missing or wrong case   | Create `README.md` (lowercase)                        |
| `invalid prerelease`       | Version like `1.0.0-beta`    | Use standard version format                           |
| `unknown option`           | Local `vsce` version differs | Check `vsce <command> --help` and use supported flags |

## GitHub Release After Marketplace Publish

When attaching the VSIX to a GitHub Release, pin the release to a full commit SHA if you use `--target`. Short SHAs can be rejected by the GitHub API.

```powershell
$full = git rev-parse HEAD
gh release create v1.0.0 .\artifacts\vsix\my-extension-1.0.0.vsix --target $full --title "v1.0.0 - Release title" --notes-file .\release-notes-v1.0.0.md
```

If you already calculate the VSIX checksum locally, record the **size** and
**SHA256 digest** in the release notes too. GitHub Release asset metadata then
becomes an independent proof of exactly which artifact was published, which is
useful when Marketplace metadata is still stale right after publish.

```powershell
$vsix = ".\artifacts\vsix\my-extension-1.0.0.vsix"
Get-Item $vsix | Select-Object Name, Length
Get-FileHash $vsix -Algorithm SHA256 | Select-Object Hash
```

After publishing, `vsce show` output can lag or sort versions unexpectedly. If you need a deterministic confirmation, run duplicate-safe publish against the exact VSIX and verify that the Marketplace reports the version as already published.

## Marketplace URLs

- **Your extensions**: `https://marketplace.visualstudio.com/manage/publishers/<publisher-id>`
- **Published extension**: `https://marketplace.visualstudio.com/items?itemName=<publisher>.<extension>`
- **Statistics**: Available in manage portal after publish

## PAT Security & Persistence

### Persist VSCE_PAT safely (Windows)

```powershell
# 1. Set for the current terminal session (type directly – never paste into chat!)
$env:VSCE_PAT = "<your-pat>"

# 2. Persist to User environment variables (survives reboots)
[Environment]::SetEnvironmentVariable("VSCE_PAT", $env:VSCE_PAT, "User")

# 3. Verify without revealing the value
if ($env:VSCE_PAT) { "present (length: $($env:VSCE_PAT.Length))" } else { "missing" }
```

> ⚠️ `SetEnvironmentVariable` does **not** update already-open terminals.
> Open a new terminal (or restart VS Code) after persisting.

### If the PAT was accidentally exposed

1. **Revoke immediately** at `dev.azure.com` → User Settings → Personal access tokens → Revoke
2. Generate a new token (same scopes)
3. Update `VSCE_PAT` with the new value

### Rules

- ❌ Never paste a PAT into chat, issue comments, or commit messages
- ❌ Never echo `$env:VSCE_PAT` – check existence/length only
- ❌ Avoid sharing raw `vsce publish --help` output when `VSCE_PAT` is set; some versions display the effective PAT default in help text
- ✅ Use `VSCE_PAT` env var; `vsce publish` picks it up automatically
- ✅ Set expiry ≤ 1 year and rotate on a schedule

## .vscodeignore – Recommended Exclusion Patterns

Keep the published VSIX small and free of dev-only artefacts:

```ignore
# Source & config (already compiled to out/)
src/**
**/tsconfig.json
**/.eslintrc.json
**/*.map
**/*.ts
!out/**

# Dev tooling
.vscode/**
.vscode-test/**
.github/**
node_modules/**

# Dev-only content (never ship to users)
docs/**
output/**
output_sessions/**
research/**
session/**
FULL_SPECIFICATION.md
AGENTS.md

# Secondary docs or local artifacts that are not needed in the VSIX
README_ja.md
artifacts/**

# Large or unnecessary assets
images/demo-animated.gif
*.vsix
```

> **Tip**: Run `npx @vscode/vsce ls` to preview exactly what will be packaged
> before running `vsce package` or `vsce publish`.

### Marketplace auto-resolves relative-path images

When the README references images by relative path (e.g. `![demo](images/demo.gif)`),
the Marketplace web view and the in-VS Code extension details pane both resolve
those paths against `repository.url` in `package.json` and fetch the file from
`raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`. So as long as the
image is committed and pushed to the default branch, you can keep it **out of
the VSIX** to drop multi-megabyte demo media without breaking the listing.

This auto-resolution applies to **images**, not to arbitrary Markdown links. If
you exclude secondary documents such as `README_ja.md` from the VSIX, link to
them with an absolute GitHub URL from the primary `README.md` instead of a
relative Markdown link.

A single 15 MB demo GIF can shrink a VSIX from ~15 MB to ~175 KB (≈99% reduction)
with no visible difference in Marketplace rendering.

### Verify VSIX integrity before publish

`vsce ls` validates `.vscodeignore` filtering, but it cannot detect a truncated
or zip-corrupt VSIX (which can happen when the package step is interrupted by
build watchers or transient I/O). Always do a local install round-trip before
`vsce publish`:

```powershell
$cli = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd"
& $cli --install-extension artifacts\vsix\my-extension-1.0.0.vsix --force
# If you see:
#   Error: End of central directory record signature not found.
# the VSIX is truncated; rebuild it with `vsce package` and re-test.
```

Also treat `vsce package` completion based on the **output file** (size +
mtime), not on console messages — terminal capture sometimes drops the
`DONE Packaged: ...` line, but the artifact on disk is the source of truth.

```powershell
Get-ChildItem artifacts/vsix/my-extension-1.0.0.vsix |
  Select-Object Length, LastWriteTime
```

If the extension manifest references icons such as `icon.png` for the Marketplace
tile and `icon.svg` for activity bar or command UI, add a release check that
asserts the referenced files physically exist before packaging.

## Post-publish Verification

`vsce show --json` is useful, but its metadata can lag right after publish.
Treat the publish command's result as the first source of truth and use at least
one more independent check.

- Run duplicate-safe publish against the exact VSIX and confirm `already published`
- If you use Git tags or GitHub Releases, verify the release/tag exists too
- If the Marketplace listing lags, do not republish a new version just because
  `vsce show` still returns the previous metadata snapshot
