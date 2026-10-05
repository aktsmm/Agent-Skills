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
- After an authentication action that may open another tab, re-enumerate contexts and pages. Bind the post-authentication page by its URL and an authenticated control instead of reading the stale pre-authentication page.
- In a split-pane SPA, a matching search result does not prove its detail pane is selected. Select the result, then wait for both its title and stable ID to match before a mutation.
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
- If an upload button changes to a dedicated upload view without emitting a file chooser, treat the view transition as successful navigation. Resolve the new view's `input[type=file]` and set the file once instead of replaying the button click.
- When upload consent starts parsing or a loading state, wait for the form's required selector to reappear. Refill parser-controlled fields afterward, then verify the filename, field values, and submit-enabled state without submitting unless authorized.
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

For raw CDP-controlled download buttons, set `Browser.setDownloadBehavior({behavior: 'allow', downloadPath: <dir>, eventsEnabled: true})` before clicking. Do not override download behavior underneath a Playwright-controlled context; use its download API instead.

With Playwright MCP, a chooser opened inside `browser_run_code_unsafe` becomes MCP modal state instead of reaching the script's `waitForEvent('filechooser')`; finish it with `browser_file_upload`. Its allowed-root check compares the drive letter case literally, so pass the path in the same case as the reported root (for example `c:\...`). Some apps (e.g. D365) ignore `setInputFiles` on the hidden input and only accept the chooser route; verify the app's own "selected file" field before continuing.

## Playwright MCP run_code Files and PDF Capture

- `browser_run_code_unsafe` with `filename` wraps the file as `(<content>)(page)`. A workspace formatter that saves the file with a trailing `};` breaks it with `SyntaxError: Unexpected token ';'`; strip the trailing semicolon or keep the script outside formatted paths.
- Do not await download completion inside `browser_run_code_unsafe` (`waitForEvent('download')`, CDP `Browser.downloadProgress`). On a headed browser attached over CDP the event may never arrive and the tool call hangs until the user cancels. Trigger the download, return, then verify the file on disk from the shell. After two hangs on the same route, stop and ask the user.
- `page.pdf()` works on a headed Chromium/Edge attached over CDP. For a site "Print" button that opens a print-layout popup, stub `window.print` with `context.addInitScript` first, wait for the popup `load`, verify its text, then `popup.pdf()` and close it. Prefer this over printing the input form page, which captures editable boxes and caret.

### Durable Downloads and GUID Filenames

- Playwright's temporary download filename can be a random GUID without an extension, so the browser download list may show a generic icon. Neither that icon nor clicking the history entry proves the file is corrupt or durable.
- In standalone Playwright, register `expect_download()` before the click, check `download.failure()`, and `save_as()` an explicit persistent path with the intended extension. Use `suggested_filename` when preserving the provider's name. Temporary downloads belong to the context and must not be the final deliverable. The MCP event-wait caveat above still applies.
- Record the document identity and saved path immediately, then validate file signature, parser readability, and expected content; inspect a render for missing or clipped content. After a verification failure, inspect the existing file and reconcile its identity before another download. Hash-check copied/renamed originals.
- Return only the task-relevant page region, never an entire account home/chat sidebar. Keep signed document URLs and authentication state out of logs and reusable scripts.
- On Windows, configure UTF-8 output before printing non-ASCII page/PDF text. A console encoding error is a reporting failure, not evidence of a failed download or sign-in.

Official API: https://playwright.dev/python/docs/api/class-download

## GitHub issue / PR image attachment

GitHub has no public API for issue attachments. Upload through a signed-in comment box without posting: click `Paste, drop, or click to add files`, send the file to the chooser, wait for `Uploading` to disappear, then read the `https://github.com/user-attachments/assets/...` URL from the textarea value. Clear the textarea (`select()` + `execCommand('delete')`; keyboard shortcuts may not reach it), confirm the comment count is unchanged, and write the URL into the body with `gh issue edit --body-file`.

## Shadow-DOM / Material widgets: rect comes back (0,0)

In Angular-Material / web-component UIs (GCP Console, YouTube Studio), many buttons live in shadow DOM and `el.getBoundingClientRect()` returns `{x:0, y:0, width:0}` to page-level JS, so a JS-computed click misses. Click by screenshot pixel coordinates with `Input.dispatchMouseEvent` instead. Also scope element queries to the form region (x/y bounds): a generic `document.querySelector('mat-select,[role=combobox]')` often grabs the page's top search box and opens a search overlay — press Escape to dismiss, then retry within the form area.

## Click times out on "visible, enabled and stable"

Background/minimized rendering can contribute to actionability timeouts, but it is not a universal failure mode. Inspect readiness, overlays, and current target state with a bounded query; successful reads or fills do not prove a click can succeed.

Keep ordinary scoped click/fill as the default. Only choose JS click as the single recovery when its semantics are acceptable and any prior write is known not to have applied. Synthetic events are not equivalent to trusted input. Verify durable state; an ambiguous timeout stops writes rather than triggering another click method or automatic foreground activation.

## Text locator matches hidden or whitespace-shifted rows

