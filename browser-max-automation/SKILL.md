---
name: browser-max-automation
description: Browser automation using Playwright MCP, CDP, and direct WebSocket CDP for web testing, UI verification, and form automation. Use when navigating websites, clicking elements, filling forms, taking screenshots, testing web applications, reusing an existing browser session, or troubleshooting CDP / iframe / modal / file chooser issues.
argument-hint: "自動化したい URL、操作内容、使いたいモード"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Browser Max Automation

Browser automation via Playwright MCP.

## When to Use

- ブラウザ自動化、UI 確認、フォーム操作、スクリーンショット取得
- MCP で手順を確立してから Python で一括実行したいとき
- 既存ブラウザのログイン状態を CDP 経由で使いたいとき
- Playwright MCP / `connect_over_cdp()` が不安定で、raw CDP WebSocket に切り替えたいとき
- モーダルや file chooser など、通常クリックが壊れやすい UI を扱うとき

## Choose Mode First

| モード             | 向く場面                                               | メリット                       | 注意点                     |
| ------------------ | ------------------------------------------------------ | ------------------------------ | -------------------------- |
| 新規ブラウザ       | まず安定して動かしたい                                 | 設定が簡単                     | 既存ログイン状態は使えない |
| 既存ブラウザ (CDP) | 普段のブラウザ状態をそのまま使いたい                   | ログイン済み状態を再利用できる | デバッグモード起動が必要   |
| 直接 CDP WebSocket | Playwright CDP が不安定、または MCP と競合させたくない | 低レベル操作で安定しやすい     | CDP コマンドを自前管理する |

### 新規ブラウザモード

`mcp.json` 例:

```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "msedge"],
      "type": "stdio"
    }
  }
}
```

### 既存ブラウザ (CDP)

1. 対象ブラウザを全部閉じる
2. デバッグポート付きで起動する
3. `mcp.json` で `--cdp-endpoint http://localhost:9222` を指定する
4. VS Code をリロードする

```powershell
Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ArgumentList "--remote-debugging-port=9222"
```

PowerShell の `Start-Process -ArgumentList` では、`--profile-directory=Profile 2` のように**値にスペースが入る引数**をそのまま渡すと、別引数に分割されて意図しないプロファイルで起動しうる。1 つの quoted argument として渡す。

```powershell
Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  -ArgumentList '--remote-debugging-port=9222', '"--profile-directory=Profile 2"'
```

#### 既存CDPを再利用する場合

既にデバッグポート付きブラウザが起動しているなら、毎回再起動する必要はない。ただし、**ポートが開いていること** と **目的のプロファイル/ログイン状態であること** は別問題として確認する。
CDP endpoint は環境変数や設定ファイルに入っていても、それだけでは正本にしない。毎回 `/json/version` と port owner を確認し、当回で検証できた endpoint を script / helper / MCP に揃える。

```powershell
# 9222 を握っているプロセスを確認
$conn = Get-NetTCPConnection -LocalPort 9222 -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) {
  Get-CimInstance Win32_Process -Filter "ProcessId=$($conn.OwningProcess)" |
    Select-Object ProcessId, Name, CommandLine
}
```

- `--profile-directory` や `--user-data-dir` を見て、意図したプロファイルか確認する
- 認証が特定プロファイルでしか通らないサイトは、既定 user data を再利用したまま `--profile-directory=<known profile>` を明示する。isolated な `--user-data-dir` は別ログイン状態と巨大なプロファイルごみを生みやすいため、必要時だけ使う
- 既存CDPが別プロファイルなら、既存ブラウザを落とす前に別ポートで目的プロファイルを起動できるか検討する
- **Chrome が同じポート（9222 等）を掴んでいると、Edge の `--remote-debugging-port` が無効になる**。`/json/version` の `Browser` フィールドが `Chrome/...` なら Chrome が占有している。Edge 用に別ポート（9223 等）で起動するか、Chrome を終了してから Edge を起動する
  ```powershell
  # HTTP で Browser フィールドを確認（Edge なら "Microsoft Edge/..." が返る）
  (Invoke-WebRequest "http://localhost:9222/json/version" -UseBasicParsing).Content | ConvertFrom-Json | Select-Object Browser
  ```
