---
description: リモートからPullして変更箇所を表示
---

# Prompt:Pull

リモートレポジトリの最新状態に合わせて(Pull)、変更箇所を教えてください。

## 手順

0. `git remote get-url origin; git branch --show-current; git pull` で Remote URL + ブランチ名 + pull
1. `git log --oneline -5` で直近 5 件のコミットを表示（変更サマリ）
