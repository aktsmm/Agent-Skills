# to-{{NEXT_MEETING_DATE}} 進捗ボード

> 次回 MTG: {{NEXT_MEETING_DATETIME}}
> 出どころとなる主なミーティング: [meeting-notes/{{SOURCE_MEETING_FILE}}](../../meeting-notes/{{SOURCE_MEETING_FILE}})
> 関連メモ: {{RELATED_MEMO_LINKS}}

このフォルダは、{{NEXT_MEETING_DATE}} の MTG までに片付ける作業の置き場です。長期継続案件は `next-actions/ongoing/` に置きます。

---

## 進捗一覧

### homework: 顧客と合意した宿題

| 状態        | 内容                 | 担当      | リンク                                   |
| ----------- | -------------------- | --------- | ---------------------------------------- |
| not-started | {{HOMEWORK_TITLE_1}} | {{OWNER}} | [homework/01_xxx.md](homework/01_xxx.md) |

### proposals: こちらから持っていく追加提案準備

| 状態        | 内容                 | 担当      | リンク                                     |
| ----------- | -------------------- | --------- | ------------------------------------------ |
| not-started | {{PROPOSAL_TITLE_1}} | {{OWNER}} | [proposals/01_xxx.md](proposals/01_xxx.md) |

### research: 調査・検証（補足扱い）

| 状態        | 内容                 | 担当      | リンク                                   |
| ----------- | -------------------- | --------- | ---------------------------------------- |
| not-started | {{RESEARCH_TITLE_1}} | {{OWNER}} | [research/01_xxx.md](research/01_xxx.md) |

---

## 状態の凡例

- `not-started`: 未着手
- `in-progress`: 着手中
- `blocked`: 詰まっている（理由を該当ファイルに書く）
- `done`: 完了
- `dropped`: 次回までにやらない判断をしたもの（理由を該当ファイルに書く）

## 更新ルール

- 各タスクの詳細・メモ・成果物は各タスクファイルに書く。
- この README は状態と担当の一覧のみ更新する。
- 完了したら該当行を `done` にし、議事録側のリンクも残したまま保つ（履歴として）。
