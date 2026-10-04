# Copilot Cloud Agent CI/CD Pitfalls

GitHub Actions で Copilot cloud agent の自動 PR パイプラインを組むときの落とし穴と対策。

## Token Anti-Recursion

後続ワークフローが自動で走らない原因は 2 つある。

- `GITHUB_TOKEN` による event は、`workflow_dispatch` / `repository_dispatch` を除き新しい workflow run を作らない（`pull_request_target` も同様）
- Copilot cloud agent が PR に push しても、既定では GitHub Actions workflow は走らず、write 権限者の **Approve and run workflows** が必要。リポジトリ設定の **Require approval for workflow runs** を無効化すると自動実行できるが、未レビューのコードが secrets / 書き込み権限に触れるリスクを受け入れることになる

### 対策

後続ワークフロー（validate、auto-merge 等）は `pull_request_target` をトリガーにする運用実績がある。ただし上記の承認ゲートを回避できるかは公式に未確認のため、導入時に Copilot の push で実際に起動するか実測する。

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

### `workflow_run` 連携時の PR 解決

`pull_request_target` を起点にした workflow を、別 workflow の `workflow_run` で受ける場合、`context.payload.workflow_run.pull_requests` が空になることがある。

- `pull_requests[0].number` を前提にしない
- `workflow_run.head_branch` から open PR を逆引きする fallback を持つ

```js
let pullRequests = context.payload.workflow_run.pull_requests || [];
if (pullRequests.length === 0 && context.payload.workflow_run.head_branch) {
  const { data: prs } = await github.rest.pulls.list({
    owner: context.repo.owner,
    repo: context.repo.repo,
    state: "open",
    head: `${context.repo.owner}:${context.payload.workflow_run.head_branch}`,
    per_page: 1,
  });
  pullRequests = prs;
}
```

### `pull_request_target` で PR head を実行する場合の注意

`pull_request_target` は base branch の workflow 定義で動くが、checkout を PR head SHA に向けると **PR 側の script / package.json / build code を実行する**。

- same-repo guard を必須にする
- 実行を許す script / 生成物の allowlist を絞る
- fork PR や不特定 contributor を対象に同じ設計を使わない

### 参照

- [GitHub Docs: Automatic token authentication](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- [GitHub Docs: pull_request_target](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target)
- [GitHub Docs: Configuring settings for Copilot cloud agent](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/configuring-agent-settings)

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
- merge 後の副作用（deploy、release、通知）は **1 workflow に責務を寄せる**。`pull_request_target: closed` など別 workflow が拾うなら、merge job 側で同じ dispatch を重複実行しない
- PR body を正規化し、`Generated from data/events/YYYY-MM-DD.json` と `Closes #XX` を必ず入れる
- `Closes #XX` パターンを PR body から抽出して linked issue を閉じる
- 閉じた PR/issue にはコメントで理由を残す

### Generated Data Invariants

collector が自動修復を持っていても、**壊れた生成物が main に入らない guard** を別に置く。

- `collect` 後に generated data validator を実行する
- generated PR validation でも同じ validator を実行する
- validator は source 実装ではなく**生成済み artifact の不変条件**を見る

例:

- 同じ stable article URL が複数の日次 JSON に出ない
- source marker や closing reference のような canonical metadata が欠落しない
- generated output に既知の不正状態（generic fallback、同一記事の日跨ぎ重複など）が残らない

重要なのは、`collect can repair` だけで終わらず、`repair に失敗した run は CI を落とす` まで入れること。

### Generated Output Diff Targets

生成物 workflow では、`git diff --quiet`、`git add`、canonical drift check の対象を必ず一致させる。

- collector が書き換える generated artifact を一覧化する（例: data, summaries, drafts, translation/summary cache）
- no-change 判定、commit staging、PR auto-fix、final drift check の対象を同じ集合にする
- cache-only drift も publish される品質に影響するなら generated output として扱う
- この集合を workflow invariant validator で固定し、対象漏れを CI で落とす
- workflow / validator / runbook 変更時は、同じ invariant validator を GitHub Actions でも実行する

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
