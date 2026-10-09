# Publishing to Marketplace

Publisher creation, `vsce` basics and the manifest fields follow the official [Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) guide. This file keeps release gates and verified gotchas.

## Authentication

- The CLI package is `@vscode/vsce` (`npx --yes @vscode/vsce ...`); do not use the old unscoped `vsce` package.
- Global Azure DevOps PATs (organization = **All accessible organizations**, which Marketplace publishing has required) are retired on **2026-12-01**. Re-check the official page before relying on the PAT steps below after that date.
- For automated publishing, prefer Microsoft Entra ID with a managed identity / workload identity federation: add the identity to the publisher (Contributor) and run `vsce publish --azure-credential` (vsce >= 2.26.1).
- PAT settings when still used: **All accessible organizations**; **Scopes** → Show all scopes → **Marketplace > Manage** (`Publish` alone may be rejected by some publish API paths even when `verify-pat` succeeds); a 401/403 on publish is usually a single-organization token or a wrong scope.
- **Expiration**: Pick a real future date such as `1 year`. The `Custom defined` field defaults to today's date in some Azure DevOps UIs, so a token issued without changing it is valid only for the current day — `vsce verify-pat` passes the same day, but `vsce publish` fails with `Access Denied: The Personal Access Token used has expired.` the moment the day rolls over.

Before publishing, verify the token against the manifest's publisher from the same terminal session that will run `vsce`:

```powershell
npx --yes @vscode/vsce verify-pat <publisher-id> -p "$env:VSCE_PAT"
```

If `verify-pat` fails but `VSCE_PAT` exists in the User environment, reload it into the current process before retrying:

```powershell
$env:VSCE_PAT = [System.Environment]::GetEnvironmentVariable("VSCE_PAT", "User")
npx --yes @vscode/vsce verify-pat <publisher-id> -p "$env:VSCE_PAT"
```

Publisher authorization failure is not proof that the token expired. Verify permissions for the intended publisher; switching to another authorized publisher changes the extension ID and requires approval. Then synchronize manifest, activation-test IDs and listing links.

For GitHub workflow authorization failures, recheck the current CLI identity as
well as permissions; another session can change the shared keyring's active
account. Use the intended account's credential only in the owning operation and
restore its prior environment afterward. Do not switch shared accounts or expose
tokens merely to recover a release.

In CI, a nonempty secret is not proof of a valid PAT. Verify publisher authorization using the job's secret without printing it. Local Process/User environment values and repository/environment secrets are separate stores: a local refresh does not repair CI. A `publish=false` build validates no credentials unless it explicitly runs that read-only check. On authentication failure, retain the artifact and commit/tag identity; report publication and downstream GitHub Release as blocked and request owner-side secret repair, never the token in chat.

## Login and Publish

```bash
# Login (first time or when token expires)
npx @vscode/vsce login <publisher-id>

# Verify the PAT used by this terminal before publish
npx --yes @vscode/vsce verify-pat <publisher-id> -p "$env:VSCE_PAT"

# Publish an already-built VSIX (prevents packaging the wrong artifact)
npx @vscode/vsce publish -i ./my-extension-1.0.0.vsix

# Resume an explicitly requested publish idempotently, not as a read-only check
npx @vscode/vsce publish -i ./my-extension-1.0.0.vsix --skip-duplicate

# Pre-release channel (same flag for package)
npx @vscode/vsce publish --pre-release
```

> `vsce` option names vary by version. For an existing VSIX, prefer the documented `-i` input option. If syntax must be checked, run help only in a process without `VSCE_PAT`; the help output itself can disclose the effective token, including to private tool logs.

- `vsce publish patch|minor|major|<x.y.z>` edits `package.json` and, inside a git repo, also creates a version commit **and tag** via `npm version`. Do not use it when the repository's release flow owns tagging; bump the version yourself and publish the verified VSIX.
- Versions must be plain `major.minor.patch`; semver pre-release tags (`1.0.0-beta.1`) are rejected. Use `--pre-release` with a distinct version (convention: odd minor for pre-release, even minor for release) and `engines.vscode >= 1.63.0`.
- Manifest/listing basics: `publisher` matches the publisher ID, `README.md` / `LICENSE` / `CHANGELOG.md` at the root, `icon` is a PNG of at least 128x128 (SVG icons and non-trusted SVG badges/images are rejected), README/CHANGELOG image URLs resolve to `https`, at most 30 `keywords`. See the official manifest reference for valid `categories`.

