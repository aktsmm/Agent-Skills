---
name: browser-max-automation
description: Visible browser automation using Playwright MCP, CLI, and CDP without interrupting the user's foreground work. Use for navigation, forms, screenshots, repeatable browser workflows, existing-session reuse, or troubleshooting CDP / iframe / modal / file chooser / passkey (WebAuthn) issues.
argument-hint: "自動化したい URL、操作内容、使いたいモード"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Browser Max Automation

Browser automation via Playwright MCP, existing-browser CDP, and direct CDP helpers.

## When to Use

- ブラウザ自動化、UI 確認、フォーム操作、スクリーンショット取得
- MCP で手順を確立してから Python で一括実行したいとき
- 既存ブラウザのログイン状態を CDP 経由で使いたいとき
- Playwright MCP / `connect_over_cdp()` が不安定で、raw CDP WebSocket に切り替えたいとき
- モーダルや file chooser など、通常クリックが壊れやすい UI を扱うとき

## Not the Best Fit

- **API / CLI を先に検討**: 公式 API（YouTube Data API、Microsoft Graph、GitHub API 等）や CLI で read/write が完結するならそちらを優先し、UI が脆い兆候（native file chooser / shadow DOM / 多段ウィザード / レンダラーを止める modal）で固執せず切り替える（例: YouTube Studio UI → `captions.insert`）
- API / CLI だけで完結するなら、該当 domain skill / script を使う
- **URL の生存確認は HTTP client で行うが、dead 判定だけはブラウザまでエスカレートする**。確実な消失の証拠は HTTP 404 / 410 だけ。403 は bot ブロック、timeout は一過性、SSL の `unable to get local issuer certificate` は中間 CA を返さないサーバーで起きる（ブラウザと .NET/schannel は AIA で自動補完するが Python `ssl` はしない）。`Invoke-WebRequest -Uri <url> -Method Get` またはブラウザで裏取りしてから結論を出す
- PowerPoint / Loop / Dynamics 365 の expense entry 画面など専用 skill がある UI は、該当 skill の操作ルールを優先する
- 認証情報、秘密情報、MFA 応答をチャットで受け取らない。必要な入力はブラウザ上でユーザーに処理してもらう
- 例外: 対象サイトが passkey / FIDO2 / WebAuthn 対応なら、CDP 仮想認証機で完全無人化できる。優先順位は **passkey (仮想認証機) > メール OTP > SMS > 物理キー / 生体**。詳細は [references/instructions/webauthn-virtual-authenticator.md](references/instructions/webauthn-virtual-authenticator.md) を参照する

## Choose Mode First

- Default to a visible, headed browser. Use headless only when explicitly requested, never as an automatic recovery path. Reuse a verified authenticated session and an owned work tab when possible; a new profile does not imply reusable authentication.
- Preserve the OS foreground window and the user's selected tab. Do not routinely call `bring_to_front`, `Page.bringToFront`, `Target.activateTarget`, or native focus/keystroke helpers. This applies to browser launch, tab creation, navigation, capture, and recovery, not just clicks.
- If a necessary operation cannot avoid activation, explain why and which bounded step needs it before proceeding. Do not force focus back afterward: the user may have switched applications meanwhile. Credentials and MFA remain user-entered.
- Identify the work tab, goal, and authorized side effects. Broad browser permission does not authorize purchases, trades, cancellations, or contract changes; read-only work must not call helpers that can submit them. Report attempted actions even when a gate prevents submission. Pause writes on user editing, target drift, or lost ownership; viewing a tab does not permit discarding it.
- Prefer API/CLI helpers for supported data operations, but preserve UI execution when the goal is a demo, UI verification, or observation of the browser workflow.

