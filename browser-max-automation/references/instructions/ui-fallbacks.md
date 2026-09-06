# UI Fallbacks and Fast Paths

Use these patterns after establishing the page model on an owned work tab. The Skill's foreground, ownership, and shared recovery limits apply to every fallback; this is not a ladder to exhaust after two failures.

## Repeatable Workflows and Playwright CLI

Look for an existing project/skill script before exploring the UI again. On the second occurrence of a stable multi-step flow, parameterize and reuse it when repetition outweighs maintenance. If bulk work is known upfront, validate one item and script the remainder during the first run; a trivial one-off click does not need a new script.

### Choosing the execution route

- MCP is useful for discovering unknown controls. Once a route works, retain it; a CLI invocation per click still leaves the agent doing per-click reasoning. A saved sequence is the reusable unit.
- Playwright CLI is a candidate, not a required installation or universal replacement. Check the installed version and `--help` before depending on commands. Its default new-browser mode is headless: use `open ... --headed` unless the user explicitly requests headless.
- Where supported, `attach --cdp=<verified-endpoint>` can reuse an authenticated headed browser; verify the profile and work target rather than assuming attachment selects the correct tab. Bind a run-owned named session, and do not use `close-all` or `kill-all` on shared sessions.
- `run-code --filename=<script>` can execute a saved Playwright sequence. Use stable locators and validated parameters, not stale snapshot refs or generated source containing untrusted input. `detach` is for an attached session and should leave the external browser running; verify actual version behavior before handoff. Neither CLI nor headed mode guarantees non-activation.
- Prefer supported API helpers for data operations, but retain UI actions and visible checkpoints for UI verification or demos. API execution without a browser is not permission to launch a headless browser or export credentials indiscriminately.

CLI reference: https://github.com/microsoft/playwright-cli

### Reusable sequence contract

- Accept endpoint/session, target/resource identity, input data, and bounded batch size as parameters. Default mutating helpers to read-only/dry-run; require an explicit apply option within the authorized task scope.
- Validate ownership and preconditions, resolve the current item, act once, wait for its postcondition with a deadline, and read back the durable result. Batch independent reads; serialize writes on one target.
- Check for competing user edits at transaction boundaries. If a shared target cannot detect concurrent editing reliably, coordinate a no-edit interval before writes; do not claim an unattended takeover guard exists. Observing the work tab alone is not a reason to destroy or replace it.
- Return completed/failed/unknown item IDs, stage, restart condition, and elapsed time; persist only non-secret task state. Reconcile unknown outcomes before replay and skip verified completed items.
- Keep task-specific scripts with the project and generic helpers with the skill. Record purpose and invocation in the existing workflow reference; search there on later runs. Do not retain auth dumps or customer-specific examples in a portable helper.

### Acceptance scenarios

These are required checks for a new or changed execution route, not claims of completed testing. Use a safe fixture and report unexecuted cases explicitly.

| Scenario                                                                                  | Pass condition                                                                                                                    |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Another app is foreground during tab creation, input, save, upload, capture, and recovery | No automation-induced OS activation or user-tab switch throughout the run; captures are readable                                  |
| The user views the work tab, then edits it                                                | Viewing remains possible; conflicting writes pause or use an explicitly coordinated interval                                      |
| Same workflow runs again                                                                  | Saved sequence is discovered and reused; durable results match and completed items are not duplicated                             |
| Save times out, or the target disappears                                                  | Readback distinguishes success, non-application, and unknown; no ambiguous replay or first-domain-match rebinding                 |
| Background rendering fails or detach is unavailable                                       | At most one bounded recovery; announce a necessary foreground exception or stop, never silently use headless or destructive close |
| Efficiency comparison                                                                     | Compare elapsed time, tool calls, and retries on equivalent input while preserving the same verification; do not invent savings   |

## Hidden File Input Upload

- If `connectOverCDP()` times out but `/json/list` exposes a page WebSocket URL, use raw CDP.
- For editors with hidden `input[type=file]`, target the existing editor tab and use `DOM.setFileInputFiles`.
- Do not navigate an unsaved draft tab to a new URL. Open a separate new tab for a fresh draft if needed.
- Capture existing asset URLs from every active editor surface (textarea, CodeMirror/contenteditable, rendered HTML), call `DOM.setFileInputFiles` once, then require a newly inserted URL. Do not dispatch duplicate `input` / `change` events unless the first upload produced no URL; double dispatch can upload the same file twice.
- If upload creates a persistent temporary draft/entity, return its exact URL or ID as cleanup evidence. Delete only that entity after the downstream article/save is verified; never infer a cleanup target from title or recency alone.
- After deleting that exact entity, reload a clean list/detail view and verify the ID is absent. Dialog dismissal and the pre-delete list DOM are not durable-state evidence because client-side rows can remain stale.