## Inspect Package Before Publishing

```bash
# List files that will be included
npx @vscode/vsce ls

# Create VSIX without publishing (for inspection)
mkdir -p artifacts/vsix
npx @vscode/vsce package --out artifacts/vsix/my-extension-1.0.0.vsix
```

Use the repository's release hygiene test for payload safety. Besides checking
paths, compare packaged runtime, Webview JS/CSS, locales and icons with the same
release build. Compare runtime manifest fields structurally, including publisher,
version, engines, entry point, localization, contributions and opt-ins. Negative
tests must reject same-name stale assets and wrong engine requirements; file
lists alone prove neither content identity nor installability.

On a byte mismatch, report paths without dumping payloads. Normalize line endings
only to diagnose formatter/checkout differences, never to waive the release gate.
Build a clean checkout of the CI commit with the same locked toolchain and rerun
strict comparison. If it passes, keep the original verified CI artifact; otherwise
resolve the content drift before publication. Remove only the temporary checkout
you created, preserving the user's working tree.

If a release test asserts the extension version inside docs or spec files (README, CHANGELOG, a `FULL_SPECIFICATION`-style file), bump **every** one of them together with `package.json`. A single doc lagging the package version fails the release gate even when the build itself is correct, so update the version in all asserted files before tagging.

### Local Preview Packages

An unpublished local VSIX often has no repository URL or license file yet. If its README uses relative links (for example, a language switch or local image), `vsce` can reject packaging because it cannot rewrite those links. For a local-only preview:

```powershell
New-Item -ItemType Directory -Force artifacts/vsix | Out-Null
npx --yes @vscode/vsce package `
  --allow-missing-repository `
  --skip-license `
  --no-rewrite-relative-links `
  --out artifacts/vsix/my-extension-0.0.1.vsix
```

Use the exact options reported by the pinned `vsce package --help`; do not guess similar names. `--no-rewrite-relative-links` is safe only when every relative target is included in the VSIX. Inspect the archive and verify the README language target and each relative image exist at those exact paths; an image excluded by `.vscodeignore` cannot fall back to GitHub in a local preview.

Do not add Marketplace/version/install badges that imply publication before the extension exists there. Local previews can use factual static badges such as `Local Preview`, the declared minimum VS Code version, local-only privacy, and available languages. Once published, replace these with real Marketplace and repository links.

## Packaging Runner Gotchas

