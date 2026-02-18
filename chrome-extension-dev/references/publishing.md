# Chrome Web Store 公開ガイド

拡張機能の公開準備とストア提出プロセス。

---

## 公開前チェックリスト

### 必須項目

- [ ] マニフェストの `name`, `version`, `description` が正確
- [ ] アイコン（16x16, 48x48, 128x128 px）が用意されている
- [ ] プライバシーポリシーが用意されている（ユーザーデータを扱う場合）
- [ ] 権限が最小限に設定されている
- [ ] 動作テストが完了している

### 推奨項目

- [ ] スクリーンショット（1280x800 または 640x400）を用意
- [ ] プロモーションタイル画像（440x280 small、920x680 large）
- [ ] 詳細な説明文（多言語対応推奨）
- [ ] カテゴリが適切に選択されている

---

## ZIP パッケージ作成

### WXT の場合

```bash
# プロダクションビルド
npm run build

# ZIP 生成
npm run zip
# → .output/[name]-[version]-chrome.zip が生成される
```

### 手動の場合

```powershell
# PowerShell
Compress-Archive -Path ".output/chrome-mv3/*" -DestinationPath "extension.zip"
```

---

## Chrome Web Store Developer Dashboard

### アカウント設定

1. [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole) にアクセス
2. 初回は $5 の登録料が必要
3. デベロッパーアカウントを設定

### 新規アイテム追加

1. 「新しいアイテム」をクリック
2. ZIP ファイルをアップロード
3. ストアリスティング情報を入力:
   - 詳細説明
   - カテゴリ
   - 言語
   - スクリーンショット
   - プライバシーポリシー URL

### 権限の正当化

ストア審査では、使用する各権限の正当化が求められる。

| 権限           | 正当化例                                               |
| -------------- | ------------------------------------------------------ |
| `tabs`         | タブのURL/タイトルを表示するため                       |
| `<all_urls>`   | すべてのウェブサイトでコンテンツスクリプトを実行するため |
| `storage`      | ユーザー設定を保存するため                             |
| `cookies`      | ログイン状態を確認するため                             |
| `activeTab`    | ユーザーがクリックした時のみ現在のタブにアクセスするため |

---

## 審査プロセス

### 審査期間

- 通常: 1〜3 営業日
- 複雑な権限を使用する場合: 1〜2 週間

### よくあるリジェクト理由

| 理由                     | 対策                                       |
| ------------------------ | ------------------------------------------ |
| 権限の過剰要求           | 必要最小限の権限に変更                     |
| プライバシーポリシー不備 | ユーザーデータの取り扱いを明記             |
| 機能の説明不足           | ストア説明を詳細化                         |
| リモートコード           | すべてのコードをバンドルに含める           |
| 誤解を招く説明           | 正確な機能説明に修正                       |
| 低品質のUI               | UIを改善                                   |

---

## アップデート公開

### バージョン更新

```typescript
// wxt.config.ts
export default defineConfig({
  manifest: {
    version: "1.1.0", // バージョンを更新
  },
});
```

### 更新手順

1. `npm run zip` で新しいZIPを生成
2. Developer Dashboard で該当アイテムを選択
3. 「パッケージ」タブで新しいZIPをアップロード
4. 変更履歴を入力
5. 送信して審査を待つ

---

## 自動パブリッシング

### WXT Auto-Publishing

```bash
# Chrome Web Store API を設定
npm install -D chrome-webstore-upload-cli

# 環境変数設定
export EXTENSION_ID="your-extension-id"
export CLIENT_ID="your-client-id"
export CLIENT_SECRET="your-client-secret"
export REFRESH_TOKEN="your-refresh-token"

# アップロード＆公開
npx chrome-webstore-upload upload --source .output/*-chrome.zip --auto-publish
```

### GitHub Actions 自動公開

```yaml
# .github/workflows/publish.yml
name: Publish to Chrome Web Store

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - run: npm ci
      - run: npm run build
      - run: npm run zip

      - name: Upload to Chrome Web Store
        uses: mnao305/chrome-extension-upload@v5.0.0
        with:
          file-path: .output/*-chrome.zip
          extension-id: ${{ secrets.EXTENSION_ID }}
          client-id: ${{ secrets.CLIENT_ID }}
          client-secret: ${{ secrets.CLIENT_SECRET }}
          refresh-token: ${{ secrets.REFRESH_TOKEN }}
```

---

## 非公開配布

### 開発者モード（ローカル）

1. `chrome://extensions` を開く
2. 「デベロッパーモード」を有効化
3. 「パッケージ化されていない拡張機能を読み込む」
4. ビルドフォルダを選択

### CRX パッケージ（社内配布）

```bash
# Chrome で CRX を生成
# chrome://extensions → パック拡張機能
# または
npx crx pack .output/chrome-mv3 -o extension.crx
```

---

## 外部リソース

- [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
- [Publishing in the Chrome Web Store](https://developer.chrome.com/docs/webstore/publish)
- [Chrome Web Store API](https://developer.chrome.com/docs/webstore/api)
