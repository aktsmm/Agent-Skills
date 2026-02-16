# テストガイド

ブラウザ拡張機能のテスト戦略（Vitest + Playwright）。

---

## テスト戦略

| テスト種別     | ツール     | 対象                                    |
| -------------- | ---------- | --------------------------------------- |
| ユニットテスト | Vitest     | ユーティリティ、ロジック、状態管理      |
| 統合テスト     | Vitest     | コンポーネント、Chrome API モック       |
| E2Eテスト      | Playwright | 拡張機能全体、実際のブラウザ操作        |

---

## Vitest セットアップ

### インストール

```bash
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom
```

### 設定

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["**/*.test.ts", "**/*.test.tsx"],
    globals: true,
    setupFiles: ["./test/setup.ts"],
  },
});
```

### セットアップファイル

```typescript
// test/setup.ts
import "@testing-library/jest-dom";

// Chrome API モック
const chromeMock = {
  storage: {
    local: {
      get: vi.fn(),
      set: vi.fn(),
    },
    sync: {
      get: vi.fn(),
      set: vi.fn(),
    },
    onChanged: {
      addListener: vi.fn(),
    },
  },
  runtime: {
    sendMessage: vi.fn(),
    onMessage: {
      addListener: vi.fn(),
    },
  },
  tabs: {
    query: vi.fn(),
    sendMessage: vi.fn(),
  },
};

vi.stubGlobal("chrome", chromeMock);
```

### テスト例

```typescript
// utils/storage.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { saveSettings, getSettings } from "./storage";

describe("Storage Utils", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should save settings to local storage", async () => {
    const settings = { theme: "dark" };
    await saveSettings(settings);

    expect(chrome.storage.local.set).toHaveBeenCalledWith({ settings });
  });

  it("should get settings from local storage", async () => {
    vi.mocked(chrome.storage.local.get).mockResolvedValue({
      settings: { theme: "light" },
    });

    const result = await getSettings();

    expect(result).toEqual({ theme: "light" });
  });
});
```

---

## React コンポーネントテスト

```typescript
// components/Popup.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Popup } from "./Popup";

describe("Popup Component", () => {
  it("should render correctly", () => {
    render(<Popup />);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("should toggle theme on button click", async () => {
    render(<Popup />);

    const button = screen.getByRole("button", { name: /toggle theme/i });
    fireEvent.click(button);

    expect(chrome.storage.local.set).toHaveBeenCalled();
  });
});
```

---

## Playwright E2E テスト

### インストール

```bash
npm install -D @playwright/test
npx playwright install chromium
```

### 設定

```typescript
// playwright.config.ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  use: {
    headless: false, // 拡張機能テストは headless: false 必須
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
});
```

### 拡張機能読み込み

```typescript
// e2e/fixtures.ts
import { test as base, chromium, type BrowserContext } from "@playwright/test";
import path from "path";

export const test = base.extend<{
  context: BrowserContext;
  extensionId: string;
}>({
  context: async ({}, use) => {
    const pathToExtension = path.join(__dirname, "../.output/chrome-mv3");
    const context = await chromium.launchPersistentContext("", {
      headless: false,
      args: [
        `--disable-extensions-except=${pathToExtension}`,
        `--load-extension=${pathToExtension}`,
      ],
    });
    await use(context);
    await context.close();
  },
  extensionId: async ({ context }, use) => {
    // 拡張機能のService Worker URLから ID を取得
    let [background] = context.serviceWorkers();
    if (!background) {
      background = await context.waitForEvent("serviceworker");
    }
    const extensionId = background.url().split("/")[2];
    await use(extensionId);
  },
});

export const expect = test.expect;
```

### E2E テスト例

```typescript
// e2e/popup.spec.ts
import { test, expect } from "./fixtures";

test("popup should open and display content", async ({
  context,
  extensionId,
}) => {
  // ポップアップページを開く
  const popupPage = await context.newPage();
  await popupPage.goto(`chrome-extension://${extensionId}/popup.html`);

  // 要素を確認
  await expect(popupPage.locator("h1")).toContainText("My Extension");
});

test("content script should inject into page", async ({ context }) => {
  const page = await context.newPage();
  await page.goto("https://example.com");

  // Content Script が注入した要素を確認
  const injectedElement = page.locator("[data-extension-injected]");
  await expect(injectedElement).toBeVisible();
});
```

### サイドパネルテスト

```typescript
// e2e/sidepanel.spec.ts
import { test, expect } from "./fixtures";

test("side panel should display", async ({ context, extensionId }) => {
  // サイドパネルページを直接開く（実際のサイドパネル操作は制限あり）
  const page = await context.newPage();
  await page.goto(`chrome-extension://${extensionId}/sidepanel.html`);

  await expect(page.locator("main")).toBeVisible();
});
```

---

## CI/CD 設定

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - run: npm ci

      - name: Run unit tests
        run: npm run test

      - name: Build extension
        run: npm run build

      - name: Install Playwright
        run: npx playwright install chromium

      - name: Run E2E tests
        run: npm run test:e2e
        env:
          # E2Eテストは headless: false が必要なため xvfb を使用
          DISPLAY: ":99"

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## テスト Tips

### Chrome API の詳細モック

```typescript
// 詳細なモック設定
vi.mocked(chrome.storage.local.get).mockImplementation(async (keys) => {
  if (keys.includes("settings")) {
    return { settings: { theme: "dark" } };
  }
  return {};
});
```

### 非同期処理のテスト

```typescript
// メッセージング のテスト
it("should handle message response", async () => {
  vi.mocked(chrome.runtime.sendMessage).mockResolvedValue({ success: true });

  const result = await sendAction("doSomething");

  expect(result.success).toBe(true);
});
```

---

## 外部リソース

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