- If packaging rejects versions that already have a release tag, keep its tests independent of the repository's current release state. Test the untagged-success path in a temporary Git work tree, and test tagged-version rejection separately. A test that expects the manifest's current version to be untagged passes before release and fails immediately after the tag is created.
- Create the parent directory passed to `--out` before invoking `vsce`; the CLI can enumerate a valid package and still fail at the final write with `ENOENT`.
- On Windows, spawning `npx.cmd` directly from Node can fail with `EINVAL`. In an **npm-managed** project, invoke `process.env.npm_execpath` through `process.execPath` and use `npm exec --package=@vscode/vsce@<version-from-one-project-constant> -- vsce ...`; validate `npm_execpath` exists and is npm's CLI before spawning. For pnpm/yarn projects, use that manager's native exec command instead of forcing npm.
- Treat the VSIX file as the completion source of truth. A quiet or truncated terminal is not success; confirm the artifact exists, has a fresh timestamp, and has a plausible size before moving to publish.
- If `vsce package` appears to hang inside a shared VS Code terminal during `vscode:prepublish`, check for active `node` processes and the expected artifact before retrying. Do not stack repeated `npx vsce package` attempts against the same output path.
- When terminal capture is unreliable, redirect package output to a log file or run the package command as a dedicated VS Code task, then remove any temporary task entries before committing.
- If prepublish already passed separately, still let `vsce package` run its configured prepublish unless the local `vsce package --help` explicitly documents a supported skip flag. Unsupported flags such as guessed `--no-prepublish` are a sign to check local help rather than continue by trial and error.
- Prefer `npx vsce package --out <file>` over ambiguous `npm exec -- vsce package --out <file>` forms. If `vsce` reports `Invalid version <path>`, the package path was parsed as a version argument; switch runner syntax rather than changing the version.
- Run `git status --short` after packaging and `vsce ls`, not only before committing. Repository prepublish scripts can regenerate tracked metadata or JSON formatting; if that happens after the release commit/tag, either commit the mutation before packaging or restore and rebuild the VSIX so the artifact matches the tagged commit.
- Use `gh run watch` only to wait, with temporary log capture when needed. Before publication, require the Actions API to report `completed`/`success`, the expected commit SHA and successful mandatory audit/test/package steps; quiet output or a watcher exit alone is not proof. If local audits are unavailable, push the candidate commit and run authorized validation-only CI before creating a publication-triggering tag. Tag only the validated SHA and separately verify publication and public package identity.
- After dependency changes, require a nonempty lockfile with public `resolved` URLs and integrity, then prove clean `npm ci` and full audit pass. On managed devices that block direct public registries, use the approved quarantine proxy; never force a blocked `--registry` or weaken TLS. If a trusted mirror writes its own host into `resolved`, change only that URL while preserving version and integrity, then test the published lockfile through the proxy. If this cannot be verified locally, use an authorized hosted CI workflow to generate and verify the lockfile; obtain approval if repository policy excludes workflows. Tag and publish only the validated commit and VSIX, without bypassing the quarantine.
- Failed `npm ci` can leave local dependencies incomplete. If offline restore lacks a locked tarball, export that exact public-registry tarball from the verified CI run separately from the VSIX, match its bytes to the lockfile integrity, then use `npm cache add <tarball> --offline` and `npm ci --offline` with the approved registry configuration. Verify local compilation and remove recovery copies. For artifacts under dot-directories, set `include-hidden-files: true` only with a narrowly allowlisted upload path and `if-no-files-found: error`; never enable broad hidden-directory uploads that could expose credentials.
- Prefer an exact archive allowlist for small extensions, not only forbidden-pattern checks, and run it automatically after every package. Verify `extension/package.json`, compiled entry points, locale bundles, icon, license, and every linked README are present while `src/`, tests, sourcemaps, debug logs, private storage snapshots, and generator scripts are absent. Account for `vsce` normalizing `README.md` to `readme.md` and extension `LICENSE` to `LICENSE.txt`; pin the observed archive names.

```javascript
const expected = new Set([
  "extension/package.json",
  "extension/out/extension.js",
]);
const actual = new Set(zipEntries);
const missing = [...expected].filter((name) => !actual.has(name));
const unexpected = [...actual].filter((name) => !expected.has(name));
if (missing.length || unexpected.length) {
  throw new Error(
    `VSIX payload mismatch: missing=${missing}; unexpected=${unexpected}`,
  );
}
```

Build the full expected set from the extension's actual runtime contract (manifest-derived entrypoint plus intentionally packaged assets); do not weaken the comparison to a size check or forbidden glob alone.

## Isolated Install Gate

Do not treat a development-host launch as proof that the VSIX installs. After exact payload verification, install the **same artifact** into an isolated test profile and list extensions with versions:

```typescript
await runVSCodeCommand(["--install-extension", vsix, "--force"], {
  version: minimumVscodeVersion,
  cachePath: testCache,
  reuseMachineInstall: false,
});
const { stdout } = await runVSCodeCommand(
  ["--list-extensions", "--show-versions"],
  {
    version: minimumVscodeVersion,
    cachePath: testCache,
    reuseMachineInstall: false,
  },
);
```

Require the exact lowercase `<publisher>.<name>@<version>` line. A strong local release gate is: dependency audit → unit/Extension Host tests → package → exact ZIP verification → isolated install → behavior-scoped live smoke for changed external integrations. The live smoke must use that same VSIX in disposable user-data/extensions roots and observe the real result; a resolved command or dispatch status is insufficient when the contract requires a downstream response. Derive the VSIX filename from manifest name/version so version bumps cannot leave scripts or docs pointing to a stale artifact.

`runVSCodeCommand` adds isolated `--user-data-dir` and `--extensions-dir` arguments when `reuseMachineInstall` is `false` (the default). Resolve `cachePath` from a repository-owned disposable test root, not user input. If you bypass that helper and invoke the CLI yourself, provide both directories explicitly under that root before using `--install-extension`.

## Post-publish Verification

