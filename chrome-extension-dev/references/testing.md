# テストガイド

ブラウザ拡張機能のテスト戦略（Vitest + Playwright）。

| テスト種別     | ツール     | 対象                                    |
| -------------- | ---------- | --------------------------------------- |
| ユニットテスト | Vitest     | ユーティリティ、ロジック、状態管理      |
| 統合テスト     | Vitest     | コンポーネント、拡張 API を使うロジック |
| E2Eテスト      | Playwright | 拡張機能全体、実際のブラウザ操作        |

## Vitest（WXT）

`chrome` を手書きで `vi.stubGlobal` するより、WXT の Vitest プラグインを使う（[Unit Testing](https://wxt.dev/guide/essentials/unit-testing)）。

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import { WxtVitest } from "wxt/testing/vitest-plugin";

export default defineConfig({
  plugins: [WxtVitest()],
});
```

- `browser` が `@webext-core/fake-browser` のインメモリ実装で polyfill されるので、`storage` などはモックせずに実際の挙動で検証できる。テストごとに `fakeBrowser.reset()`（`wxt/testing/fake-browser`）。
- `wxt.config.ts` の Vite 設定、auto-import、`import.meta.env.BROWSER` などのグローバル、`@/*` エイリアスも反映される。
- `#imports` 由来の関数をモックするときは実パスを指定する（例: `vi.mock("wxt/utils/inject-script")`）。実パスは `.wxt/types/imports-module.d.ts` で確認する（無ければ `wxt prepare`）。
- fake browser は実ブラウザの制約（シリアライズ、権限、SW 終了）を再現しない。境界は E2E で確認する（下記）。

## Playwright E2E

- 拡張は `launchPersistentContext` でのみ読み込める。Chrome / Edge 本体はサイドロード用フラグを削除済みなので、Playwright 同梱の Chromium を使う。
- `channel: "chromium"` を指定すれば headless でも拡張が動く（headed も可）。
- 拡張 ID は SW の URL から取る（`context.serviceWorkers()` が空なら `waitForEvent("serviceworker")`）。
- MV3 SW は約 30 秒で停止・再起動されるが、Playwright の Worker ハンドルは再起動をまたいで有効。停止の瞬間に実行中だった `evaluate()` は `Service worker restarted` で失敗し得る。

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
      channel: "chromium",
      args: [
        `--disable-extensions-except=${pathToExtension}`,
        `--load-extension=${pathToExtension}`,
      ],
    });
    await use(context);
    await context.close();
  },
  extensionId: async ({ context }, use) => {
    let [sw] = context.serviceWorkers();
    if (!sw) sw = await context.waitForEvent("serviceworker");
    await use(sw.url().split("/")[2]);
  },
});
export const expect = test.expect;
```

- ポップアップやサイドパネルは `chrome-extension://<id>/<page>.html` を直接開いて検証する。実際のサイドパネル UI の開閉は自動化に制約がある。
- CI では `npm run build` の後に E2E を走らせ、失敗時は `playwright-report/` を artifact として保存する。

## WXT Typecheck

WXT の生成型を含めた型検査は、root `tsconfig.json` や `.wxt/tsconfig.json` だけでは不足することがある。専用 `tsconfig.typecheck.json` を用意し、`.wxt/wxt.d.ts` と必要な browser API 型を include する。

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "noEmit": true,
    "types": ["wxt/client", "chrome"],
    "jsx": "react-jsx"
  },
  "include": ["**/*.ts", "**/*.tsx", ".wxt/wxt.d.ts"]
}
```

`entrypoints/` 配下に補助 `.d.ts` を置くと WXT が entrypoint と誤認することがあるため、shim は root か型専用フォルダに置く。

## テスト Tips

### 実ブラウザ境界のテスト

- `chrome.scripting.executeScript({ args })` に `undefined` を渡すと実 MV3 では引数のシリアライズで失敗し得る。mock の成功だけで完了にせず、未承認操作を含む実拡張テストで注入できることを確かめる。
- `chrome.downloads.download()` が返す ID は保存完了ではない。対象 ID の `onChanged` と初期 `search` で `complete` / `interrupted` を判定し、期限を設ける。E2E では保存本文と推奨ファイル名を確認し、一時ブラウザの GUID 名や汎用アイコンで利用者プロファイルの保存結果を判定しない。

---

## 外部リソース

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
