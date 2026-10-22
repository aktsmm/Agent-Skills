---
name: prompt-to-skill-reconcile
description: "Prompt ファイル (.prompt.md) から Skill へ移行した後に、ワークスペース内の instructions / agents / README / Skill 本文 / スクリプトに残る旧 Prompt 前提の参照と運用手順を点検し、承認後に最小修正する。Use when: Prompt から Skill に移行した、migration 後の参照修正、.github/prompts 前提の記述が残っていないか確認、移行後の整合チェック。移行そのものの実行や Skill の新規設計には使わない。"
argument-hint: "対象ワークスペース、移行した Prompt / Skill の範囲（省略時は Git 差分から推定）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: aktsmm
---

# Prompt To Skill Reconcile

Prompt から Skill への移行が済んだワークスペースで、旧 Prompt を前提にした記述だけを見つけて直す。移行の実行、Skill の新規設計、文体整理は扱わない。

## When to Use

- 「Prompt から Skill に移行したので関連ルールも直して」「.github/prompts 前提の記述が残っていないか確認して」
- 移行ツールの実行後に、参照・一覧・呼び出し方の整合を確認したいとき

## Workflow

1. **対応表を作る**: 旧 Prompt と移行先 Skill を、Git 差分（削除された `*.prompt.md`、追加された `SKILL.md`）とファイル一覧から対応付ける。名前だけで推測せず、本文の用途で照合する。対応先が無い・複数ある・名前が意図とずれている（例: 無関係な名前で作られた）ものは確認事項にする。
2. **旧前提を検索する**: 次を対象に、`.github/prompts`、`.prompt.md`、「prompt を読む」「prompt に従う」、Prompt を正本とする記述、Prompt 前提のフロー図・依存一覧を検索する。
   - instructions / `AGENTS.md` / agents / chat modes / templates
   - README / docs / Skill 一覧
   - Skill 本文（自身が「prompt」と名乗る説明を含む）
   - スクリプトの docstring・コメント・設定
3. **分類する**: 各ヒットを次に分ける。
   - 修正: 現行の手順・依存・正本の案内として生きている参照
   - 保持: 過去の議事録・作業ログなど履歴の記録、Prompt 一般の説明、LLM に渡す文面としての「プロンプト」
   - 要判断: 対応先が不明、挙動が変わる、承認が要るもの
4. **修正案を提示して確認を取る**: 対象・変更前後・理由・挙動への影響を表で示す。リネーム・移動・削除は dry-run を先に見せる。
5. **最小修正する**: 承認された範囲だけ直す。既存の未コミット変更を巻き込まない。編集前にファイルごとの改行コードと文字コードを実測し、既存に合わせる。
6. **検証する**: 下記の完了条件を機械的に確認し、結果を報告する。

## 守ること

- 一括置換しない。ヒットごとに文脈を見て判断する。
- `disable-model-invocation` など呼び出し挙動の設定は、明示指示なしに変更しない。
- Skill の `name` はフォルダ名と一致させる。不一致は修正案に挙げる。
- 移行と無関係な整理・リファクタ、コミット、push は行わない。
- Skill 一覧や登録カタログがある場合は、移行した Skill が載っているか確認する。自動生成ブロックがあるときは、その外側に追記する。
- 履歴として保持した参照は、残した理由を報告する。

## 完了条件

- 現行の手順・依存・正本の案内に旧 Prompt 参照が残っていない（保持分は理由つきで報告）
- 修正後の参照先がすべて実在する
- 移行した Skill の `name`・`description` が揃い、一覧に載っている
- 呼び出し設定が変更されていない（変更した場合は承認済み）
- 空白・文字コード・改行が崩れていない
- 実機での呼び出し確認など、未実施の検証は「未確認」と明記する

詳細な検索観点と誤検出の扱いは [references/reconciliation-checklist.md](references/reconciliation-checklist.md)。
