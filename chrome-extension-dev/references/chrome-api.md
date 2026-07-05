# Chrome API Reference

Chrome拡張機能で使用する主要APIの詳細ガイド。

---

## chrome.tabs API

タブの作成・変更・再配置など、ブラウザのタブシステムを操作。

### 権限

```json
{
  "permissions": ["tabs"],        // url, title等のセンシティブ情報
  "permissions": ["activeTab"],   // ユーザー操作時の一時的アクセス
  "host_permissions": ["*://*/*"] // ホストへの完全アクセス
}
```

### よく使うメソッド

```typescript
// 現在のタブを取得
async function getCurrentTab() {
  const [tab] = await chrome.tabs.query({
    active: true,
    lastFocusedWindow: true,
  });
  return tab;
}

// 新しいタブを作成
chrome.tabs.create({ url: "https://example.com" });

// タブにメッセージを送信
const response = await chrome.tabs.sendMessage(tabId, { type: "getData" });

// タブを更新
await chrome.tabs.update(tabId, { url: "https://new-url.com" });

// タブを閉じる
await chrome.tabs.remove(tabId);
```

### イベント

```typescript
// タブがアクティブになった時
chrome.tabs.onActivated.addListener((activeInfo) => {
  console.log("Tab activated:", activeInfo.tabId);
});

// タブが更新された時
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    console.log("Tab loaded:", tab.url);
  }
});

// タブが閉じられた時
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  console.log("Tab closed:", tabId);
});
```

---

## chrome.storage API

ユーザーデータの保存・取得・変更追跡。

### 権限

```json
{
  "permissions": ["storage"]
}
```

### Storage エリア

| エリア    | 容量             | 同期 | 用途                       |
| --------- | ---------------- | ---- | -------------------------- |
| `local`   | 10MB             | ❌   | 大きなデータ               |
| `sync`    | 100KB (8KB/item) | ✅   | ユーザー設定               |
| `session` | 10MB             | ❌   | 一時データ（メモリ）       |
| `managed` | -                | -    | 管理者ポリシー（読取専用） |

### 使用例

```typescript
// ローカルストレージに保存
await chrome.storage.local.set({ key: "value" });

// 取得
const result = await chrome.storage.local.get(["key"]);
console.log(result.key);

// Sync ストレージ（ブラウザ間同期）
await chrome.storage.sync.set({ settings: { theme: "dark" } });

// Session ストレージ（メモリ、再起動でクリア）
await chrome.storage.session.set({ tempData: {} });

// 変更を監視
chrome.storage.onChanged.addListener((changes, areaName) => {
  for (const [key, { oldValue, newValue }] of Object.entries(changes)) {
    console.log(`${key} changed from ${oldValue} to ${newValue}`);
  }
});
```

### ⚠️ 注意: localStorage は使わない

- Service Worker で使用不可
- Content Script はホストページとストレージを共有
- ブラウザ履歴削除でデータ消失

---

## chrome.cookies API

Cookieの取得・設定・変更通知。

### 権限

```json
{
  "permissions": ["cookies"],
  "host_permissions": ["*://*.example.com/"]
}
```

### 使用例

```typescript
// Cookie取得
const cookie = await chrome.cookies.get({
  url: "https://example.com",
  name: "session_id",
});

// 全Cookie取得
const cookies = await chrome.cookies.getAll({ domain: "example.com" });

// Cookie設定
await chrome.cookies.set({
  url: "https://example.com",
  name: "my_cookie",
  value: "my_value",
  expirationDate: Date.now() / 1000 + 3600,
});

// Cookie削除
await chrome.cookies.remove({
  url: "https://example.com",
  name: "my_cookie",
});

// 変更監視
chrome.cookies.onChanged.addListener((changeInfo) => {
  console.log("Cookie changed:", changeInfo.cookie.name, changeInfo.cause);
});
```

---

## chrome.offscreen API

Service WorkerでDOM操作が必要な場合に使用。

### 権限

```json
{
  "permissions": ["offscreen"]
}
```

### 使用理由

| 理由             | 説明                  |
| ---------------- | --------------------- |
| `CLIPBOARD`      | クリップボードAPI使用 |
| `DOM_PARSER`     | DOMParser使用         |
| `DOM_SCRAPING`   | iframe内のDOM取得     |
| `AUDIO_PLAYBACK` | 音声再生              |
| `USER_MEDIA`     | getUserMedia()        |
| `WEB_RTC`        | WebRTC使用            |

### 使用例

```typescript
// オフスクリーンドキュメントが存在するか確認
async function setupOffscreenDocument(path: string) {
  const existingContexts = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
    documentUrls: [chrome.runtime.getURL(path)],
  });

  if (existingContexts.length > 0) return;

  await chrome.offscreen.createDocument({
    url: path,
    reasons: ["CLIPBOARD"],
    justification: "クリップボード操作のため",
  });
}

// 使用
await setupOffscreenDocument("offscreen.html");
await chrome.runtime.sendMessage({ type: "copy", data: "text" });
```

---

## chrome.runtime API

拡張機能のライフサイクル・メッセージング。

### メッセージング

```typescript
// メッセージ送信
const response = await chrome.runtime.sendMessage({
  type: "getData",
  key: "foo",
});

// メッセージ受信
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "getData") {
    sendResponse({ value: "bar" });
  }
  return true; // 非同期レスポンス用
});
```

### インストール・更新イベント

```typescript
chrome.runtime.onInstalled.addListener(({ reason }) => {
  if (reason === "install") {
    chrome.tabs.create({ url: "onboarding.html" });
  }
  if (reason === "update") {
    console.log("Extension updated");
  }
});
```

---

## chrome.scripting API

Content Script やCSSの動的注入。

### 権限

```json
{
  "permissions": ["scripting"],
  "host_permissions": ["<all_urls>"]
}
```

### 使用例

```typescript
// スクリプト注入
await chrome.scripting.executeScript({
  target: { tabId: tabId },
  func: () => {
    document.body.style.backgroundColor = "red";
  },
});

// CSS注入
await chrome.scripting.insertCSS({
  target: { tabId: tabId },
  css: "body { background: blue !important; }",
});
```

---

## chrome.action API

ツールバーアイコンの制御。

### 使用例

```typescript
// バッジテキスト設定
await chrome.action.setBadgeText({ text: "5" });
await chrome.action.setBadgeBackgroundColor({ color: "#FF0000" });

// アイコン変更
await chrome.action.setIcon({ path: "icons/active.png" });

// ポップアップ変更
await chrome.action.setPopup({ popup: "popup2.html" });

// クリックイベント（ポップアップなしの場合）
chrome.action.onClicked.addListener((tab) => {
  console.log("Action clicked on tab:", tab.id);
});
```

---

## chrome.sidePanel API

サイドパネルの表示制御。

### 権限

```json
{
  "permissions": ["sidePanel"]
}
```

### マニフェスト設定

```json
{
  "side_panel": {
    "default_path": "sidepanel.html"
  }
}
```

### 使用例

```typescript
// サイドパネルを開く
await chrome.sidePanel.open({ windowId: windowId });

// 特定タブでパネル変更
await chrome.sidePanel.setOptions({
  tabId: tabId,
  path: "custom-panel.html",
  enabled: true,
});
```

---

## 外部リソース

- [Chrome API Reference](https://developer.chrome.com/docs/extensions/reference)