- 同じ user-data-dir で既に CDP ポート付き Edge が起動済み（例: `--remote-debugging-port=9222 --profile-directory=Default`）のとき、別プロファイルが必要なら **ポート指定なし** で起動する（`msedge.exe --profile-directory="Profile 2" <url>`）。新ウィンドウが同一プロセスに合流し、既存 CDP ポートで両方のプロファイルタブにアクセスできる。全 Edge を kill する必要はない
- 自動化スクリプト側は `http://localhost:9222` 固定にせず、検出・起動したCDP URLを引数や環境変数で受け取れるようにする
- 既存の endpoint 値があっても「前回は正しかった値」にすぎない。別セッションのブラウザが同じ port を使うことがあるため、接続失敗や login redirect が出たら再ログインより先に endpoint drift を疑う
- helper を複数呼ぶ場合は、途中で endpoint を再推測させず、検証済みの同じ CDP URL を同一 process 環境から渡す

直接 WebSocket CDP の起動フラグ、`websocket-client` 接続、SPA hash navigation、virtual scroll 操作は [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) を参照する。

## Quick Reference

| Command                   | Purpose           |
| ------------------------- | ----------------- |
| `browser_navigate`        | URL を開く        |
| `browser_snapshot`        | 要素 ref を取る   |
| `browser_click`           | ref でクリック    |
| `browser_type`            | テキスト入力      |
| `browser_take_screenshot` | 画面確認          |
| `browser_wait_for`        | 表示待機          |
| `browser_evaluate`        | DOM 直接操作      |
| `browser_file_upload`     | file chooser 対応 |

## Core Loop

```text
1. browser_navigate(url)
2. browser_snapshot で ref を取る
3. browser_click / browser_type で操作する
4. browser_snapshot or screenshot で結果確認する
```

UI verification では、操作前に期待する state と確認方法を決める。成功 toast やボタン押下だけを成功判定にせず、DOM、URL、永続化された一覧行、API の read 結果、または screenshot / trace などの証跡で確認する。

## Decision Patterns

### MCP で続けるか、CLI に切り替えるか

- **MCP**: 1 件ずつ画面を見ながら UI フロー、セレクタ、待機時間を確立する
- **Python CLI**: 手順が固まった後に N 件一括処理する

切り替え基準は単純で、**操作手順をまだ探っているなら MCP、手順が固まったら CLI**。

### snapshot で取れない要素をどう扱うか

- `browser_snapshot` で ref が取れるなら通常操作する
- 画面には見えるのに ref が取れないなら `browser_evaluate` で DOM 直接操作する
- 画面にも見えていないなら、待機かページ再読込を優先する

```text
snapshot で ref 取得
  ├─ 取れた → click / type
  └─ 取れない → screenshot で可視確認
      ├─ 見えている → evaluate で直接操作
      └─ 見えていない → wait / reload
```

### read-only データ抽出を高速化する

一覧表、残高、ステータス確認など、**読み取りだけ** の fallback では、巨大な `browser_snapshot` を何度も解析しない。手順が分かっている画面は `browser_evaluate` で DOM から必要な行だけを JSON 化して返す。

- ページ到達やログイン状態の判定: `browser_snapshot` で証跡を残す
- 表・明細・残高などの定型抽出: `browser_evaluate` で `document.querySelectorAll("tr")` や `document.body.innerText` を処理して JSON を返す
- 不可逆操作の直前・直後: snapshot または screenshot を残す

また、helper / probe / cache の JSON artifact を一次ソースにする場合は、内容を見る前に `timestamp` や対象日を確認する。日付が現在の実行日と合わない artifact は stale とみなし、`ok` や `fast_path_ok` が true でも確定情報として使わない。

### unsaved editor / draft タブを壊さない

Qiita や CMS の draft editor のように、未保存変更を持つタブへそのまま別 URL を開かせると、`beforeunload` dialog が出て upload や遷移が壊れることがある。

