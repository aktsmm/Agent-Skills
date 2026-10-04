# Manifest V3 ガイド

MV3 の前提と、実装で踏みやすい制約だけをまとめる。マニフェストの基本構成と WXT 設定は SKILL.md と [WXT 公式ドキュメント](https://wxt.dev) を参照。

## MV2 の状況（2026-10 確認）

- Chrome 138（2025-07）で全チャネルの MV2 拡張が無効化され、再有効化不可。Chrome 139 で企業ポリシー `ExtensionManifestV2Availability` も削除。
- 2026-08-31 に残りの MV2 拡張は Chrome Web Store から削除済み。新規・更新は MV3 のみ。
- 出典: [Manifest V2 support timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)

## MV2 → MV3 主要変更点

| 機能                   | MV2                        | MV3                       |
| ---------------------- | -------------------------- | ------------------------- |
| バックグラウンド処理   | Background Pages           | **Service Workers**       |
| ネットワークリクエスト | webRequest（ブロッキング） | **declarativeNetRequest** |
| リモートコード         | 許可                       | **禁止**                  |
| コード実行             | `eval()` 許可              | **禁止**                  |
| CSP                    | 柔軟                       | **厳格化**                |

## Service Worker のライフサイクル

Chrome は次のいずれかで拡張 SW を終了する（[lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)）。

- 30 秒間イベントも拡張 API 呼び出しもない（Chrome 110+ は API 呼び出しでもタイマーがリセットされる）
- 1 つのイベント/API 呼び出しの処理が 5 分を超える
- `fetch()` の応答到着に 30 秒以上かかる

| 制約                   | 対処                                                                                                                   |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| グローバル変数が消える | `chrome.storage.session`（メモリ、10MB）か `storage.local` に保存。SW では `localStorage` 不可                         |
| 定期処理               | `chrome.alarms`（Chrome 120+ は最小 30 秒）。SW を無期限に延命する keep-alive は避け、終了されても再開できる設計にする |
| 長時間接続             | Chrome 116+ はアクティブな WebSocket の送受信でアイドルタイマーがリセットされる                                        |
| DOM が必要             | `chrome.offscreen`（詳細は [chrome-api.md](chrome-api.md#chromeoffscreen)）                                            |
| 動的コード             | `eval()` / リモートスクリプト不可。すべてバンドルする                                                                  |

- リスナーはトップレベルで同期的に登録する。`await` の後で登録すると SW 再起動時のイベントを取りこぼす。
- 起動時に storage から読み込む値は Promise で保持し、各ハンドラで `await` してから使う。

## 権限

- `host_permissions` と `permissions` は最小にし、ユーザー操作時だけでよい場合は `activeTab` を使う。
- 後から必要になる権限は `optional_permissions` / `optional_host_permissions` に置き、`chrome.permissions.request()` をユーザー操作の中で呼ぶ。
- 権限の追加はユーザーに再承認を求め、承認まで拡張が無効化されることがある。更新前に影響を確認する。

## MV3 移行時の一般的な問題

| 問題                                 | 原因                        | 解決策                            |
| ------------------------------------ | --------------------------- | --------------------------------- |
| バックグラウンドスクリプトが動かない | Background Page → SW 移行   | `background.service_worker`を使用 |
| ネットワーク操作が動かない           | webRequest ブロッキング廃止 | declarativeNetRequest に移行      |
| 外部スクリプトが読み込めない         | リモートコード禁止          | 全コードをバンドルに含める        |
| localStorage 使用不可                | SW で Web Storage API 不可  | `chrome.storage` に移行           |
| `eval()` エラー                      | 動的コード実行禁止          | 事前コンパイル                    |

## declarativeNetRequest

- 静的ルールは manifest の `declarative_net_request.rule_resources` で JSON ファイルを宣言し、`declarativeNetRequest` 権限を付ける。対象サイトへの host 権限が必要なアクション（redirect、header 変更）がある点に注意。
- ルール構文と上限は公式 [declarativeNetRequest](https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest) を参照。

## 外部リソース

- [Migrate to Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate)
- [Service Worker Lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)
