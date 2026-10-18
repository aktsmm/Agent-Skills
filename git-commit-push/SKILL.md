---
name: git-commit-push
description: "ディスク上の変更を作業単位でコミット＆プッシュ"
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

# Git Commit & Push

ディスク上の変更を作業単位で commit & push する。エディタ内の未保存の編集は、この環境では保存できない場合がある。

## 保存

- 今回の依頼またはハーネスの状態から保存済み・未保存なしと確認できれば、保存処理と再確認は不要。
- それ以外は、現在のハーネスで許可された保存機能があれば使い、正常完了を確認する。拡張機能や補助スクリプトは追加しない。
- 保存手段がない、失敗・キャンセル・未保存の残存、または完了未確認でも、確認質問や停止はせず、ディスク上の内容で Git 操作を続行する。最終報告で保存結果と、未保存の編集が反映されていない可能性を明記する。保存済みとは推測しない。

## Git 操作

1. 作業ディレクトリ、現在のブランチ、送信先 remote / upstream、`git config user.name` を確認する。
2. `git fetch <remote>` と `git status -sb` で同期状態と変更を確認する。未コミット変更も未送信コミットもなく、behind でもなければ `Nothing to commit/push` で終了する。
3. 未コミット変更がある場合は差分を確認し、対象パスを明示して `git add -- <対象パス>`、`git diff --cached --check`、`git commit` の順に実行する。複数PoC・別artifact/test・無関係な変更は作業単位へ分類し、scope別の明示pathでstageして別コミットにする。
4. push 直前に送信先を再 fetch し、ahead / behind を確認する。behind の解消は作業ツリーが clean かつ fast-forward 可能な場合の `git pull --ff-only` に限る。解消できなければ停止して状況を報告し、rebase・autostash・履歴変更を承認なく実行しない。
5. `git push` を実行する。rejected の場合は手順4で再確認し、解消できた場合だけ1回再試行する。
6. 完了後、リモートリポジトリの URL を Markdown リンクで表示する。

## コミットメッセージ

Conventional Commits 形式: `<type>(<scope>): <subject> - <user.name>`。`<user.name>` は手順1で取得した値を使う。