- 既に目的の editor / draft タブが開いているなら、そのタブを優先して再利用する
- 新しい draft が必要でも、**既存タブを別 URL へ飛ばさず、新しいタブを開く**
- `dialog.accept()` で無理に吸収する設計を通常フローにしない。beforeunload は race で失敗しやすい
- file upload の前に、現在タブが本当に editor 本体かを URL と title で確認する

このパターンは、Qiita に限らず「未保存フォームを持つ管理画面」全般で効く。

### Azure Portal の deep link は既存タブを再利用する

Azure Portal のような hash-routing な管理画面は、**新しいタブで deep link を開くと login に落ちる** ことがある。別タブで既に portal に入れていても、同じ挙動になる場合がある。

- まず **既にログイン済みの Portal タブ** を再利用する
- 既存タブ上で `page.goto()` や hash 遷移を使い、目的画面へ移動する
- 到達確認は URL だけで済ませず、**title と本文テキスト** も見る
- `.../bgpPeers` のような subview URL でも、overview に戻ったりローディングのまま止まることがある。必要なら raw screenshot を 1 枚残してから次操作へ進む
- Azure Portal のコンテンツ部分は `sandbox-*.reactblade.portal.azure.net` の **iframe 内** にレンダリングされている。`page.evaluate()` では outer frame しか見えないため、タブやフォームの操作は `page.frames()` で iframe を探し、`contentFrame.evaluate()` で操作する
- outer frame から見えない場合でも、CDP の `Target.getTargets()` では `type=iframe` の **OOPIF** として見えることがある。Playwright の frame 探索で詰まったら、`reactblade.portal.azure.net` の iframe target に `Target.attachToTarget(flatten=true)` で直接つなぐ
- ただし Portal の `openBlade()` 系遷移は **trusted user event** 前提のことがあり、React の `onClick` や handler を直接呼んでも blade が開かない場合がある。iframe 内テキストの確認や handler 調査までは自動化できても、最後の blade open は手動クリックへ切り替える判断を持つ

```javascript
// Azure Portal の iframe 内コンテンツを操作する例
const contentFrame = page.frames().find(f => f.url().includes('sandbox-1.reactblade'));
if (contentFrame) {
  const text = await contentFrame.evaluate(() => document.body.innerText);
  // タブクリックも contentFrame 内で行う
  await contentFrame.evaluate(() => {
    const tab = [...document.querySelectorAll('[role="tab"]')]
      .find(t => t.innerText.includes('対象タブ名'));
    if (tab) tab.click();
  });
}
```

判断基準は単純で、**新規タブで login に落ちたら再ログインより先に既存 Portal タブの再利用を試す**。**`page.evaluate` でコンテンツが見えなければ iframe を疑う**。**iframe 内に見えていても blade 遷移だけ動かなければ trusted event 制約を疑い、最後だけ手動に切り替える**。

### Angular Material フォーム自動化

Angular Material (`mat-select`, `mat-dialog`, `cdk-overlay`) を Playwright で操作するときの共通パターン。

**mat-select は nativeInputValueSetter では動かない**

Angular の `mat-select` や `mat-form-field` は、`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call()` で値を書き込んでも **form control の内部状態が更新されない**。ボタンの `disabled` が解除されない、validation が通らない等の症状が出る。

正しい操作:
1. `.mat-select-trigger` をクリックして overlay を開く
2. `[role="option"]` から目的の選択肢を `click()` する
3. 数値入力は increment/decrement ボタン (`[aria-label*="Increment"]`) を N 回クリックする

選択肢ラベルが似ている場合は、**部分一致ではなく exact match を優先**する。`Delivery` と `(ISD only) Delivery` のように部分一致で誤選択しやすい UI は、`/Delivery/i` ではなく `innerText.trim() === 'Delivery'` で選ぶ。

```javascript
// ❌ 動かない
setNativeValue(input, '04');

// ✅ 正しい: increment ボタンを N 回クリック
for (let i = 0; i < 4; i++) {
  document.querySelector('[aria-label*="Increment by 1"]').click();
  await new Promise(r => setTimeout(r, 100));
}

// ✅ 類似ラベルは exact match を優先
const options = [...document.querySelectorAll('[role="option"]')]
  .filter(o => o.offsetParent);
const exact = options.find(o => o.innerText.trim() === 'Delivery');
if (exact) exact.click();
```