| Mode | Use when | Boundary |
| --- | --- | --- |
| Existing headed browser + MCP/CDP | Authentication or interactive exploration matters | Verify profile, owned target, and non-activation behavior |
| Playwright CLI or saved Playwright script | A stable workflow will repeat | Reuse the session; explicitly request headed mode for new launches |
| Direct CDP WebSocket | A verified lower-level route is needed | Pin target ID; do not bypass ownership or recovery limits |

既存ブラウザ CDP の起動、profile 確認、port drift、認証 URL encode、スクリーンショット取得は [references/instructions/cdp-existing-browser.md](references/instructions/cdp-existing-browser.md) を参照する。
直接 WebSocket CDP の起動フラグ、`websocket-client` 接続、SPA hash navigation、virtual scroll 操作は [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) を参照する。

## Core Loop

```text
1. Reuse a suitable script or establish the flow on an owned, verified work tab.
2. Resolve the target and expected postcondition with a scoped snapshot or query.
3. Perform the action once; wait for the expected state with a deadline.
4. Read back the durable result before retrying or moving to the next item.
```

Keep one working control route instead of repeatedly switching MCP/CLI/CDP. Batch independent reads and return compact results; use full snapshots or screenshots at meaningful visual checkpoints, not after every read.

Wait for required fields and completed loading, not a sample record's presence. Test empty results, zero values, alternate records, and partial rendering through the actual collector; a visible heading alone does not prove complete data.

UI verification では、操作前に期待する state と確認方法を決める。成功 toast やボタン押下だけを成功判定にせず、DOM、URL、永続化された一覧行、API の read 結果、または screenshot / trace などの証跡で確認する。
返信・コメント form では editor に残った送信文が `get_by_text` に一致しても成功ではない。POST の 2xx と、reply ID・件数・本文の readback で確定する。

API と DOM の状態が一時的にずれるケースがある。API が stale / capture failure を返しても、画面上の cell / row の `aria-label` や status text が進展した状態を示しているなら DOM も正本候補として扱う。API 単独で「未完了」と断定しない。

## Decision Patterns

| Situation | Action |
| --- | --- |
| Flow or selectors are still unknown | Use MCP interactively |
| A stable multi-step flow recurs a second time | Reuse or parameterize a saved script when repetition outweighs maintenance; for known bulk work, validate one item and script the rest on the first run |
| Snapshot returns a ref | Use normal click/type |
| Element is visible but has no ref | Confirm visually, then use evaluate or the relevant UI fallback |
| Element is not visible | Wait for a bounded readiness condition; preserve dirty forms and do not force interaction |
| Read-only tabular extraction | Keep navigation evidence, then return compact JSON from DOM evaluation |

