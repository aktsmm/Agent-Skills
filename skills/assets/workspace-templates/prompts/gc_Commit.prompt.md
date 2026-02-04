---
description: 保存してコミット（Pushなし）
---

# Prompt: Commit

保存していないファイルを保存して commit してください。

## 手順

0. **ワークスペース確認**: `Get-Location; git remote -v` で現在地とリモートリポジトリを確認し、意図したリポジトリにいることを確認（違う場合は `Set-Location <正しいパス>` で移動）
1. `git config user.name; git status --short` でユーザー名 + 変更確認（変更なければ「Nothing to commit」で終了）
2. VS Code コマンド `workbench.action.files.saveAll` で未保存ファイルを保存
3. `git add .; git commit -m "<コミットメッセージ>"` でステージング & コミット

## コミットメッセージのフォーマット

**Conventional Commits** 形式でコミットメッセージを作成してください。
詳細は [git.instructions.md](../instructions/dev/git.instructions.md) を参照（存在する場合）。

```
<type>(<scope>): <subject> - <user.name>
```

例（`git config user.name` を反映）:

- `feat(auth): ログイン機能を追加 - <user.name>`
- `fix(api): タイムアウトエラーを修正 - <user.name>`
- `docs(readme): セットアップ手順を更新 - <user.name>`