**cdk-overlay が操作を塞ぐ**

`mat-select` をクリックすると `cdk-global-overlay-wrapper` が画面を覆う。option 選択後も overlay が残ることがあり、次の `mat-select` や入力要素をクリックできなくなる。

対処:
- option 選択後に `Escape` キーを送って overlay を閉じる
- または次の `mat-select` の `.mat-select-trigger` を直接 `click()` する（overlay は自動的に閉じて新しい overlay が開く）

**Update / Save が disabled のまま**

Angular reactive form では、必須フィールドが 1 つでも未入力なら submit ボタンが `disabled` のままになる。

ただし、確認 dialog 系（Delete reason + Notes など）では submit ボタン自体は常に enabled で、**click は通るが form invalid で silent fail** する亜種がある。`disabled` だけ見て「押せたから成功」と判定せず、操作後に対象 record の消失や status 変化を必ず確認する。

また、modal / overlay が複数重なっている画面では、`document.querySelector('form')` のような広すぎる検索で **古い dialog を掴む** ことがある。フォーム操作は常に **active な overlay / dialog に scope** する。

診断:
```javascript
const invalids = [...form.querySelectorAll('[class*="ng-invalid"]')]
  .filter(el => el.offsetParent)
  .map(el => el.getAttribute('formcontrolname') || el.tagName);
// → ["lateReason"] のように未入力の control 名が分かる

// active dialog を最後の visible overlay に限定
const overlays = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
  .filter(d => d.offsetParent);
const activeForm = overlays[overlays.length - 1]?.querySelector('form');
```

**UI state の事前確認**

`page.evaluate` で連続操作する前に、前回操作の「残り状態」が残っていないかを確認する:
- 日付・タブ・フィルタの選択状態
- 未閉じの overlay / dialog / modal
- URL のハッシュフラグメント（SPA router state）

前回の操作で水曜が選択されたまま次の投入を実行すると、意図しない日に集中する。操作の冒頭で目的の state を明示的にセットする。

### iframe と force click

- iframe が多段なら `contentFrame()` を順に辿る
- SVG オーバーレイなどで塞がれているだけなら `force: true` を検討する
- ただし `force: true` は最後の手段で、まず要素の実在確認と可視確認を優先する

### file chooser が残ったとき

- `browser_file_upload(paths=[])` で空送信して閉じる
- ダメなら別ページへ移動する
- CDP 競合が疑わしいなら Python プロセスや MCP 接続を整理する

### hidden file input upload の fallback

Qiita などの editor では、hidden `input[type=file]` が upload の正体で、Playwright `connectOverCDP()` は WebSocket 接続後に timeout することがある。

- `connectOverCDP()` timeout でも `/json/list` と page target の WebSocket URL が取れるなら、raw CDP に切り替える
- 既に開いている draft / editor tab を target にし、`DOM.setFileInputFiles` で hidden input へ直接流し込む
- upload 後は page HTML か editor text に増えた `qiita-image-store` URL を見て、新しい URL だけを拾う
- beforeunload を避けるため、既存の unsaved draft tab は再利用し、別 URL へ飛ばさない
- 既存 draft で upload がトリガーされず timeout することがある。その場合は既存 draft を壊さず、**fresh draft (`/drafts/new`) を別タブで開いてから** 同じ `DOM.setFileInputFiles` + `change` event を試す
- 既存 draft をそのまま `/drafts/new` へ飛ばすのは避ける。beforeunload dialog と race しやすく、未保存内容を巻き込みやすい

### unsaved editor / draft タブを壊さない

Qiita や CMS の draft editor のように、未保存変更を持つタブへそのまま `drafts/new` や別 URL を開かせると、`beforeunload` dialog が出て upload や遷移が壊れることがある。

- 既に目的の editor / draft タブが開いているなら、そのタブを優先して再利用する
- 新しい draft が必要でも、**既存タブを別 URL へ飛ばさず、新しいタブを開く**
- `dialog.accept()` で無理に吸収する設計を通常フローにしない。beforeunload は race で失敗しやすい
- file upload の前に、現在タブが本当に editor 本体かを URL と title で確認する

