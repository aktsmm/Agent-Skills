# よくあるパターン集

WXT / MV3 拡張で繰り返し使う実装パターンと落とし穴。API の基本形は [chrome-api.md](chrome-api.md) と WXT 公式を参照。

## メッセージング

- 非同期応答は `return true`（[chrome-api.md](chrome-api.md#chromeruntime)）。送信先タブにコンテンツスクリプトが未注入だと `tabs.sendMessage` は `Could not establish connection` で失敗するので、捕捉して注入または無視する。
- 型安全にするならメッセージ名 → request/response の型マップを 1 か所で定義し、送受信の両側で同じ型を使う。WXT では [Messaging](https://wxt.dev/guide/essentials/messaging) の推奨ライブラリを使ってよい。

```typescript
type MessageMap = {
  GET_DATA: { request: { key: string }; response: { value: string } };
};

async function sendMessage<T extends keyof MessageMap>(
  type: T,
  payload: MessageMap[T]["request"],
): Promise<MessageMap[T]["response"]> {
  return chrome.runtime.sendMessage({ type, payload });
}
```

## ストレージ

- WXT では `storage.defineItem<T>("local:key")` で型付きアイテムを定義し、`getValue` / `setValue` / `watch` を使う。手書きのラッパーより WXT の [Storage](https://wxt.dev/guide/essentials/storage) を優先する。
- UI で購読する場合は初期値の読み込みと `onChanged`（または `watch`）の購読を両方行い、アンマウント時に解除する。

## Content Script

- **コンテキスト無効化**: 拡張の更新・無効化後も既存ページのコンテンツスクリプトは残り、拡張 API 呼び出しが `Extension context invalidated` で失敗する。WXT では `ctx.addEventListener` / `ctx.setTimeout` などを使い、`ctx.isValid` を確認する。
- **スタイル分離**: WXT の `createShadowRootUi`（`cssInjectionMode: "ui"`、CSS は entrypoint で import）を使う。`all: initial` で継承スタイルは戻るが、`rem` は `<html>` の font-size に依存するため Tailwind 等はサイトごとに大きさが変わる。ページの CSS 影響を完全に避けたい、または HMR が必要なら `createIframeUi`。
- 動的に出現する要素への mount は `anchor` + `ui.autoMount()`。
- **ページ変数へのアクセス**: `world: "MAIN"` は拡張 API を使えない。WXT は unlisted script + `injectScript()`（`web_accessible_resources` に登録）を推奨しており、親コンテンツスクリプト経由で拡張 API と連携できる。
- **SPA**: コンテンツスクリプトはフルリロード時にしか走らない。広めの `matches` で注入し、`wxt:locationchange` イベントと `MatchPattern` で対象 URL を判定する。
- WXT の import は `#imports` 経由で解決される（例: `createShadowRootUi` の実体は `wxt/utils/content-script-ui/shadow-root`）。古い `wxt/client` からの import は現行版に合わせる。

## ブラウザ自動操作

### ref 番号システム

DOM要素に一意の ref 番号を付与し、LLMが確実に要素を特定できるようにする。

```typescript
// DOM解析でref番号を付与
function assignRefNumbers() {
  const interactiveElements = document.querySelectorAll(
    'button, a, input, select, [role="button"], [role="link"], [role="checkbox"]',
  );

  interactiveElements.forEach((el, i) => {
    el.setAttribute("data-copilot-ref", `e${i}`);
  });

  // 出力形式
  // [e0] button "次へ"
  // [e5] radio "そう思わない"
}

// LLMからの指示を解析
// [ACTION: click, e5]
function executeAction(action: string, ref: string) {
  const element = document.querySelector(`[data-copilot-ref="${ref}"]`);
  if (!element) return;

  switch (action) {
    case "click":
      (element as HTMLElement).click();
      break;
    case "focus":
      (element as HTMLElement).focus();
      break;
  }
}
```

### 操作ペース

連続操作は対象サイトの負荷と利用規約を考慮して間隔を空ける。ボット検出や利用制限の回避を目的とした人間らしさの偽装（ランダム遅延、マウス移動の模倣など）は実装しない。

## Service Worker

### 長時間処理の分割

SW は処理中でも終了され得る（[manifest-v3.md](manifest-v3.md#service-worker-のライフサイクル)）。即座に `sendResponse` で受付を返し、チャンクごとに進捗を `storage.session` に保存して、再起動後に続きから再開できるようにする。

```typescript
async function processInChunks(data: unknown[]) {
  const CHUNK_SIZE = 100;
  const { progress = 0 } = await chrome.storage.session.get("progress");
  for (let i = progress; i < data.length; i += CHUNK_SIZE) {
    await processChunk(data.slice(i, i + CHUNK_SIZE));
    await chrome.storage.session.set({ progress: i + CHUNK_SIZE });
  }
  await chrome.runtime.sendMessage({ type: "TASK_COMPLETE" });
}
```

### アラームによる再開

`chrome.alarms`（最小 30 秒）で保留タスクを定期確認し、残っていれば再開する。SW を延命するための常時アラームにはしない。

## スクリーンショット

- `tabs.captureVisibleTab()` は `activeTab`（ユーザー操作時）か `<all_urls>` 相当の host 権限が必要で、Base64 の data URL を返す。
- フルページ撮影でスクロール→撮影を繰り返すと呼び出し頻度上限に当たる。各撮影の間隔を空け、固定ヘッダーの重複や遅延読み込み画像を考慮して結合する。

## 外部リソース

- [WXT Messaging](https://wxt.dev/guide/essentials/messaging)
- [WXT Content Scripts](https://wxt.dev/guide/essentials/content-scripts)
- [Chrome Extensions Samples](https://github.com/GoogleChrome/chrome-extensions-samples)
