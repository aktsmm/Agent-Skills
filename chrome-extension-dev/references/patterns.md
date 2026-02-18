# よくあるパターン集

ブラウザ拡張機能開発でよく使う実装パターン。

---

## メッセージングパターン

### Content Script ↔ Service Worker

```typescript
// content.ts - メッセージ送信
const response = await chrome.runtime.sendMessage({
  type: "GET_DATA",
  payload: { key: "value" },
});

// background.ts - メッセージ受信
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_DATA") {
    // 非同期処理
    fetchData(message.payload).then((data) => {
      sendResponse({ success: true, data });
    });
    return true; // 非同期レスポンスを示す
  }
});
```

### Service Worker → Content Script

```typescript
// background.ts
const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
const response = await chrome.tabs.sendMessage(tab.id!, {
  type: "UPDATE_UI",
  data: { theme: "dark" },
});
```

### 型安全なメッセージング

```typescript
// types/messages.ts
type MessageMap = {
  GET_DATA: { request: { key: string }; response: { value: string } };
  SET_DATA: { request: { key: string; value: string }; response: void };
};

type MessageType = keyof MessageMap;

async function sendMessage<T extends MessageType>(
  type: T,
  payload: MessageMap[T]["request"]
): Promise<MessageMap[T]["response"]> {
  return chrome.runtime.sendMessage({ type, payload });
}

// 使用
const result = await sendMessage("GET_DATA", { key: "settings" });
```

---

## ストレージパターン

### 型安全なストレージラッパー

```typescript
// utils/storage.ts
interface StorageSchema {
  settings: {
    theme: "light" | "dark";
    notifications: boolean;
  };
  lastSync: number;
}

export async function getStorage<K extends keyof StorageSchema>(
  key: K
): Promise<StorageSchema[K] | undefined> {
  const result = await chrome.storage.local.get(key);
  return result[key];
}

export async function setStorage<K extends keyof StorageSchema>(
  key: K,
  value: StorageSchema[K]
): Promise<void> {
  await chrome.storage.local.set({ [key]: value });
}

// 使用
const settings = await getStorage("settings");
await setStorage("settings", { theme: "dark", notifications: true });
```

### リアクティブストレージ（React）

```typescript
// hooks/useStorage.ts
import { useState, useEffect } from "react";

export function useStorage<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(defaultValue);

  useEffect(() => {
    // 初期値を読み込み
    chrome.storage.local.get(key).then((result) => {
      if (result[key] !== undefined) {
        setValue(result[key]);
      }
    });

    // 変更を監視
    const listener = (
      changes: { [key: string]: chrome.storage.StorageChange },
      areaName: string
    ) => {
      if (areaName === "local" && changes[key]) {
        setValue(changes[key].newValue);
      }
    };

    chrome.storage.onChanged.addListener(listener);
    return () => chrome.storage.onChanged.removeListener(listener);
  }, [key]);

  const updateValue = async (newValue: T) => {
    await chrome.storage.local.set({ [key]: newValue });
    setValue(newValue);
  };

  return [value, updateValue] as const;
}

// 使用
function SettingsComponent() {
  const [theme, setTheme] = useStorage("theme", "light");
  return <button onClick={() => setTheme("dark")}>Dark Mode</button>;
}
```

---

## Content Script パターン

### Shadow DOM でスタイル分離

```typescript
// content.ts
export default defineContentScript({
  matches: ["<all_urls>"],
  main() {
    // Shadow DOM でホストページのスタイルから分離
    const container = document.createElement("div");
    const shadow = container.attachShadow({ mode: "closed" });

    shadow.innerHTML = `
      <style>
        .ext-panel { /* スタイル */ }
      </style>
      <div class="ext-panel">
        <!-- UI -->
      </div>
    `;

    document.body.appendChild(container);
  },
});
```

### WXT の createShadowRootUi