このパターンは、Qiita に限らず「未保存フォームを持つ管理画面」全般で効く。

### `browser_run_code` / `page.evaluate` の速度 vs 証跡

`browser_run_code` + `page.evaluate(JS)` で直接 DOM 操作すると、`browser_snapshot` → `browser_click` の MCP 標準フローより速い。ただし snapshot が出ないため、操作の証跡が残りにくい。

| 方式                          | 速度                     | 証跡              | 使い分け                         |
| ----------------------------- | ------------------------ | ----------------- | -------------------------------- |
| MCP 標準 (snapshot → click)   | 遅い（snapshot 数秒/回） | YAML + ref で明確 | 初回探索、デバッグ、重要操作     |
| `browser_run_code` + evaluate | 速い                     | テキスト返却のみ  | 手順確立済みの定型操作、大量入力 |

判断基準: **発注確定など不可逆操作の直前・直後は `browser_take_screenshot` で証跡を残し、中間のフォーム入力は evaluate で高速化**するのが実用的なバランス。

### evaluate + fetch() による API bulk 操作

ログイン済みブラウザ上で、または live session から Cookie / CSRF token / 認証ヘッダーを実行直前に抽出できる場合、`page.evaluate` 内から `fetch()` を使うと **認証処理なしで API を叩ける**。`page.goto()` も不要なので CDP ナビゲーション不安定の影響がゼロ。

| 方式 | 速度 | 安定性 | 用途 |
|------|------|--------|------|
| MCP 標準 (snapshot → click) | 遅い | 高い | 初回探索、デバッグ |
| evaluate + DOM操作 | 速い | 中 | 定型フォーム |
| **evaluate + fetch()** | **最速** | **最高** | **認証済みセッションでの API bulk 操作** |

```javascript
// page.evaluate 内: credentials: 'same-origin' でセッション cookie を自動送信
async ({ apiBase, pageSize }) => {
  const results = [];
  let path = `${apiBase}?page_size=${pageSize}`;
  while (path) {
    const resp = await fetch(path, { credentials: 'same-origin' });
    if (!resp.ok) return { error: resp.status, text: (await resp.text()).slice(0, 200) };
    const data = await resp.json();
    results.push(...(data.results || []));
    path = data.next ? new URL(data.next).pathname + new URL(data.next).search : null;
  }
  return { total: results.length, results };
}
```

**使い分け判断**:

- `page.goto()` → DOM 操作 → フォーム送信: UI が唯一の入口のときだけ
- `page.evaluate` + `fetch()`: REST API があるサイトで bulk read/write するとき
- 同一 eval 内で fetch → 判定 → 更新 → 結果返却まで完結させると、Python ⇔ CDP 往復が 1 回で済む
- **Navigate-free 設計**: `page.goto()` は CDP 接続不安定の最大要因。API があるサイトでは `page.evaluate` + `fetch()` だけで全操作を完結させ、`page.goto()` を一切使わない構成が最も安定する。初期ページ（ログイン済みの任意ページ）に一度だけ接続すれば、以降はすべて evaluate 内の fetch で済む
- live session から session 情報を取れたら、ブラウザ UI は login / preflight / before-after 証跡だけに寄せ、bulk 処理は headless な HTTP/API helper に handoff する

**注意**: JS 内ロジックが Python 正本と乖離すると false positive を生む。判定ロジックは Python 側に寄せ、JS は fetch + PUT の実行役に徹するのが安全。

### API write が不安定なときの最小 UI fallback

認証済み API が read では使えるのに write だけ backend state や preflight guard で止まることがある。こういうときは mutation を無理に押し切らず、**安定している最小 UI 経路だけ**を使う。