- Apply the **Release Completion Contract** below; use read-only checks, never another publish command to prove existence.
- If an artifact audit is required, use `https://marketplace.visualstudio.com/_apis/public/gallery/publishers/<publisher>/vsextensions/<extension>/<version>/vspackage`. A `405` from `HEAD` is inconclusive; download via `GET` directly to a temporary file and inspect the actual ZIP.
- When exact public-byte provenance is an agreed gate, compare the version-specific Marketplace GET with the same GitHub Release asset: HTTP success, nonempty size and SHA256 must match. Compare a separately rebuilt local ZIP by runtime bytes and structural manifest, not its archive hash; ZIP timestamps can differ. Retain the verified public package as the canonical artifact and use those same bytes for isolated install. Otherwise do not add optional downloads as new completion gates.
- If a pushed release tag fails CI before publication, keep the failed tag as provenance. Fix the issue, bump to a new patch version, synchronize package/lock/changelog/spec files, and publish a new tag; do not move or reuse the pushed tag.

## Local VSIX Artifact Hygiene

Store generated `.vsix` files under `artifacts/vsix/` (see SKILL.md) and prune old local builds automatically; keeping the latest 10 is usually enough for rollback and spot-checking.

```powershell
$vsixDir = "artifacts/vsix"
Get-ChildItem $vsixDir -Filter "my-extension-*.vsix" |
  Sort-Object { [version]($_.BaseName -replace '^my-extension-', '') } -Descending |
  Select-Object -Skip 10 |
  Remove-Item -Force
```

If the project ships multiple package variants such as a release VSIX and a dev/coexistence VSIX, keep **all** of them under `artifacts/vsix/` except the one release artifact you intentionally attach. Apply the same hygiene checks to every variant so the smaller test build does not silently diverge from the release payload.

## Unpublishing and Removal

These are external, hard-to-reverse operations: get explicit user approval first.

- Marketplace portal **Unpublish** hides the extension but keeps statistics.
- `vsce unpublish <publisher>.<extension>` and portal **Remove** delete the extension and its statistics irreversibly; the extension name is permanently reserved and cannot be reused.
- A specific version can be deleted only from the portal (Reports → Manage → Delete this version). The latest version cannot be deleted, and a deleted version number cannot be reused.

## Common Errors

| Error                                   | Cause                                                                                                                                                                                                                                                        | Fix                                                                                                                                                                        |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `401` / `403` on publish                | PAT bound to one organization instead of All accessible organizations, or scope is not `Marketplace (Manage)`                                                                                                                                                | Reissue the PAT with the correct organization and scope, or move to Entra ID publishing                                                                                    |
| `Access Denied... PAT used has expired` | The current `VSCE_PAT` value is expired, the open terminal still has an old value, the PAT was issued with `Custom defined` expiration defaulting to today, or the PAT lacks `Marketplace > Manage` scope (so `verify-pat` passes but `publish` is rejected) | Regenerate the PAT with a real future expiration and `Marketplace > Manage` scope, update `VSCE_PAT`, reload the current process, and run `vsce verify-pat` before publish |
| `version already exists`                | Same version published (or a deleted version number)                                                                                                                                                                                                         | Increment version number                                                                                                                                                   |
| `invalid prerelease`                    | Version like `1.0.0-beta`                                                                                                                                                                                                                                    | Use `major.minor.patch` plus `--pre-release`                                                                                                                               |
| `unknown option`                        | Local `vsce` version differs                                                                                                                                                                                                                                 | Check `vsce <command> --help` (without `VSCE_PAT` in the process) and use supported flags                                                                                  |

## Release Completion Contract

When the user explicitly asks to release a VS Code extension, do not stop at a
version bump, commit, or push. Treat the release as incomplete until all of these
are done or explicitly blocked:

1. Package the VSIX under `artifacts/vsix/`.
2. Inspect the VSIX contents or run the repo-specific package integrity test.
3. Run the **Isolated Install Gate** above against the generated VSIX; do not modify the normal user profile.
4. Follow the repository's single publication route. For tag-triggered CI, first validate the candidate commit with an explicit non-publishing branch run, then push its matching tag and let CI publish and attach the same VSIX. Do not publish locally first and make CI collide with an existing version.
5. For manual publication, publish the verified VSIX, push the matching tag and attach that VSIX to the GitHub Release; ensure the tag does not independently trigger a second publish.
6. Keep manual workflow dispatch non-publishing by default and serialize runs capable of publishing the same package, including branch and tag routes. Check both the dispatch input and ref: a tag condition can override `publish=false`. Never move a published tag; follow the repository's version/retry policy after failure.
7. Confirm the item page is accessible and public availability identifies the
   intended publisher, extension and version. Use gallery metadata or inspect a
   version-specific Marketplace VSIX when latest metadata is stale; HTTP 200
   alone is insufficient. Verify the actual package's manifest/runtime and
   isolated install, retaining any agreed asset size/SHA256 equality gate.
   Confirm the GitHub Release asset, tag's release commit and synchronized branch.

Separate submission, version-specific public availability and latest-page/catalog
propagation. A verified package can be public while latest still shows an older
version. If public bytes are unavailable, use read-only publishing status to
distinguish pending validation from rejection. Bound watching and retries; if
metadata stays unchanged, record that display gap and its read-only resume
condition. Never republish, retag or bump a version merely to check visibility.

Once these checks and the pre-agreed quality gates pass, report publication
complete with any remaining display gap named separately, then stop. Extra
screenshots, repeated page loads and hashes beyond the agreed package gates are
follow-up audits, not reasons to reopen publication.

Report linked Issue follow-up separately from publication. Read existing
comments before an authorized release reply, link the published version and
state verified behavior versus guarded gaps; close only covered acceptance
criteria. Release authority is not blanket Issue-posting/closure authority,
and an unrelated unfinished integration stays open.
If a repository explicitly required exact artifact equality before publication,
retain that gate; do not invent or relax gates mid-run. Update local state and
task status without reopening completed verification.

If a blocker appears after the version bump, report the state separately:
`Version`, `VSIX`, `Marketplace publish`, `Git tag`, and `GitHub Release`.

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

Verify the GitHub Release and remote tag independently while Marketplace
validation or metadata propagation is pending:

```powershell
gh release view vX.Y.Z --json "tagName,name,url,isDraft,isPrerelease,publishedAt"
git ls-remote --tags origin vX.Y.Z
```

Record submission and public availability separately until the Release Completion
Contract passes; do not use duplicate-safe publish as a verification command.

## Marketplace URLs

- **Your extensions**: `https://marketplace.visualstudio.com/manage/publishers/<publisher-id>`
- **Published extension**: `https://marketplace.visualstudio.com/items?itemName=<publisher>.<extension>`

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

