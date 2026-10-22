---
name: sync-copilot-customizations
description: "~/.copilot の instructions と agents を、公開 repo（Agent-Customization）の .github へ安全に同期する。syncToGlobal の分類と機密監査を通し、公開前に差分を提示して承認を取る。skill は対象外（private skills repo の retro / sync 系を使う）"
argument-hint: "対象（instructions / agents / 両方）、mode（review-only / apply）、対象 repo path（省略時は環境変数）"
disable-model-invocation: true
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---
<!-- syncToGlobal: true -->
<!-- author: aktsmm -->
<!-- repository: https://github.com/aktsmm/Agent-Customization -->
<!-- license: CC BY-NC-SA 4.0 -->
<!-- copyright: Copyright (c) 2025 aktsmm -->

# sync copilot customizations

`~/.copilot` の個人 instructions / agents を、公開 repo の `.github/` へミラーする。`~/.copilot` は作業コピーで、正本は公開 repo。この skill 自身は同期対象外。

## Scope

| 同期元 | 同期先（公開 repo） |
| --- | --- |
| `$HOME/.copilot/instructions/*.instructions.md` | `.github/instructions/<category>/`（repo 側の既存 mirror path） |
| `$HOME/.copilot/agents/*.agent.md` | `.github/agents/` |

- 同期元は 1 フォルダごと（再帰しない）。`instructions` と `agents` は別々に実行する
- 対象外: `~/.copilot/copilot-instructions.md`、skills（private skills repo の retro / sync 系が担当）、`mcp-config.json` などの設定ファイル
- repo / GitHub repo は `$env:SYNC_USER_CUSTOMIZATIONS_REPO_DIR` / `$env:SYNC_USER_CUSTOMIZATIONS_GITHUB_REPO`。未設定または path 不在なら確認する

## Classification

| ラベル | 条件 | 扱い |
| --- | --- | --- |
| `public-safe` | `syncToGlobal: true` | 監査通過で同期対象 |
| `local-only` | `syncToGlobal: false` | 同期しない |
| `ignored` | `.github/.sync-ignore` に載っている | 同期しない |
| `needs-review` | `syncToGlobal` が無い、または同期先が決まらない（複数 / 候補なし） | 停止して確認。新規 category path は作らない |

## Gates

- 既定は公開前に承認を取る。dry-run の結果（追加・更新・削除候補、分類、監査、予定差分）を提示し、承認後だけ `-Apply` する。公開 repo への push を承認なしで行わない
- `review-only` / `確認だけ` / `dry-run` では dry-run だけで終える
- 監査は push 前に 1 回。秘密鍵、password / API key / client secret / 接続文字列 / refresh token、ラベル付き GUID、メールアドレスを検出する。実値らしいヒットが出たら書き込まず停止し、ファイル・検出種別・件数だけ報告する。値は表示しない
- 監査の通過だけでは公開可否は決まらない。個人アカウント、tenant / subscription ID、社内情報、端末固有値、個人の承認設定を含むファイルは、`syncToGlobal: false` でなければ停止して確認する
- 削除候補は報告のみ。repo 専用資産と古い mirror を区別できないため、自動削除しない。削除は確認して別 commit で行う
- 既存の未コミット差分はユーザー所有として扱い、混ぜない。分離できなければ停止する
- 破壊的操作（`git reset --hard` など）をしない。一時ファイルは OS の temp に置き、完了前に削除する

## Workflow

1. 準備: repo の branch / origin（GitHub repo 名と照合）/ ahead-behind / dirty を確認する。script が無い・古いときは、clean を確認して fetch + fast-forward してから実行する（手作業で再実装しない）
2. dry-run: 引数なしで実行する。`-Source` を必ず明示する（script の既定値は旧 `%APPDATA%\Code\User\prompts` で、空のフォルダ）

```powershell
& "$env:SYNC_USER_CUSTOMIZATIONS_REPO_DIR\scripts\Sync-UserCustomizations.ps1" -Source "$HOME\.copilot\instructions"
& "$env:SYNC_USER_CUSTOMIZATIONS_REPO_DIR\scripts\Sync-UserCustomizations.ps1" -Source "$HOME\.copilot\agents"
```

3. 確認: 結果を提示する。`-Source` に指定したフォルダ以外の repo 資産は「削除候補（報告のみ）」に並ぶが、同期元が違うだけなので削除しない。`needs-review` と実値らしい監査ヒットがあれば、ここで止める
4. 承認後、同じコマンドに `-Apply` を付けて実行する。変更候補だけを明示パスで stage して commit・push し、remote == HEAD まで script が検証する。push が rejected なら fetch して ahead-behind と変更 path を確認し、競合がなければ取り込んでから再送する
5. 完了確認: remote SHA = HEAD、clean、除外ファイルが公開されていないことを確認する。中断後は既存 commit と remote を照合し、反映済みの操作を再実行しない

## Report

```
Summary:   結論を 1-3 行
Synced:    追加 / 更新
Excluded:  ファイル名 + 理由（local-only / ignored / needs-review）
Audit:     結果 + ヒット有無（値は書かない）
Commit:    SHA + メッセージ
Remote:    GitHub URL
Pending:   削除候補（報告のみ）、未同期の既存差分
```

不明点は最小限だけ確認し、それ以外は完了まで進める。