- Do not fix any locator (text, `name`/attribute, or the first `querySelector` match) to the first hit when duplicate hidden and visible nodes can coexist. Enumerate matches and act on the first candidate with a non-empty visible bounding box. Forms that toggle read/edit modes keep both copies; pressing the hidden copy sends no request and logs no error, which looks like a silently ignored control.
- Rich-text APIs and list DOMs can represent the same text differently: an API may fold `<br>` into spaces while `innerText` joins the boundary without a space. If ordinary text matching finds no visible row, compare whitespace-stripped text and choose the smallest visible container containing the target, rather than a broad ancestor.
- A fallback match only identifies a row to open. Before filling or saving, compare the opened editor's complete normalized text with the expected item; reject a shared prefix or section label so a whitespace-tolerant click cannot overwrite a neighboring row.

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

A concrete gesture case: a button that calls `window.open` (new tab/popup) does nothing visible when clicked with `el.click()` from `Runtime.evaluate`, because there is no user activation, and the target list shows no new page. Click the element's centre with `Input.dispatchMouseEvent` (`mouseMoved`, `mousePressed`, `mouseReleased`) instead, then re-list targets and bind the new tab by its full URL. Do not count the silent miss as an application failure or replay a possibly-applied write.

## Hidden tabs and ambiguous targets

- A background tab can make `Page.captureScreenshot` time out or leave a spinner in the capture. Check `document.visibilityState`; in a browser the run owns, select the owned tab once (`/json/activate/<id>`) and re-check instead of retrying the capture.
- Wrap `/json/list` results in `@(...)` before filtering (a single page unwraps to a scalar) and match tabs by full URL. A path fragment such as `/agents/new` can match two apps.
- Do not treat an empty `[role=dialog]` / `aria-live` query as "no message". Error banners often render outside those roles, so search `document.body.innerText` for the expected text and read the screenshot.
- Do not conclude a documented control is missing until gating steps are done. Progressive forms reveal later sections (for example a payment-method choice) only after earlier sections are saved; read the page's own hint ("Add X in order to ...") and prior run records first.

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

## Rich-text Editor Replacement

- In TipTap/contenteditable fields, `.fill()` may append to the old text. Before saving, read back the entire field, check the old anchor is absent, and use the site's own length counter rather than `innerText.length` for limits.
- If concatenated, focus only that editor, use Ctrl+A then Backspace, verify the field and counter are empty, refill, and read back before saving. Preserve unrelated paragraphs when changing only one claim.
- Click-to-edit `<textarea>` bound to a framework (rendered block turns into a textarea + Save): if the block's click times out, dispatch one `click` event on it, then set the value with the native setter (`Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(el, v)`) and dispatch `input`/`change`; a plain `el.value =` may be ignored. Edit by string replace on the value just read, aborting unless the anchor occurs exactly once and the new text is absent, then press that form's own Save.
- When Save publishes immediately (no draft/preview), treat it as the publish write: show the exact body first, click once, and read back the public page with a cache-busting query instead of the editor state.
- The native setter plus `input` does not persist in every controlled field (seen on a React `<input type=text>`: the DOM value showed but the form state stayed empty, so the dependent Create/Save button stayed disabled). Click the field with a real mouse event, type with `Input.insertText`, and judge success by the dependent control becoming enabled or by a saved-state label, not by reading the field's `value`.

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

## Virtualized feeds and per-item mutations

- For infinite-scroll feeds, collect a stable item ID or canonical URL for the current batch, then re-resolve that item immediately before each mutation. Do not retain a locator or accessibility ref across a scroll or another item mutation; virtualized DOM nodes are routinely recycled.
- Treat a missing picker option, modal, or navigation as **unknown**, not success. Confirm the persistent assignment state (or an equivalent destination-specific DOM state) before recording an item as done; distinguish an already-assigned item from a picker-render failure.
- Process one bounded batch, persist its completed stable IDs in the active run, then scroll until new IDs appear. End only after several end-of-feed scrolls yield no new stable IDs, and report any unverified items separately.

## handler が何回走ったかを数えるとき

Instrument the listener and compare isolated runs before diagnosing duplicate binding. `locator.click()`, `el.click()`, and `dispatchEvent()` have different event sequences and trust semantics; none is a universal oracle for a real user's click. Verify the resulting state, and never replay a possibly successful write merely to compare methods.

## Content-Filter Preflight

外部プラットフォームは、認証や前後の書き込みが正常でも、送信内容が攻撃 payload に似ているという理由で 403 を返したり書き込みを拒否したりする。技術・セキュリティ内容を繰り返し／一括送信する前に:

- run a deterministic checker for platform-known blocked signatures across **every field included in the request body**, not only the visible field being edited;
- on rejection, capture the failed POST status and response body, then compare same-session successful controls that vary one feature at a time before changing content;
- URL-like text can enter a dedicated link-warning path or return 400 even when nearby plain text succeeds. Use the platform's supported confirmation path or semantically equivalent non-URL wording, preserving meaning and never inserting invisible characters;
- keep one-item rejection isolated so independent later items still run, but keep the overall result non-PASS until the rejected item is fixed or explicitly waived;

信頼できる preflight がない場合は、使い捨て draft / canary target または可逆な 1 件 pilot を使う。成功した probe を同じ経路で復元できない production target 上で mutation の binary search をしない。
