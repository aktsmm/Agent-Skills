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

## Release Gate

- 既存 tag に後続修正が入った場合、tag 付け替えではなく patch version を上げる。
- 公開前に `npm run test`, `npm run lint`, `npm run typecheck`, `npm run validate:bridge`, `npm audit --omit=dev`, `npm run zip` を通す。
- full `npm audit` が WXT 経由の dev-only 脆弱性を返す場合は、`--omit=dev` の runtime audit と分けて判断する。semver-major の WXT 更新は別サイクルで扱う。
- CLI stdout や success marker だけで gate 完了を判定しない。ZIP の存在、サイズ、更新時刻、checksum、プロセス残存なしを別経路で確認する。

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

| 権限         | 正当化例                                                 |
| ------------ | -------------------------------------------------------- |
| `tabs`       | タブのURL/タイトルを表示するため                         |
| `<all_urls>` | すべてのウェブサイトでコンテンツスクリプトを実行するため |
| `storage`    | ユーザー設定を保存するため                               |
| `cookies`    | ログイン状態を確認するため                               |
| `activeTab`  | ユーザーがクリックした時のみ現在のタブにアクセスするため |

---

## 審査プロセス

### 審査期間

- 通常: 1〜3 営業日
- 複雑な権限を使用する場合: 1〜2 週間

### よくあるリジェクト理由

| 理由                     | 対策                             |
| ------------------------ | -------------------------------- |
| 権限の過剰要求           | 必要最小限の権限に変更           |
| プライバシーポリシー不備 | ユーザーデータの取り扱いを明記   |
| 機能の説明不足           | ストア説明を詳細化               |
| リモートコード           | すべてのコードをバンドルに含める |
| 誤解を招く説明           | 正確な機能説明に修正             |
| 低品質のUI               | UIを改善                         |

---

## 商標セーフな命名 (公開後の takedown 対策)

審査通過後でも、商標権者の代理 (例: Microsoft 代理の Tracer `microsoft@tracer.ai`) が
Google 経由で商標侵害を申し立てると、7 日以内に是正しないと item が suspend される。

- 苦情が狙うのは **item の Title** に当たる箇所: manifest `name` / `action.default_title` /
  ストアリスティング名。ここから他社商標 (GITHUB, Copilot, Microsoft 等) を外す。
- `description` / README / keywords での **nominative な互換性言及** は許容
  (例: `Works with GitHub Copilot or local LLMs`)。エスカレートしたら description も中立化するが、
  Title 修正だけで suspend リスクは消える。
- 商標対応で **manifest `name` の内部 ID や設定キー prefix を変えない** —
  既存ユーザーのインストール / 設定が壊れる。変えるのは人間が見る Title 文字列だけ。
- リネーム後は全面 grep して、ビルド生成物 (`.output` の manifest、コンパイル済み JS) からも
  旧 Title が消えていることを確認する。
- ZIP 反映と **リスティング項目は別物**。Title だけ直して submit しても、CWS の
  **説明文の見出し / Privacy policy URL / Store icon / Screenshots 画像 / Website・Support URL**
  に旧名が残ったままだと再申し立ての火種になる。再申請前に Dashboard 上で全項目を点検する。
  Screenshots は画像内に写り込んだタブ title やパネル見出しも対象。新名で撮り直して差し替える。
- ストアの URL slug (`/detail/<slug>/<itemId>`) は Title 由来で **公開後に自動再生成**される
  (item ID は不変、旧 URL は redirect で生き続ける)。slug を直接変更する API は無いため、
  Title 中立化 + 審査通過後に新 slug を検証する。
- Dashboard の Screenshots スロットを自動操作する場合、削除はサムネイル hover で出るボタン、
  追加は drop zone の click → `expect_file_chooser` 経由が確実。`input[type=file]` への
  直接 `set_input_files` は隠し input に当たって反映されないことがある。
- ただし **UI 部品ごとに動作が違う**: Store icon (128×128) は `input[type=file]` への直接
  `set_input_files` が通る。Screenshots だけ drop zone + file chooser 必須。アップロード後は
  必ず thumbnail / preview の有無で反映を検証する (`SCREENS_AFTER_UP` が増えない＝失敗)。
- hover overlay を出すときは sticky header が pointer を奪う。`scroll_into_view_if_needed`
  + `window.scrollBy` で対象を viewport 中央 ~300px 下へ移動し、座標ベースの
  `page.mouse.move(cx, cy)` で hover してから click すると安定する。
- ダッシュボードを撮ったスクショには **publisher email / extension ID** が写る。
  証跡として残す画像（メール添付用など）は repo の `store-assets/evidence/` に隔離し、
  そのパスを `.gitignore` に追加して public repo に絶対に commit しない。

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

## Artifact Hygiene

- ZIP の中身を列挙し、`src/`, `tests/`, `.github/`, `.vscode/`, `store-assets/`, `*.map`, log が入っていないことを確認する。
- `publish-extension` は `.env.submit` を自動読込する。OAuth `invalid_grant` は refresh token 失効として扱い、同じ ZIP を保持したまま再認可後に再実行する。
- 再認可時の auth code や refresh token はチャットやログへ貼らず、ターミナルへ直接入力する。更新後は secret を表示せず token exchange の成功だけ確認する。
- live retry 前に `publish-extension --dry-run --chrome-zip <zip>` を通し、認証と設定だけ先に確認する。
- CWS publish が止まった場合でも、ZIP と SHA256 を GitHub Release に残して再開可能にする。
- 審査中、認証、権限、duplicate など外部状態で publish だけ止まる場合は、ZIP / SHA256 / version / commit / tag / upload の状態を分けて記録し、再開条件を明記する。
- ブロッカー解消後の再開では、**最新タグの ZIP を rollup 提出**する。ブロック時点の古い ZIP を蘇生せず、間に積まれた patch をまとめて出す（実例: v0.1.11→v0.1.15 で 4 版分を一括公開）。
- `publish-extension` が `400 "Publish condition not met: You may not edit or publish an item that is in review."` で失敗する場合は、前回の draft が審査キュー残留中。先に `?projection=DRAFT` で stuck している `crxVersion` を確認し、Dashboard UI から `more_vert` → 審査をキャンセル → 確認ダイアログで取り下げる。ステータスバッジが「公開済み」に戻り次第 `publish-extension` を再実行できる。
- publish 後の CWS API 確認は item endpoint に `?projection=DRAFT` を付ける。`crxVersion` が対象版で `itemError` が 0 件なら API 側の確認は通過扱いにし、`uploadState: NOT_FOUND` だけで失敗判定や再アップロードをしない。
- API 応答が疎または stale な場合、最終ステータスは Chrome Web Store Developer Dashboard で確認する。

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