## Native File Chooser (button opens OS picker, no reachable input)

Some flows (e.g. a multi-step "アップロード" wizard) only reveal the `input[type=file]` after a button click that ALSO opens the OS file picker. The native picker blocks the renderer, so any later `Runtime.evaluate` hangs until it is dismissed.

Intercept it instead of letting the OS dialog open:

1. `Page.setInterceptFileChooserDialog({enabled: true})`.
2. Click the button, but **raw-send** the `Input.dispatchMouseEvent` over the WebSocket without consuming responses in an id-matching loop (otherwise the loop swallows the event).
3. Wait for the `Page.fileChooserOpened` CDP event and read its `backendNodeId`.
4. `DOM.setFileInputFiles({backendNodeId, files: [path]})`.
5. `Page.setInterceptFileChooserDialog({enabled: false})`.

For download buttons, set `Browser.setDownloadBehavior({behavior: 'allow', downloadPath: <dir>, eventsEnabled: true})` before clicking so the file lands where you expect instead of the default Downloads folder.

## Shadow-DOM / Material widgets: rect comes back (0,0)

In Angular-Material / web-component UIs (GCP Console, YouTube Studio), many buttons live in shadow DOM and `el.getBoundingClientRect()` returns `{x:0, y:0, width:0}` to page-level JS, so a JS-computed click misses. Click by screenshot pixel coordinates with `Input.dispatchMouseEvent` instead. Also scope element queries to the form region (x/y bounds): a generic `document.querySelector('mat-select,[role=combobox]')` often grabs the page's top search box and opens a search overlay — press Escape to dismiss, then retry within the form area.

## Click times out on "visible, enabled and stable"

Background/minimized rendering can contribute to actionability timeouts, but it is not a universal failure mode. Inspect readiness, overlays, and current target state with a bounded query; successful reads or fills do not prove a click can succeed.

Keep ordinary scoped click/fill as the default. Only choose JS click as the single recovery when its semantics are acceptable and any prior write is known not to have applied. Synthetic events are not equivalent to trusted input. Verify durable state; an ambiguous timeout stops writes rather than triggering another click method or automatic foreground activation.

## Radio and checkbox groups that ignore a click

Prefer a state-setting check/select operation over toggling. If an input or label click is ineffective, inspect the actual control and choose at most one recovery within the shared budget. Read `input.checked` before and after; do not cycle through parent clicks and synthetic event sequences blindly.

A read-back only proves transient UI state. Re-verify after the form's own save and reload before treating the value as submitted.

Never assume a radio group starts empty. A group can arrive with a non-default option pre-selected, so read the whole group's state before deciding whether you need to change anything.

## Element sits outside the real viewport

Canvas-like widgets (org charts, diagram editors, graph views) lay children out around a centred root, so a target can resolve with a valid rect at a NEGATIVE `left` or a `top` past the window height. `Input.dispatchMouseEvent` at those coordinates lands on nothing and returns success, so the click looks like it worked.

- Widening the viewport with `Emulation.setDeviceMetricsOverride` does **not** fix this. Input hit testing still follows the real window, so a coordinate inside the enlarged virtual viewport but outside the window hits nothing.
- Measure first and only scroll when the point is outside the window. Some widgets re-run their own layout and reset the container scroll, so an unconditional `scrollIntoView` can move the target back out of view.
- `scrollIntoView` is not synchronous with layout. Scroll, wait, then re-read `getBoundingClientRect()` in a second evaluation. Reading the rect in the same call returns pre-scroll coordinates and you click the previous element.
- Refuse to click when the re-measured point is still outside the window, instead of dispatching into empty space.

## Handler runs but synthetic clicks are ignored

Do not invoke application handlers or private frontend internals as another retry after click failures. Inspect event/state evidence to distinguish trust or gesture requirements from a stale target, then use a supported route within the existing budget or stop. Never treat handler execution as proof of the user's intended transaction. The Skill's explicitly approved single-incident exception still requires ownership and foreground checks and does not reset the retry budget.

## Hiding sensitive UI before a capture

