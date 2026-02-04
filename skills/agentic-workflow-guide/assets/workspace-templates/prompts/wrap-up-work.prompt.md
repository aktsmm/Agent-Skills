---
description: セッション終了時のクリーンアップ
---

# Prompt: Cleanup Session

セッション終了時のクリーンアップ。

## セッション終了チェックリスト

実行前に確認：

- [ ] 未保存ファイルがないか
- [ ] エラーが残っていないか（`get_errors` で確認）
- [ ] コミットすべき変更があるか（`git status`）
- [ ] TODO リストが完了しているか
- [ ] 重要な学びがあれば `/review-session-export-md` でエクスポート済みか

## コマンド実行

以下を順番に実行：

1. `inlineChat.acceptChanges`
2. `workbench.action.files.saveAll`
3. `workbench.action.closeUnmodifiedEditors`
4. `workbench.action.chat.clearHistory` → **Delete All** を押す
5. `workbench.action.chat.newChat` → 手動で **+** ボタン or `Ctrl+Shift+P` → "Chat: New Chat"