CLI commands alone do not remove per-action reasoning. Save a verified sequence with stable locators, input/target parameters, readback, duplicate-write protection, and resumable per-item results. Store task-specific scripts with their project and generic helpers with the owning skill; record purpose and invocation for discovery. Do not persist secrets or transient snapshot refs. See [repeatable workflows](references/instructions/ui-fallbacks.md#repeatable-workflows-and-playwright-cli).

### Virtualized feeds and per-item mutations

- For infinite-scroll feeds, collect a stable item ID or canonical URL for the current batch, then re-resolve that item immediately before each mutation. Do not retain a locator or accessibility ref across a scroll or another item mutation; virtualized DOM nodes are routinely recycled.
- Treat a missing picker option, modal, or navigation as **unknown**, not success. Confirm the persistent assignment state (or an equivalent destination-specific DOM state) before recording an item as done; distinguish an already-assigned item from a picker-render failure.
- Process one bounded batch, persist its completed stable IDs in the active run, then scroll until new IDs appear. End only after several end-of-feed scrolls yield no new stable IDs, and report any unverified items separately.

### handler が何回走ったかを数えるとき

Instrument the listener and compare isolated runs before diagnosing duplicate binding. `locator.click()`, `el.click()`, and `dispatchEvent()` have different event sequences and trust semantics; none is a universal oracle for a real user's click. Verify the resulting state, and never replay a possibly successful write merely to compare methods.

### unsaved editor / draft タブを壊さない

Keep dirty editor tabs in place; use a separate clean work tab instead of navigating or reloading them. Never auto-accept Leave or discard changes.
CDP reporting `No dialog is showing` does not rule out a browser-chrome prompt. Native automation may invoke **Cancel/Stay only** when the owned browser process, selected-tab address, exact leave-site warning and enabled button uniquely match; otherwise stop. Never handle credential, permission or arbitrary dialogs this way.
After dismissal, verify the same target responds; preserved form values are not proof of saved settings. See [unsaved-form safety](references/instructions/unsaved-form-tabs.md) and [native recovery](references/instructions/cdp-recovery-and-context.md).

Azure Portal iframe / OOPIF / trusted event の注意は [references/instructions/azure-portal.md](references/instructions/azure-portal.md) を参照する。
Angular Material / `mat-select` / `cdk-overlay` / disabled save の注意は [references/instructions/angular-material.md](references/instructions/angular-material.md) を参照する。

iframe、force click、file chooser、hidden input、evaluate+fetchは [UI Fallbacks](references/instructions/ui-fallbacks.md) を参照する。`force: true` は要素の実在と可視性を確認した後の最終手段とする。

## Safety Rules

### Content-Filter Preflight

外部プラットフォームは、認証や前後の書き込みが正常でも、送信内容が攻撃 payload に似ているという理由で 403 を返したり書き込みを拒否したりする。技術・セキュリティ内容を繰り返し／一括送信する前に:

- run a deterministic checker for platform-known blocked signatures across **every field included in the request body**, not only the visible field being edited;
- on rejection, capture the failed POST status and response body, then compare same-session successful controls that vary one feature at a time before changing content;
- URL-like text can enter a dedicated link-warning path or return 400 even when nearby plain text succeeds. Use the platform's supported confirmation path or semantically equivalent non-URL wording, preserving meaning and never inserting invisible characters;
- keep one-item rejection isolated so independent later items still run, but keep the overall result non-PASS until the rejected item is fixed or explicitly waived;

信頼できる preflight がない場合は、使い捨て draft / canary target または可逆な 1 件 pilot を使う。成功した probe を同じ経路で復元できない production target 上で mutation の binary search をしない。

### Failure Budget

- Before a write, choose its durable success signal and one bounded recovery. Allow the initial attempt plus at most one recovery attempt per logical operation across UI, CLI, CDP, script, and replacement-tab routes; switching routes does not reset the budget.
- A timeout is not proof of failure. Re-read authoritative state; retry only when non-application is established or an idempotency mechanism prevents duplication. If the outcome remains ambiguous, stop without replaying the write.
- Stop after two failed attempts and report target, attempts, last state, and restart condition. Waiting for normal asynchronous progress is not another attempt: use a deadline and a narrow state check, not fixed sleeps or repeated full-page snapshots.
- UI clickからDOM mutation、keyboard、private frontend internalsへ連続的にfallbackしない。公開されていないViewModelやupload実装の操作は、明示承認のある単発incident以外では使わない
- `Session ended`、login redirect、別contextを検出したらstale DOMを操作しない。再認証後は永続stateを再取得し、未完了操作だけを再開する

### CDP 排他制御

- Use one controller per work target. Do not attach competing Playwright clients to a shared browser unless coordination is verified; raw WebSocket access is not an exemption for concurrent writes or browser-wide settings.
- Pin the verified profile/context and owned target ID; re-check URL, route, query, and item ID before each write batch. Never select the first domain match again after binding the work target.
- Before a necessary handoff, stop the owned runner and verify the current tool's detach/close semantics. Do not use `browser_close` as a generic disconnect: it may destroy tabs or the browser. Preserve dirty tabs; if safe detachment is unavailable, retain the working route or stop.
- Close only explicitly owned, no-longer-needed targets after result verification. Never close the last tab of a shared browser or stop another session's runner as cleanup.

raw WebSocket を使う場合は、CDP command id で応答をフィルタし、`Runtime.enable` / `Page.enable` など必要な domain を先に有効化する。詳細は [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) を参照する。

CDP recovery、blocking dialog、context/page selection は [references/instructions/cdp-recovery-and-context.md](references/instructions/cdp-recovery-and-context.md) を参照する。

### ローカルファイルを MCP で開く

Playwright MCP は `file:` を拒否する（`Access to "file:" protocol is blocked`）。ローカル HTML を開いて検証・計測したいときは、そのフォルダーを `python -m http.server <port> --bind 127.0.0.1` で配信して `http://127.0.0.1:<port>/...` を開く。

MCP は既存ブラウザーの CDP に attach するだけなので、ユーザーがそのブラウザーを閉じると途中で `Target page, context or browser has been closed` になり、再 navigate も debug port への `ECONNREFUSED` で失敗する。**計測は 1 回の `browser_evaluate` で取り切る**。二分探索や全要素走査を複数 call に分けると、途中で失われて最初からやり直しになる。

### 破綻しやすい場面

- modal overlay が snapshot に出ない
- file chooser が残って後続操作を塞ぐ
- CDP 二重接続で入力先が混線する
- CDP の別 context/page を使い、未ログイン画面や別アカウントを操作してしまう
- 「見えているがクリックできない」状態を無理に通常 click で押し切る
- 座標クリックが成功を返すのに何も起きない（要素が実ウィンドウ外にいる）
- ページは正常なのに特定の widget だけ、一定回数の操作後に無反応になる

## Subprocess + CDP Stability (Windows)

Windows の PIPE デッドロック、VS Code terminal の SIGINT、JSON status artifact、taskkill tree kill は [references/instructions/windows-subprocess-cdp.md](references/instructions/windows-subprocess-cdp.md) を参照する。

## Reference Map

| Need | Reference |
| --- | --- |
| Existing browser CDP, profile, port drift, screenshot capture | [references/instructions/cdp-existing-browser.md](references/instructions/cdp-existing-browser.md) |
| Raw CDP WebSocket | [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) |
| WebAuthn virtual authenticator / passkey | [references/instructions/webauthn-virtual-authenticator.md](references/instructions/webauthn-virtual-authenticator.md) |
| CDP recovery and context selection | [references/instructions/cdp-recovery-and-context.md](references/instructions/cdp-recovery-and-context.md) |
| Azure Portal iframe / OOPIF | [references/instructions/azure-portal.md](references/instructions/azure-portal.md) |
| Angular Material forms | [references/instructions/angular-material.md](references/instructions/angular-material.md) |
| Hidden upload, VS Code Web, evaluate+fetch, UI fallback | [references/instructions/ui-fallbacks.md](references/instructions/ui-fallbacks.md) |
| Unsaved editor / draft tab safety | [references/instructions/unsaved-form-tabs.md](references/instructions/unsaved-form-tabs.md) |
| Windows subprocess stability | [references/instructions/windows-subprocess-cdp.md](references/instructions/windows-subprocess-cdp.md) |

## Done Criteria

- Verify the actual control route preserves OS foreground and user tab selection during the operation, not just before/after it; distinguish measured results from unverified behavior. Inspect saved captures for incomplete rendering.
- Report the work target and durable result; for repeat runs, report script reuse and compare elapsed time, tool calls, and retries without omitting verification. See the [acceptance scenarios](references/instructions/ui-fallbacks.md#repeatable-workflows-and-playwright-cli).
- MCP または CDP 設定が完了している
- 対象ページまで安定して到達できる
- 目的の操作が完了している
- 成功判定を toast だけに頼らず、DOM / URL / API read / screenshot / status artifact のいずれかで確認している
- modal / file chooser / iframe / CDP context のどこで詰まるか説明できる
- 一括処理が必要なら MCP から CLI / API helper へ切り替える判断ができている
