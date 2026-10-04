# Testing VS Code Extensions

Integration tests run in an Extension Development Host. Follow the official [Testing Extensions](https://code.visualstudio.com/api/working-with-extensions/testing-extension) guide for boilerplate; this file keeps the project rules and gotchas.

## Setup

- Default: the test CLI. `npm install -D @vscode/test-cli @vscode/test-electron`, set `"test": "vscode-test"`, and configure `.vscode-test.mjs` (Mocha under the hood; `--label` selects one configuration).
- Use a custom `runTests` runner from `@vscode/test-electron` only for custom setup (installing a VSIX first, patching a downloaded archive, multiple launch variants).
- Running tests from the CLI fails if the same VS Code build is already running; run them against a different build/channel or from the debug launch configuration.
- If `capabilities.untrustedWorkspaces` is declared, run separate trusted/untrusted configurations (trust cannot be toggled from a test); give the untrusted run its own `--user-data-dir`.

## Engine Floor

Treat `engines.vscode` as the supported API/runtime floor, not the developer's
installed version. Pin `@types/vscode` to that floor; derive test-host and
isolated-install versions from the validated manifest range rather than separate
constants. Only strip a caret after validating a simple `^major.minor.patch`
range; use a range parser for other forms. Keep lockfile and compatibility docs
aligned. A host rejecting activation on its engine check does not prove an API
failure: test a proposed lower floor with its types and real Extension Host
before lowering it. Newer versions inside the declared range need no blanket
untested-version warning; report actual failures with a manual, data-free Issue
link instead of uploading diagnostics automatically.

```javascript
// .vscode-test.mjs
import { defineConfig } from "@vscode/test-cli";
import { readFileSync } from "node:fs";

const range = JSON.parse(readFileSync("package.json", "utf8")).engines?.vscode;
if (typeof range !== "string" || !/^\^\d+\.\d+\.\d+$/.test(range)) {
  throw new Error("This config requires a simple caret engine range.");
}

export default defineConfig({
  files: "out/test/**/*.test.js",
  version: range.slice(1),
  mocha: { ui: "tdd", timeout: 20000 },
});
```

In a custom runner, pass the same derived value as `runTests({ version })` and set Mocha `failZero: true` so an empty test glob fails.

## Risk-Based Regression Checks

Typecheck explicitly when `compile` only bundles (for example, esbuild); then run the smallest behavior check and the full suite before release.

Extension Host assertions, command resolution, CI success and package identity do not prove that a downstream service produced a user-visible result. For changes to Chat, LM Tools, authentication, model selection or other external integrations, run the affected workflow before release with the same candidate VSIX in disposable `--user-data-dir` and `--extensions-dir` roots. Use disabled/disposable data, verify readback and persisted state, observe the real downstream result (for example, an exact Chat response marker), and remove the profile afterward. Never install over a normal profile that can contain enabled schedules or user data.

If the isolated account does not expose the target model or capability, report that path as unverified and keep a static guard; do not select a hidden model or treat a nearby model's successful smoke as proof for it.

| Change area                                   | Extra checks                                                                                                                                                                                                                                         |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Commands / settings / views in `package.json` | Verify manifest consistency, command IDs, setting keys, menu `when` clauses, and README setting tables                                                                                                                                               |
| Manifest/runtime localization                 | Treat these as separate systems: compare every manifest `package.nls*.json` key set; verify runtime `bundle.l10n.*.json` covers each `vscode.l10n.t` message with identical placeholder sets; confirm both sets ship in the VSIX                     |
| Runtime logging / diagnostics                 | Verify logs go through an Output Channel logger instead of direct `console.*` calls in extension runtime paths                                                                                                                                       |
| Resource scanners / providers                 | Test with extension-host APIs available and with missing/empty roots; avoid relying on local filesystem guesses; if you scan installed extensions, cover both known `resources/*` roots and manifest-declared `chatAgents` / `chatPromptFiles` paths |
| Selectors / quick actions / saved options     | Hide internal, test, deprecated, stale, or unsupported candidates; preserve newly introduced normal candidates; confirm hidden saved values do not reappear from settings, cache, or fallback paths                                                  |
| Chat / LM Tools / model configuration         | Query the installed tool catalog, create only disabled disposable state, execute one explicit ID, observe the actual response, and confirm selected model/configuration plus disabled-state persistence                                              |
| Installer / updater / index merge logic       | Run focused regression scripts plus a broader smoke test because these paths often cross manifest, filesystem, and network boundaries                                                                                                                |
| Generated marker sections                     | Test duplicate marker handling and confirm the final file contains exactly one generated section pair                                                                                                                                                |
| Worker or secondary module entry points       | Guard that the runtime path (for example `path.join(__dirname, "x.js")`) resolves to a real source file, a compiled output, and an entry in the packaged payload allowlist; packaging can pass while analysis fails only at runtime                  |

Filesystem and realpath behavior can classify the same missing resource differently across developer machines and hosted runners. Assert the user-facing contract first (for example, fallback source/status/payload), and only pin an internal error reason when the test controls the exact failure branch. If multiple reasons are specification-equivalent, use an explicit allowed set instead of one environment-dependent value.

For shared manifest, installer, updater or scanner changes, add a focused regression instead of relying only on manual verification.

## Reliability Gotchas

- Execute actual Webview submit/source-change handlers, not only source-token assertions. Textareas normalize CRLF to LF; normalize comparisons without inferring a provenance change. Keep file-to-inline conversion explicit, disable hidden required fields, and focus validation errors on visible controls.
- Test rejected create/update requests with multiple changed fields and invalid paths, including NUL in cached local/global references. Assert that memory, persisted payload and metadata remain unchanged; read-time path rejection does not prove that invalid input cannot be saved.
- A synchronous storage mock cannot prove queued persistence ordering. Hold the first write with a deferred promise, enqueue the next, and assert it cannot start or read stale state before the first settles. Cover rejected-write recovery, preserved entries and direct versus best-effort error propagation; release and await all pending work before fixture cleanup, without sleeps.
- A UI automation timeout, a missing busy indicator or a disabled Send button is not proof that a mutating LM Tool did not run. Inspect the Chat transcript and persisted readback before retrying; uncertain delivery can otherwise create duplicates.
- For bounded automatic dispatch, test oldest-due selection, reserved daily capacity and slot release on both execution and persistence failures. Keep unclaimed work pending. Name what callback completion proves: a Chat command resolving may confirm dispatch, not completion of the model response; a per-window limiter is not a cross-window guarantee.
- Do not assume `npm test -- --grep <pattern>` reaches Mocha. Parse supported options before editor download/launch, reject unknown arguments and empty/invalid regex, and forward the unchanged pattern through `extensionTestsEnv`. With no CLI filter, explicitly clear the inherited filter so CI runs the full suite. Verify selected-test counts, zero-match exit failure, and unfiltered execution with an impossible ambient filter. If PowerShell drops options through `npm.ps1`, use `npm.cmd`; for shell-sensitive regex, compile first and invoke the Node runner directly.
- Make each direct test entry point compile or clean first. An explicit list such as `node --test out/test/a.test.js` can silently pass against stale `out/` while a newly added source test never runs. Give every public test script a matching npm lifecycle hook (for example, `pretest:unit`) and add a guard that every source `*.test.ts` has a compiled path in the test script, or use deterministic discovery.
- For privacy-sensitive opt-outs around asynchronous file reads, clearing a cache is not enough. Increment a generation on opt-out/disposal, check it after every `await` and before cache/UI writes, close any view showing the disabled data, and use an injected delayed filesystem in tests to prove an in-flight read cannot repopulate state after opt-out.
- For scanners, test pure merging and the actual registered create/change/delete callbacks: prove cache invalidation, in-flight cancellation and displayed-state updates, including another open item. Frequent writes should update one entry; deletion may use a debounced full scan when sibling files share an ID. Before optimizing selected-item refresh, measure filesystem call counts and guard new/deleted files, sibling formats, cold caches and ordinary full refresh. Synthetic call reductions are not wall-clock speedups; state when other items' cached timestamps refresh.
- Test optional builtins through the real lazy loader, not only an injected replacement. Load the compiled module in an isolated VM with controlled `require`; assert zero loads on import, one load across repeated successful or failed reads, safe failure results, and isolation between module instances. Exercise the default read path too. Avoid production reset APIs or changing global module caches for tests; account for cross-realm prototypes in object comparisons.
- Async scans need a generation token and a disposed guard so an older completion cannot overwrite newer state or update UI after deactivation. Route fire-and-forget promises through one rejection handler and assert that watcher/timer entry points use it.
- If behavior depends on `ExtensionContext.storageUri`, run the Extension Host suite both with a folder argument and without one. Empty windows can have different storage roots and otherwise remain an unexecuted branch.
- Size Extension Host fixtures by what the assertion discriminates, not by the production limit. Building a multi-megabyte payload inside the host can trip the `Extension host is unresponsive` watchdog even when the suite still passes; shrink the fixture until it is fast and still exercises the branch.
- On Windows, `@vscode/test-electron` can fail before extension activation while VS Code setup holds the global `vscode-updating` mutex. A downloaded archive is not an Inno Setup installation: use `downloadAndUnzipVSCode`, verify the executable resolves inside the dedicated `.vscode-test` cache, set **only that copy's** `product.json#win32VersionedUpdate` to `false`, re-read it to confirm the value, and pass its `vscodeExecutablePath` to `runTests`. Archive layouts may add a build-hash directory before `resources/app/product.json`; resolve candidate realpaths under the cache root, require exactly one candidate, require a JSON object with a boolean `win32VersionedUpdate`, and never patch the machine installation.

```typescript
for (const folderArgs of [[extensionDevelopmentPath], []]) {
  await runTests({
    extensionDevelopmentPath,
    extensionTestsPath,
    launchArgs: [...folderArgs, "--disable-extensions"],
  });
}
```

Treat the archive patch as test infrastructure with static guards: assert cache containment, the single-candidate product lookup, and both workspace/empty-window launches. The main-process log can still print a harmless instance-mutex warning; completion is decided by extension-host assertions and exit code.

## Terminal Readiness and Owned Cleanup

- Diagnose `terminal.shellIntegration`, its `cwd`, and `terminal.state.shell` separately. Active integration does not guarantee a detected shell type; log only readiness flags and an allowlisted shell label, not commands, output or environment values.
- If shell detection is absent, do not guess from a profile label, switch shells silently or stretch readiness timeouts to pass a gate. A platform-specific fallback needs bounded read-only observation of the owned terminal's actual process, PID validation and fail-closed handling of errors or ambiguous children; it must not kill processes or bypass execution-time authorization checks.
- Use isolated local fixtures to assert real start/output/end events, literal argv/stdin, cancellation and unrelated-process survival. Unit mocks or a blocked outcome do not substitute for successful real-shell gates. Retry only after new evidence or a corrective change.
- Resolve owned Webview tabs from the current `tabGroups` immediately before cleanup rather than retaining stale `Tab` objects across asynchronous UI changes. Limit cleanup to the view opened by the test; never close unrelated user tabs.

## CI Integration

On Linux runners, wrap the test command with `xvfb-run -a` (for example `xvfb-run -a npm test`) because the Extension Host needs a display.