> ⚠️ `SetEnvironmentVariable` does **not** update already-open terminals or VS Code child processes; reload the value as shown in [Authentication](#authentication).

If you control the repository workflow, a small wrapper script can validate the Process `VSCE_PAT`, fall back to the User value when VS Code still holds a stale one, and then forward `verify-pat` / `show` / `publish`.

### If the PAT was accidentally exposed

1. **Revoke immediately** at `dev.azure.com` → User Settings → Personal access tokens → Revoke
2. Generate a new token (same scopes)
3. Update `VSCE_PAT` with the new value

### Rules

- ❌ Never paste a PAT into chat, issue comments, or commit messages
- ❌ Never echo `$env:VSCE_PAT` – check existence/length only
- ❌ Never run `vsce publish --help` with `VSCE_PAT` set; some versions print the effective PAT default even into private tool logs
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
.playwright-mcp/**
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

# Local artifacts (exclude secondary docs only if no shipped link needs them)
artifacts/**

# Large or unnecessary assets
images/demo-animated.gif
*.vsix
```

> **Tip**: Run `npx @vscode/vsce ls` to preview exactly what will be packaged
> before running `vsce package` or `vsce publish`. Packages listed only in
> `devDependencies` are excluded automatically.

> **Gotcha**: `vsce ls --packagePath foo.vsix` does not enumerate entries; for
> packaged VSIX verification (e.g. confirming `node_modules/**` is excluded),
> open the VSIX as a ZIP and list every entry instead:
>
> ```powershell
> Add-Type -AssemblyName System.IO.Compression.FileSystem
> $zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path foo.vsix))
> $zip.Entries | Select-Object FullName, Length
> ```

### Judging `node_modules/**` exclusion

Before excluding `node_modules/**`, confirm `out/*.js` only requires `vscode`
and Node built-ins, with no live external imports:

```powershell
Select-String -Path out\*.js -Pattern 'require\("([^.][^"]+)"\)' -AllMatches
Select-String -Path out\*.js -Pattern 'import\("[^.]'  # dynamic imports
```

A `dependencies` entry that is only reached through a guarded dynamic `import(...)`
disabled in the extension host (e.g. a CLI-side SDK that exits early when
`vscode` is present) ships its entire transitive tree as dead weight. One real
case: `@github/copilot-sdk` → `@github/copilot` ≈ 285 MB → packaged VSIX 181 MB.
After moving the unused dep out and excluding `node_modules/**`, the same VSIX
dropped to ~45 KB (≈4000× smaller). Compare VSIX size against the previous
release; an unchanged-huge size usually means `.vscodeignore` is not actually
excluding `node_modules/**`.

### Marketplace auto-resolves relative-path images

When the README references images by relative path (e.g. `![demo](images/demo.gif)`)
and `repository` points to a public GitHub repository, `vsce` rewrites those paths
to `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` at package time
(`main` by default; override with `--githubBranch` or `--baseImagesUrl`). So as long
as the image is pushed to that branch, you can keep it **out of the VSIX** to drop
multi-megabyte demo media without breaking the listing.

Relative Markdown links are rewritten the same way (`--baseContentUrl`), so they
only work for readers when the target exists on that public branch. If you exclude
secondary documents such as `README_ja.md` from the VSIX, prefer an explicit
absolute GitHub URL from the primary `README.md` to a publicly readable document.

Marketplace publication does not authorize making a private source repository
public. Private raw GitHub image URLs will not serve anonymous readers: use
public distribution assets, keep required icons in the VSIX, and provide alternate
language content on the listing or a publicly reachable page. Verify support access
as an intended user, not only as the maintainer. A private issue tracker is not a
public support channel: use an approved accessible alternative or clearly disclose
restricted access in the feedback UI and listing. Keep `bugs.url`, UI actions and
README destinations aligned; neither a VSIX link nor a support need authorizes a
repository visibility change.

An unchanged documentation icon may pin an earlier published asset version.
Validate its publisher, extension, asset type and expected image rather than
requiring the URL version to equal a not-yet-published package version. The new
VSIX must still contain its own declared runtime and Activity Bar icons.

### Verify VSIX integrity before publish

`vsce ls` validates `.vscodeignore` filtering, but it cannot detect a truncated
or zip-corrupt VSIX (which can happen when the package step is interrupted by
build watchers or transient I/O). Run the exact ZIP verifier and the **Isolated
Install Gate** above before `vsce publish`; never install release-test artifacts
into the normal user profile. A ZIP parser error such as `End of central directory
record signature not found` means the artifact is truncated and must be rebuilt.

Also treat `vsce package` completion based on the **output file** (size +
mtime), not on console messages — terminal capture sometimes drops the
`DONE Packaged: ...` line, but the artifact on disk is the source of truth.
If the VSIX exists but ZIP inspection fails, check whether `node` / `vsce` is
still writing the file. Once no package process remains, delete the corrupt
artifact, rebuild with a deterministic output path, and inspect that rebuilt
file instead of reusing the partial archive.

```powershell
Get-ChildItem artifacts/vsix/my-extension-1.0.0.vsix |
  Select-Object Length, LastWriteTime
```

If the extension manifest references icons such as `icon.png` for the Marketplace
tile and `icon.svg` for activity bar or command UI, add a release check that
asserts the referenced files physically exist before packaging.

## Marketplace Propagation Notes

- `vsce show --json` and the human listing can lag; do not republish solely from stale metadata.
- Gallery "latest" resolution lags too, so `code --install-extension <publisher>.<name> --force` right after publish can silently install the previous version. While propagation is pending, do not install or verify by extension ID: install the identical verified local VSIX (or one downloaded from the version-specific endpoint) with `code --install-extension <path> --force`, confirm with `code --list-extensions --show-versions`, and do not republish.
- Follow the Release Completion Contract; after the public page and exact API identity/version are confirmed, stop waiting unless a pre-agreed artifact gate is still unmet.
- If publish is paused by review, auth, duplicate, or permissions, report version, artifact checksum, commit, tag, push, and publish state separately so the same VSIX can be resumed without guessing.
