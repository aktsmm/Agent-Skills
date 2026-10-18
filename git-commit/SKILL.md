---
name: git-commit
description: "ディスク上の変更を作業単位でコミット（Pushなし）"
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

# git commit

ディスク上の変更を作業単位で commit してください。エディタ内の未保存の編集は、この環境では保存できない場合がある。

## 手順

1. `Get-Location; git branch --show-current` で現在地とブランチを確認
2. `git config user.name` でユーザー名を取得（コミットメッセージに使用）
3. 未保存なしと確認済みの場合以外は、現在のハーネスで許可された保存機能があれば使う。保存機能がない・失敗した・完了未確認でもディスク上の内容で続行し、最終報告で未保存の編集が反映されていない可能性を明記する。保存用の拡張機能や補助スクリプトは追加しない。
4. 保存処理後に `git status --short`、`git diff`、`git diff --cached` を確認する。変更がなければ「Nothing to commit」で終了する。既存 staged を含め今回の対象を確定し、無関係な変更や所有不明の変更が混在して対象を決められない場合は確認する。
5. 作業単位ごとに対象パスを明示して `git add -- <対象パス>` を実行する。成功後に `git diff --cached` で staged 全体がその作業単位だけであることを確認し、`git diff --cached --check` を実行する。add またはチェックに失敗したら停止して報告する。無関係な staged が残る場合は勝手に解除せず停止して確認する。
6. チェック成功後に `git commit -m '<コミットメッセージ>'` を実行し、成功を確認してから次の作業単位へ進む。独立した作業は別コミットにする。完了後はコミットIDと残った変更を報告し、push は実行しない。

## コミットメッセージのフォーマット

**Conventional Commits** 形式でコミットメッセージを作成してください。

```
<type>(<scope>): <subject> - <user.name>
```

例（`git config user.name` を反映）:

- `feat(auth): ログイン機能を追加 - <user.name>`
- `fix(api): タイムアウトエラーを修正 - <user.name>`
- `docs(readme): セットアップ手順を更新 - <user.name>`