When a selector suppresses something that must not appear in a published image (account avatar, notification badge, tenant name), a zero-match must be an error. Helpers that loop over `querySelectorAll` and hide each hit succeed silently on zero elements, so a renamed class ships the very thing you meant to remove. Return the match count and fail the run when it is 0. Split the selectors into must-hide and optional so localization or A/B variants that legitimately lack an element do not fail every run.

Prefer `visibility: hidden` over `display: none` so the surrounding layout does not reflow; neighbouring content you wanted to keep stays where the recorded crop expects it.

## VS Code Web (Codespaces, github.dev)

- Toggle shortcuts such as `Ctrl+Alt+B` for the secondary side bar flip state on every run. Detect whether the pane is actually visible before pressing, otherwise a rerun undoes what the previous run achieved.
- Shortcuts are swallowed while a preview iframe holds focus. Click the editor area first, then send the key.
- The workbench renders in the browser's UI language, so consent, workspace-trust, and pane labels differ per machine. Match both the English and the localized label when driving buttons.
- The color theme follows the signed-in GitHub account's Appearance setting, and the workbench reads the OS preference rather than a page attribute. With `Sync with system` it opens light on a light OS. Emulate `prefers-color-scheme` over CDP (`Emulation.setEmulatedMedia`); attribute injection that works on GitHub.com pages does nothing here.
- **Browser zoom is per-origin.** A codespace gets a fresh domain on every start, so manual zoom never carries over and cannot be reproduced from a recorded procedure. Drive magnification with the window size instead.
- `workbench.action.zoomIn` is desktop-only and does nothing on the web build. Substituting CDP `Emulation.setDeviceMetricsOverride` is worse: the page stops filling the window, and `page.mouse` coordinates shift so terminal input lands in the wrong place.
- `https://github.dev/<owner>/<repo>` answers 302 to `https://vscode.dev/github/<owner>/<repo>`, so the address bar shows `vscode.dev`. Say so in any caption that promises github.dev.

### CLI prerequisite

`gh codespace` subcommands need the `codespace` scope. On a `gh` OAuth login, `gh auth refresh -h github.com -s codespace` adds it, but that opens a browser authorization and widens the saved authorization, so ask the user before running it. A PAT login needs the scope on the token instead. HTTP 403 "Must have admin rights to Repository" is one symptom of the missing scope, not proof of it.

## evaluate + fetch

When a logged-in session exposes a REST API, prefer `page.evaluate(() => fetch(...))` for bulk read/write. It avoids navigation instability and uses existing cookies with `credentials: 'same-origin'`.

Rules:

- Use UI for login, preflight, and before/after evidence.
- Keep business logic in Python or the main script; let JavaScript execute fetch/write only.
- Complete fetch -> decision -> update -> result return in one evaluation when possible.
- The same path turns the browser into a local rendering engine: `import()` a renderer (diagram, chart, markdown) into a blank tab and return the produced markup, instead of installing a headless toolchain or posting the payload to a hosted rendering service. The data never leaves the machine, which matters when it holds names or internal structure.
- Pin the exact version of any library imported this way. A floating major on a CDN can change or break an unattended run months later, and the failure surfaces as a parse error far from the change.

## Minimal UI Write Fallback

If an authorized API write is confirmed not applied because of stale automation state or a route mismatch, choose a UI recovery within the shared budget. Permission or service-policy refusals are not a reason to bypass the restriction:

1. Confirm the UI save path is stable.
2. Use the shortest path: search -> select row -> required fields -> save.
3. Verify with list/detail/status text or a read API after save.
4. Record state precisely, such as `saved in UI / pending submit`.

Do not change the business classification just because API automation failed. Change the operation path, then verify the intended destination.

## Slow Transactional Forms

Some enterprise forms keep a separate active-row state, right-pane state, and pending-save state. D365-style expense forms are a common example.

- Treat one row edit as one transaction: select row -> wait for right-pane Amount/Merchant to match -> fill all required fields -> save -> re-read that same row.
- Do not infer success from a button click, toast, or report-level summary. Verify the durable cell/status that represents the real outcome.
- If a pending overlay such as `fastEditRailsMode`, `ShellBlockingDiv`, or `Your last action is still being worked on` appears, stop issuing new writes until it disappears.
- Prefer screenshots plus targeted DOM reads for verification. Large snapshots can be stale or too noisy, while DOM-only reads can miss visually obvious row/detail mismatches.
