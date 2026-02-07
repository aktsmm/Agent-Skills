# Manifest V3 ガイド

Manifest V3（MV3）は2025年以降の必須標準。

---

## MV2 → MV3 主要変更点

| 機能                   | MV2                        | MV3                       |
| ---------------------- | -------------------------- | ------------------------- |
| バックグラウンド処理   | Background Pages           | **Service Workers**       |
| ネットワークリクエスト | webRequest（ブロッキング） | **declarativeNetRequest** |
| リモートコード         | 許可                       | **禁止**                  |
| コード実行             | `eval()` 許可              | **禁止**                  |
| CSP                    | 柔軟                       | **厳格化**                |

---

## Service Worker 制限事項

| 制限               | 内容                         | 対処法                           |
| ------------------ | ---------------------------- | -------------------------------- |
| 30秒タイムアウト   | イベント処理後30秒でスリープ | `chrome.alarms` でウェイクアップ |
| DOMアクセス不可    | `document`/`window` 不可     | `chrome.offscreen` を使用        |
| 永続化なし         | 変数はスリープ時にクリア     | `chrome.storage.session` を使用  |
| eval()禁止         | 動的コード実行不可           | 事前にバンドル                   |
| リモートコード禁止 | CDNからのスクリプト不可      | 全コードをバンドル               |

### 30秒タイムアウト対策

```typescript
// chrome.alarms でウェイクアップ
chrome.alarms.create("keepAlive", { periodInMinutes: 0.5 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "keepAlive") {
    // 定期的な処理
  }
});
```

### DOMアクセスが必要な場合

```typescript
// offscreen ドキュメントを使用
await chrome.offscreen.createDocument({
  url: "offscreen.html",
  reasons: ["DOM_PARSER"],
  justification: "HTML解析のため",
});

// offscreen.js 内でDOM操作
const parser = new DOMParser();
const doc = parser.parseFromString(html, "text/html");
```

### 状態の永続化

```typescript
// ❌ グローバル変数（スリープでクリア）
let counter = 0;

// ✅ storage.session を使用
await chrome.storage.session.set({ counter: 0 });

const { counter } = await chrome.storage.session.get("counter");
await chrome.storage.session.set({ counter: counter + 1 });
```

---

## マニフェスト構成

### 基本構成

```json
{
  "manifest_version": 3,
  "name": "Extension Name",
  "version": "1.0.0",
  "description": "説明文",
  "icons": {
    "16": "icons/16.png",
    "48": "icons/48.png",
    "128": "icons/128.png"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/16.png",
      "48": "icons/48.png"
    }
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ],
  "permissions": ["storage", "activeTab"],
  "host_permissions": ["<all_urls>"]
}
```

### WXT での設定

```typescript
// wxt.config.ts
import { defineConfig } from "wxt";

export default defineConfig({
  manifest: {
    name: "Extension Name",
    permissions: ["storage", "activeTab", "scripting"],
    host_permissions: ["<all_urls>"],
  },
});
```

---

## 権限のベストプラクティス

### 最小権限の原則

```json
{
  // ❌ 過剰な権限
  "permissions": ["tabs", "history", "bookmarks"],
  "host_permissions": ["<all_urls>"]
}

{
  // ✅ 必要最小限
  "permissions": ["activeTab"],
  "host_permissions": ["*://*.example.com/*"]
}
```

### オプショナル権限

```json
{
  "optional_permissions": ["tabs", "history"],
  "optional_host_permissions": ["*://*.newsite.com/*"]
}
```

```typescript
// 必要時にリクエスト
const granted = await chrome.permissions.request({
  permissions: ["tabs"],
  origins: ["*://*.newsite.com/*"],
});
```

---

## MV3 移行時の一般的な問題

| 問題                                 | 原因                        | 解決策                            |
| ------------------------------------ | --------------------------- | --------------------------------- |
| バックグラウンドスクリプトが動かない | Background Page → SW 移行   | `background.service_worker`を使用 |
| ネットワーク操作が動かない           | webRequest ブロッキング廃止 | declarativeNetRequest に移行      |
| 外部スクリプトが読み込めない         | リモートコード禁止          | 全コードをバンドルに含める        |
| localStorage 使用不可                | SW で Web Storage API 不可  | `chrome.storage` に移行           |
| `eval()` エラー                      | 動的コード実行禁止          | 事前コンパイル                    |

---

## declarativeNetRequest

ネットワークリクエストのルールベース制御。

### 権限

```json
{
  "permissions": ["declarativeNetRequest"],
  "host_permissions": ["<all_urls>"]
}
```

### ルール定義

```json
// rules.json
[
  {
    "id": 1,
    "priority": 1,
    "action": { "type": "block" },
    "condition": {
      "urlFilter": "*://ads.example.com/*",
      "resourceTypes": ["script", "image"]
    }
  },
  {
    "id": 2,
    "priority": 1,
    "action": {
      "type": "redirect",
      "redirect": { "url": "https://example.com/blocked.html" }
    },
    "condition": {
      "urlFilter": "*://blocked.com/*"
    }
  }
]
```

### マニフェスト設定

```json
{
  "declarative_net_request": {
    "rule_resources": [
      {
        "id": "ruleset_1",
        "enabled": true,
        "path": "rules.json"
      }
    ]
  }
}
```

---

## 外部リソース

- [Migrate to Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate)
- [Service Worker Lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers)
