# Copilot Cloud Agent CI/CD Pitfalls

GitHub Actions で Copilot Cloud Agent の自動 PR パイプラインを組むときの落とし穴と対策。

## Token Anti-Recursion

GitHub App トークン（Copilot Cloud Agent 含む）で作成・push した PR は、`pull_request` イベントで後続ワークフローをトリガーしない。GitHub の再帰防止ルール。

- `GITHUB_TOKEN` でも同様
- `pull_request_target` は制限を受けない

### 対策

後続ワークフロー（validate、auto-merge 等）は `pull_request_target` をトリガーにする。

```yaml
on:
  pull_request_target:
    types: [opened, synchronize, reopened, ready_for_review, edited]
```

**注意**: `pull_request_target` はベースブランチのワークフローコードで実行される。fork からの PR でコード実行すると危険なため、同一リポジトリ制約を付ける。

```yaml
jobs:
  validate:
    if: github.event.pull_request.head.repo.full_name == github.repository
```

### 参照

- [GitHub Docs: Automatic token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [GitHub Docs: pull_request_target](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#pull_request_target)

## Self-Healing Reconcile Pattern

自動生成 PR パイプラインでは、チェーンの途中が壊れると PR と issue が stuck する。スケジュール実行の reconcile ワークフローで自己回復させる。

### 回復対象

| 状態 | 条件 | アクション |
|---|---|---|
| **stuck PR** | open, not draft, 条件合致, 2h+ 経過 | squash merge + issue close |
| **コンフリクト PR** | merge 失敗, 24h+ 経過 | PR close + issue close |
| **孤立 issue** | 対応 PR なし, 48h+ 経過 | issue close |
| **重複 PR** | 同一トピックに複数 PR | 古い方を close |

### 設計ポイント

- merge 前にファイル allowlist を検証する（auto-merge と同じ基準）
- `needs-human-review` ラベル付き PR はスキップする
- merge 成功後に pages deploy を dispatch する
- `Closes #XX` パターンを PR body から抽出して linked issue を閉じる
- 閉じた PR/issue にはコメントで理由を残す
