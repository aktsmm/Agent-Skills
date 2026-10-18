---
name: git-pull
description: "リモートからPullして変更箇所を表示"
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

# git pull

リモートレポジトリの最新状態に合わせて(Pull)、変更箇所を教えてください。

## 手順

1. 現在地、ブランチ、remote / upstream、`pull.rebase` / `branch.<name>.rebase` / `pull.ff` の有効な設定を確認する。対象不明、upstream 未設定、または merge / rebase / 競合解消の途中なら変更せず停止する。
2. pull 前の HEAD を `git rev-parse HEAD` で記録し、`git status --short`、`git diff`、`git diff --cached`、`git stash list --format=%H` でローカル変更・ステージ状態・未追跡ファイル・既存 stash の OID を記録する。未追跡ファイルは autostash の保護対象とみなさない。
3. 既存の取り込み設定を変えず `git pull --autostash` を実行し、直後の終了コードと出力を記録する。方式未設定で履歴が分岐している場合は確認して停止し、別方式で自動再試行しない。
4. 終了コードだけで成功とせず、`git status`、`git diff --name-only --diff-filter=U`、実行後の差分と stash の OID を確認する。取り込み処理の完了、未解決競合なし、実行前のローカル変更内容の復元を個別に検証し、ステージ状態の変化も報告する。復元は差分文字列の完全一致や変更パスだけで判定せず、記録した編集内容が取り込み後のファイルに保持・反映されたかを照合する。新規 stash が残った、変更が欠けた、または復元を確認できない場合は未完了とする。
5. 失敗・競合・復元未確認ならそこで停止する。取り込みと復元のどちらで止まったか、merge / rebase の進行中状態、HEAD の変化、競合パス、残った stash の OID と次の確認を報告する。stash の再適用・削除、reset、abort、再 pull は承認なく実行しない。
6. 両方の成功を確認してから pull 後の HEAD を取得し、`git log --oneline <before>..<after>` と `git diff --stat <before> <after>` / `git diff <before> <after>` で今回のコミットとファイル差分を要約する。rebase 時は書き換えられたローカルコミットも範囲に含まれるため、全件をリモート由来と呼ばない。HEAD が同じなら取り込み変更なしと報告する。
