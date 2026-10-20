# Chrome Web Store 提出の自動化（API v2・サービスアカウント）

CWS への新版アップロードと審査提出を、ブラウザーのログインなしでコマンド化する手順。v1.1 の OAuth（refresh token）は 2026-10-15 に停止済みで使わない。公開前チェック・審査・ZIP 検査は [publishing.md](publishing.md) を参照する。

## 方式の選び方

| 状況 | 使う経路 |
| --- | --- |
| サービスアカウントを Dashboard に登録済み | API v2（既定。ログイン不要） |
| 未構築、またはトークン／権限エラー | 下記「構築」を行う。急ぎなら Dashboard 提出（ユーザーのログインが必要） |

## 構築（1 回だけ）

1. GCP プロジェクトで Chrome Web Store API を有効化する。
2. サービスアカウントを作る（プロジェクト権限なし・鍵ファイルは作らない）。
3. 自分のアカウントに、そのサービスアカウント限定で `roles/iam.serviceAccountTokenCreator` を付与する。反映に最大 1 分かかり、`IAM_PERMISSION_DENIED` は待って再試行する。
4. Dashboard の 設定 → サービス アカウント にそのメールを登録する。ユーザーのログインが要る唯一の手動工程なので、専用プロファイルのブラウザーで行う。

## 認証

短命トークンを gcloud の impersonation で取り、REST に渡す。

```
gcloud auth print-access-token --impersonate-service-account=<sa> --scopes=https://www.googleapis.com/auth/chromewebstore --project=<project>
```

- gcloud の既定プロジェクトが別物なら `--project` を明示し、グローバル設定は変えない。
- トークンは表示も保存もしない。有無は先頭が `ya29.` であることだけで確認する。
- `403 PERMISSION_DENIED` は SA の Dashboard 未登録か権限の反映待ち。

## エンドポイントと値

- `GET v2/publishers/{pub}/items/{item}:fetchStatus`
- `POST upload/v2/publishers/{pub}/items/{item}:upload`（本文は ZIP）
- `POST v2/publishers/{pub}/items/{item}:publish`
- `POST v2/publishers/{pub}/items/{item}:cancelSubmission`（破壊的なので承認後）
- `uploadState`: `SUCCEEDED | IN_PROGRESS | FAILED | NOT_FOUND`
- リビジョンの state: `PENDING_REVIEW | STAGED | PUBLISHED | PUBLISHED_TO_TESTERS | REJECTED | CANCELLED`

## 提出スクリプトの規則

- 既定は dry-run（ZIP の version・権限・混入ファイルの検査と、`fetchStatus` からの実行計画だけ）。変更は `--apply` のような明示フラグ時だけ。
- `PENDING_REVIEW` / `STAGED` 中、同一または旧 version、開発ファイル混入ではブロックする（終了コードで区別する）。`REJECTED` / `CANCELLED` は履歴なので止めない。
- 実機で未実行の経路（upload → publish）は、初回に応答を読み戻してから再実行の要否を決める。曖昧な結果で `--apply` を繰り返さず、先に `fetchStatus` を読む。

## Dashboard 提出（API が使えない間）

専用プロファイルのブラウザーを `--remote-debugging-port` 付きで起動し（既存セッションは使わない）、ログインだけユーザーに依頼する。

1. Package → 「新しいパッケージをアップロード」→ ダイアログの「ファイルを選択」（file chooser）→ ZIP を指定する。
2. Package でドラフトの version と権限を確認する。
3. 「審査のため送信」は Package タブにはなく、アップロード後に移る掲載情報タブのヘッダーにある。1 回押し、確認ダイアログ（自動公開 checkbox は既定のまま）を確定する。
4. ヘッダーのステータスバッジで「審査待ち」を確認する（トーストは過去の結果が残る）。
5. 終了後はそのブラウザーとプロファイルを削除する。

公開中の版は公開ページ（`chromewebstore.google.com/detail/<id>`）の manifest version からも確認できる。