```typescript
// content.ts
import { createShadowRootUi } from "wxt/client";

export default defineContentScript({
  matches: ["<all_urls>"],
  cssInjectionMode: "ui",
  async main(ctx) {
    const ui = await createShadowRootUi(ctx, {
      name: "my-extension-ui",
      position: "inline",
      anchor: "body",
      onMount: (container) => {
        const root = createRoot(container);
        root.render(<App />);
        return root;
      },
      onRemove: (root) => {
        root.unmount();
      },
    });
    ui.mount();
  },
});
```

### ページコンテキストでの実行

```typescript
// ページのグローバル変数にアクセスする必要がある場合
export default defineContentScript({
  matches: ["<all_urls>"],
  world: "MAIN", // ページコンテキストで実行
  main() {
    // window オブジェクトはページと共有
    console.log(window.somePageVariable);
  },
});
```

---

## ブラウザ自動操作パターン

### ref 番号システム

DOM要素に一意の ref 番号を付与し、LLMが確実に要素を特定できるようにする。

```typescript
// DOM解析でref番号を付与
function assignRefNumbers() {
  const interactiveElements = document.querySelectorAll(
    'button, a, input, select, [role="button"], [role="link"], [role="checkbox"]'
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

### ボット検出回避

```typescript
// ループ間に3-5秒のランダム待機
async function humanLikeDelay() {
  const waitTime = 3000 + Math.random() * 2000;
  await new Promise((resolve) => setTimeout(resolve, waitTime));
}

// マウス移動をシミュレート
async function humanLikeClick(element: HTMLElement) {
  // ホバーイベント
  element.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
  await new Promise((resolve) => setTimeout(resolve, 100 + Math.random() * 200));

  // クリック
  element.click();
}
```

---

## Service Worker パターン

### 長時間処理の分割

```typescript
// 30秒制限を回避するため、処理を分割
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "LONG_TASK") {
    // 即座にレスポンスを返す
    sendResponse({ status: "started" });

    // バックグラウンドで処理を継続
    processInChunks(message.data);

    return false; // 同期レスポンス
  }
});

async function processInChunks(data: any[]) {
  const CHUNK_SIZE = 100;

  for (let i = 0; i < data.length; i += CHUNK_SIZE) {
    const chunk = data.slice(i, i + CHUNK_SIZE);
    await processChunk(chunk);

    // 進捗を保存
    await chrome.storage.session.set({ progress: i + CHUNK_SIZE });
  }

  // 完了通知
  await chrome.runtime.sendMessage({ type: "TASK_COMPLETE" });
}
```

### Keep-Alive パターン

```typescript
// 定期的にウェイクアップ
chrome.alarms.create("keepAlive", { periodInMinutes: 0.5 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "keepAlive") {
    // セッションストレージをチェック
    chrome.storage.session.get("pendingTasks").then((result) => {
      if (result.pendingTasks?.length > 0) {
        processPendingTasks(result.pendingTasks);
      }
    });
  }
});
```

---

## スクリーンショットパターン

### 現在のタブをキャプチャ

```typescript
// background.ts
async function captureTab(): Promise<string> {
  const dataUrl = await chrome.tabs.captureVisibleTab(undefined, {
    format: "png",
  });
  return dataUrl;
}

// 使用（権限: activeTab または tabs + host_permissions）
chrome.action.onClicked.addListener(async (tab) => {
  const screenshot = await captureTab();
  // Base64 データURL が返る
});
```

### フルページキャプチャ

```typescript
// Content Script でスクロールしながらキャプチャ
async function captureFullPage(): Promise<string[]> {
  const screenshots: string[] = [];
  const viewportHeight = window.innerHeight;
  const totalHeight = document.documentElement.scrollHeight;

  for (let y = 0; y < totalHeight; y += viewportHeight) {
    window.scrollTo(0, y);
    await new Promise((resolve) => setTimeout(resolve, 100));

    const screenshot = await chrome.runtime.sendMessage({ type: "CAPTURE" });
    screenshots.push(screenshot);
  }

  return screenshots;
}
```

---

## 外部リソース

- [WXT Messaging](https://wxt.dev/guide/messaging.html)
- [WXT Content Script UI](https://wxt.dev/guide/content-script-ui.html)
- [Chrome Extension Examples](https://github.com/nicolo-ribaudo/nicolo-ribaudo.github.io/issues/14)
