# Chrome API Reference

主要 API の基本的な呼び出し方は公式 [API Reference](https://developer.chrome.com/docs/extensions/reference/api) に従う。ここでは権限・上限・踏みやすい挙動だけを扱う（2026-09 時点の公式 docs で確認）。

- Chrome 148+ は標準化された `browser.*` 名前空間もサポートする。WXT は `browser` を提供するため、WXT プロジェクトではそちらに揃える。

## chrome.tabs

- `tabs` 権限は `url` / `title` / `favIconUrl` を読むときだけ必要。ユーザー操作時に現在タブへ一時アクセスするだけなら `activeTab` で足りる。
- `tabs.captureVisibleTab()` は呼び出し頻度に上限がある（`MAX_CAPTURE_VISIBLE_TAB_CALLS_PER_SECOND`）。スクロールしながら連続撮影する処理は間隔を空け、quota エラーを再試行で吸収する。

## chrome.storage

| エリア    | 容量                                                       | コンテンツスクリプトへの公開 | 用途 / 注意                                                       |
| --------- | ---------------------------------------------------------- | ---------------------------- | ----------------------------------------------------------------- |
| `local`   | 10MB（`unlimitedStorage` で解除）                          | 既定で公開                   | 大きなデータ。拡張削除でクリア                                    |
| `sync`    | 約 100KB、1 item 8KB、512 items、120 書込/分・1800 書込/時 | 既定で公開                   | ユーザー設定。同期オフ時は local と同じ挙動。機密データは置かない |
| `session` | 10MB（メモリ）                                             | 既定で非公開                 | SW の一時状態。無効化・再読込・更新・ブラウザ再起動でクリア       |
| `managed` | -                                                          | 既定で公開                   | 企業ポリシー（読取専用）                                          |

- 公開範囲は `chrome.storage.<area>.setAccessLevel()` で変える。
- `localStorage` は使わない: SW で使えず、コンテンツスクリプトではホストページと共有し、閲覧履歴削除で消える。
- 上限超過は即座に失敗（Promise reject）。高頻度書き込みは debounce する。

## chrome.cookies

- `cookies` 権限に加え、対象ドメインの `host_permissions` が必要。
- `cookies.set` の `expirationDate` は UNIX 秒（ミリ秒ではない）。

## chrome.offscreen

SW から DOM API を使うための隠しドキュメント（Chrome 109+、`offscreen` 権限）。

- 同時に開けるのは拡張ごとに 1 つだけ（incognito split モードでは通常/シークレットで各 1 つ）。作成前に存在確認し、並行作成を Promise で直列化する。
- オフスクリーンドキュメント内で使える拡張 API は `chrome.runtime` だけ。結果はメッセージで SW に返す。
- `reasons` は用途に合うものを選び、`justification` を必ず書く。主な値: `DOM_PARSER`、`DOM_SCRAPING`、`IFRAME_SCRIPTING`、`CLIPBOARD`、`BLOBS`、`AUDIO_PLAYBACK`（30 秒無音で自動終了）、`USER_MEDIA`、`DISPLAY_MEDIA`、`WEB_RTC`、`LOCAL_STORAGE`、`WORKERS`、`MATCH_MEDIA`、`GEOLOCATION`、`BATTERY_STATUS`、`TESTING`。

```typescript
let creating: Promise<void> | null = null;

async function setupOffscreenDocument(path: string) {
  const existing = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
    documentUrls: [chrome.runtime.getURL(path)],
  });
  if (existing.length > 0) return;

  if (creating) {
    await creating;
  } else {
    creating = chrome.offscreen.createDocument({
      url: path,
      reasons: ["CLIPBOARD"],
      justification: "クリップボード操作のため",
    });
    await creating;
    creating = null;
  }
}
```

`runtime.getContexts()` は Chrome 116+。それ以前を対象にするなら `clients.matchAll()` で代替する。

## chrome.runtime

- `onMessage` で非同期に `sendResponse` するときはリスナーから `true` を返す。返さないとメッセージチャネルが閉じ、送信側は `undefined` を受け取る。
- `onInstalled` は初回インストール、拡張更新、Chrome 更新で発火する。コンテキストメニュー作成など 1 回限りの初期化はここで行う。

## chrome.scripting

- `scripting` 権限と対象の host 権限（または `activeTab`）が必要。
- `executeScript({ func, args })` の `args` は JSON シリアライズ可能な値だけ。`undefined` などで実ブラウザが失敗し得る（mock では再現しない）。
- `world: "MAIN"` で注入したコードは拡張 API にアクセスできない。

## chrome.action

- `default_popup` を設定している間は `action.onClicked` が発火しない。

## chrome.sidePanel

- Chrome 114+、`sidePanel` 権限と manifest の `side_panel.default_path`。
- `sidePanel.open()`（Chrome 116+）はユーザー操作（アクションのクリック、ショートカット、コンテキストメニュー、拡張ページ/コンテンツスクリプトでのジェスチャー）に応じてのみ呼べる。`windowId` か `tabId` のどちらかが必須。
- アクションアイコンで開くなら `sidePanel.setPanelBehavior({ openPanelOnActionClick: true })`。
- タブ単位の有効/無効やパス切替は `setOptions({ tabId, path, enabled })`。

## 外部リソース

- [Chrome API Reference](https://developer.chrome.com/docs/extensions/reference/api)