- API write が `404` / stale state / guardrail refusal で止まるなら、先に UI 側の保存経路が安定しているか確認する
- UI fallback では、検索 → 対象行選択 → 必須項目だけ入力 → Save の最短経路に絞る
- 保存後は一覧、明細、または画面上の数値で before/after を確認する
- backend が後追いで整合するまで、台帳やログには `saved in UI / pending submit` のように状態を分けて記録する
- 次回の再実行価値があるなら、使い捨て手順で終わらせず helper / CLI に昇格する

## Safety Rules

### CDP 排他制御

MCP Playwright と Python スクリプトは **同じ CDP ポートへ同時接続しない**。
とくに Python 側も `connect_over_cdp()` を使う場合、MCP と Playwright セッションが二重になり、ページ操作が競合して「遷移先が想定外」「フォーム送信が効かない」等の不定失敗が起きる。

| ルール        | 内容                                                                                                               |
| ------------- | ------------------------------------------------------------------------------------------------------------------ |
| 同時接続禁止  | MCP と Python を同じ CDP に同時接続しない                                                                          |
| MCP 切断優先  | Python 実行前に **`browser_close` で MCP ページを解放** してから実行する                                           |
| プロセス確認  | 実行前にゾンビ Python を確認する                                                                                   |
| 標準フロー    | MCP で手順確立 → `browser_close` → Python 単独実行 → 完了後に MCP 再接続して検証                                   |
| raw WebSocket | `websocket-client` 等で CDP WebSocket に直接繋ぐスクリプトは MCP と共存可能（Playwright セッションを張らないため） |

raw WebSocket を使う場合は、CDP command id で応答をフィルタし、`Runtime.enable` / `Page.enable` など必要な domain を先に有効化する。詳細は [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) を参照する。

### CDP 断線復帰

ブラウザがクラッシュ・終了した場合（`Target page, context or browser has been closed` エラー）:

1. CDP ポート確認: `Invoke-WebRequest -Uri 'http://localhost:<port>/json/version' -TimeoutSec 5` — 接続拒否ならブラウザが落ちている
2. ブラウザ再起動: 同じ `--remote-debugging-port` と `--user-data-dir` で起動する
3. CDP 起動確認: 上の確認コマンドで `Browser:` が返ること
4. MCP 再接続: `browser_close`（古いセッション破棄）→ `browser_navigate` で新しいページを開く
5. 認証が必要なサイトは、MCP を `browser_close` してから Python ログインスクリプトを実行し、完了後に MCP で再接続する

### CDP 無応答だが切断はしていない

`/json/list` で tab は見えるのに `Runtime.evaluate` や `Page.enable` が timeout するときは、ブラウザ側で JS dialog / beforeunload prompt / reload 確認が CDP コマンド処理を塞いでいる可能性が高い。完全切断とは別問題で、ブラウザ再起動は最終手段。

診断:

- 1 行 probe: `Runtime.evaluate({expression: '1+1'})` を 10s timeout で投げる。timeout なら blocking 中。
- `Page.handleJavaScriptDialog({accept: false})` を試す。`No dialog is showing` が返れば native dialog ではなく、in-page modal (`cdk-overlay-pane` 等) か Edge/Chrome 固有の system dialog (例: 「サイトを再度読み込みますか？」reload 確認) が原因。

回復:

- native dialog なら `Page.handleJavaScriptDialog` で閉じる。
- in-page modal なら DOM 操作（Escape キー送信、Cancel ボタン synthetic click）で閉じる。
- **ブラウザ固有の system dialog は CDP から触れない**。ユーザーに手動 Cancel を依頼する方が、`Page.reload` リトライや別 helper で吸収しようとするより速く、副作用も少ない。
- リトライ連発は VS Code 共有シェルで stuck shell を連鎖させやすいため、probe で 1-2 回確認して回復しなければ次の操作経路に切り替える（別 shell、手動 fallback、別タブ）。

### CDP context / page 選択

`connect_over_cdp()` では、複数プロファイルや複数 browser context が見えることがある。`browser.contexts[0]` や `context.pages[0]` 固定は、別アカウント・未ログイン・別タブを掴む原因になる。

安全な選び方:

