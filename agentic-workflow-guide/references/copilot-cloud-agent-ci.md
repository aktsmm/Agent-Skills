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

自動生成 PR パイプラインでは、チェーンの途中が壊れると PR と issue が stuck する。

- **in-band 回復**: validate failure の直後に PR コメントで修正指示を返し、Copilot に再修正させる
- **scheduled reconcile**: それでも取りこぼした stuck PR / 孤立 issue を定期ジョブで掃除する

`rerun failed workflow` だけでは直らない。content / policy failure は、**失敗理由に応じた修正指示**を PR 上に返す設計が必要。

### 回復対象

| 状態                | 条件                                | アクション                 |
| ------------------- | ----------------------------------- | -------------------------- |
| **stuck PR**        | open, not draft, 条件合致, 2h+ 経過 | squash merge + issue close |
| **コンフリクト PR** | merge 失敗, 24h+ 経過               | PR close + issue close     |
| **孤立 issue**      | 対応 PR なし, 48h+ 経過             | issue close                |
| **重複 PR**         | 同一トピックに複数 PR               | 古い方を close             |

### 設計ポイント

- merge 前にファイル allowlist を検証する（auto-merge と同じ基準）
- `needs-human-review` ラベル付き PR はスキップする
- merge 成功後に pages deploy を dispatch する
- PR body を正規化し、`Generated from data/events/YYYY-MM-DD.json` と `Closes #XX` を必ず入れる
- `Closes #XX` パターンを PR body から抽出して linked issue を閉じる
- 閉じた PR/issue にはコメントで理由を残す

### In-Band Self-Heal Rules

- validate failure 時は、失敗ステップ名だけでなく**修正ルール**を PR コメントに書く
- self-heal コメント後に Copilot reviewer を再要求し、再修正の起点を明示する
- 同じ原因の自動修正は最大 3 回まで。超えたら PR を close し、linked issue / PR の両方に `needs-human-review` を付ける
- `already gave up` 状態では重複コメントを増やさない
- PR だけでなく linked issue にも escalation コメントを残し、`なぜ blocked なのか` を issue 単体で読めるようにする

### Metadata and Closing Discipline

- generated PR の title / body は opened / synchronize 時に正規化する
- linked issue を閉じたいなら、merge job 側の best effort close だけに頼らず、PR body に closing reference を注入する
- source marker と closing reference が missing のままだと、PR merge 後に issue が残留しやすい

### Human-Review Block Discipline

- `needs-human-review` が付いた linked issue は、authoring workflow 側で **自動 assignment と shepherd を止める**
- blocked issue を定期実行や手動再実行で勝手に再開しない
- issue のラベル再設定時に `needs-human-review` を消さない
- 再開条件は明示する。例: `ラベルを外すと再度自動化できます`

### Resume Semantics

- blocked issue を再開するとき、Copilot が assignee に残っていても `already assigned` だけでは不十分
- **対応する open generated PR が無い**なら、assignment を再実行して作業を再開する
- open PR が既にある場合だけ `already assigned / in progress` と判定する

### Duplicate PR Canonicalization

- 同一トピック（例: 同じ date key）で generated PR が複数 open になったら、**最新 1 本を canonical** にする
- stale duplicate PR は comment を残して自動 close する
- canonical PR の source marker / closing reference を SSOT にする

### Failure-Specific Feedback

- build failure は `build を直して` だけでは弱い。失敗している policy を具体化する
- 例: pages build が published output 内の generic fallback copy を検出して落ちるなら、`generic な仮置き文言を対象更新に即した運用影響へ書き換える` まで指示する
- self-heal コメントには validate run へのリンクを残し、人が読むときも追跡できるようにする
