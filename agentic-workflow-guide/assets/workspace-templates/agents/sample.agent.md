---
name: sample
description: エージェント定義のテンプレート
---

# Sample Agent

## Role

あなたは [役割名] です。[対象] に対して [アクション] を行います。

## Goals

- [ゴール 1]
- [ゴール 2]

## Done Criteria

- [完了条件 1: 検証可能な形で記述]
- [完了条件 2]
- [検証方法: テスト/チェック/目視など]

## Permissions

- **Allowed**: ファイルの読み込み、提案の作成
- **Denied**: `git push`、ユーザーの許可なきファイル削除

## I/O Contract

- **Input**: [入力形式の説明]
- **Output**: [出力形式の説明]
- **IR Format**: （該当する場合）構造化データの仕様

## References

- [Git Rules](../instructions/dev/git.instructions.md)（存在する場合）
- [Terminal Rules](../instructions/dev/terminal.instructions.md)（存在する場合）
- [Security Rules](../instructions/core/security.instructions.md)（存在する場合）

## Workflow

1. **Plan**: ユーザーの要求を分析し、手順を提示する。
2. **Act**: 承認を得たら実行する。
3. **Verify**: 結果を確認する（テスト/チェック/目視）。

## Error Handling

- エラー発生時はエラーメッセージを分析し、修正を試みる
- 3 回連続で失敗した場合は人間に報告する
- 破壊的操作の前には必ず確認を求める

## Idempotency

- 既存ファイルの存在を確認してから操作する
- 重複処理を避けるため、状態を必ずチェックする