1. すべての `browser.contexts` を走査する
2. 各 context の既存 page を、目的ドメインや管理画面URLを優先して並べる
3. 候補 page ごとにログイン/権限/目的画面への到達を確認する preflight を実行する
4. preflight が通った context/page だけを以後の操作に使う
5. 全候補が失敗したら、失敗したURL・title・理由をJSONに残して停止する

```python
async def select_ready_page(browser, preflight):
  failures = []
  for context_index, context in enumerate(browser.contexts):
    pages = list(context.pages) or [await context.new_page()]
    for page_index, page in enumerate(pages):
      result = await preflight(page)
      result.update({"context_index": context_index, "page_index": page_index})
      if result.get("ok"):
        return context, page, result
      failures.append(result)
  raise RuntimeError(f"No usable browser context found: {failures[:5]}")
```

preflight では最低限、以下を確認する:

- 目的ドメインに到達できている
- ログイン画面へリダイレクトされていない
- 操作に必要な管理画面・権限リンク・APIが見えている

### 破綻しやすい場面

- modal overlay が snapshot に出ない
- file chooser が残って後続操作を塞ぐ
- CDP 二重接続で入力先が混線する
- CDP の別 context/page を使い、未ログイン画面や別アカウントを操作してしまう
- 「見えているがクリックできない」状態を無理に通常 click で押し切る

## Subprocess + CDP Stability (Windows)

CLI で Playwright / CDP 子プロセスを呼ぶとき、Windows 固有の落とし穴がある。

### PIPE デッドロック

`subprocess.Popen(stdout=PIPE)` + `proc.communicate()` は、Playwright が内部で起動する Node.js ツリーがパイプハンドルを保持するためデッドロックする。`taskkill /F /T` で子プロセスを殺してもパイプの `join()` が戻らない。

**解決策**: stdout / stderr をファイルにリダイレクトし、`proc.poll()` ループで完了を検知する。

```python
with open(stdout_path, "w", encoding="utf-8") as fout, \
     open(stderr_path, "w", encoding="utf-8") as ferr:
    proc = subprocess.Popen(cmd, stdout=fout, stderr=ferr,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

while proc.poll() is None:
    if time.time() - start > timeout:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True, timeout=10)
        proc.wait()
        break
    time.sleep(0.5)
```

### VS Code ターミナルの SIGINT 干渉

VS Code 共有ターミナルで長時間の `time.sleep()` や `proc.communicate()` を実行すると、ターミナルが予期しない `SIGINT` を送り `KeyboardInterrupt` で死ぬことがある。

対策:

1. スクリプト冒頭で `signal.signal(signal.SIGINT, signal.SIG_IGN)` を宣言する
2. または `Start-Process -Wait` で独立プロセスとして実行する

```powershell
Start-Process -FilePath ".venv\Scripts\python.exe" `
  -ArgumentList "script.py","--all" `
  -NoNewWindow -Wait `
  -RedirectStandardOutput "stdout.txt" `
  -RedirectStandardError "stderr.txt"
```

### JSON status artifact を正本にする

長時間 runner が `--output-json` や同等の status file を返せるなら、完了判定は terminal の見た目ではなく **JSON の機械可読フィールド** を正本にする。

- `final_status` / `overall_status` / `status` のような field を優先して見る
- stdout の完了メッセージ、文字化け、途中で切れたログは補助証跡として扱う
- Windows terminal では encoding 崩れや出力欠落が起きるため、`stdout に成功っぽい文が出た` だけで完了扱いにしない

推奨:

```python
result = json.loads(Path(output_json).read_text(encoding="utf-8"))
if result.get("final_status") != "passed":
    raise RuntimeError(f"runner failed: {result.get('final_status')}")
```

### taskkill ツリー kill

CDP 経由の子プロセスは Node.js + ブラウザ接続のツリーを持つ。`proc.kill()` では孫プロセスが残る。

```powershell
taskkill /F /T /PID <pid>
```

Python から:

```python
subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
               capture_output=True, timeout=10)
```

## Done Criteria

- MCP または CDP 設定が完了している
- 対象ページまで安定して到達できる
- 目的の操作が完了している
- modal / file chooser / iframe のどこで詰まるか説明できる
- 一括処理が必要なら MCP から CLI へ切り替える判断ができている
