---
name: prompt-to-skill-reconcile
description: "Prompt ファイル (.prompt.md) から Skill へ移行した後に、ワークスペース内の instructions / agents / README / Skill 本文 / スクリプトに残る旧 Prompt 前提の参照と運用手順を点検し、承認後に最小修正する。Use when: Prompt から Skill に移行した、migration 後の参照修正、.github/prompts 前提の記述が残っていないか確認、移行後の整合チェック、Scheduler など自動実行タスクの旧 Prompt 参照の更新。移行そのものの実行や Skill の新規設計には使わない。"
argument-hint: "対象ワークスペース、移行した Prompt / Skill の範囲（省略時は Git 差分から推定）"
disable-model-invocation: true
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
   - スクリプトの docstring・コメント・設定・実行時の表示文
   - 自動実行タスクの inline prompt（Scheduler・cron・CI・hook）。ファイルでなくツール側に保存されるため、ファイル検索では見つからない。一覧と詳細を実際に読む
   - 旧名の表記ゆれ（`ppt_x` と `ppt-x`、`/prompt X` と `/X`）。Skill 名はフォルダ名に揃うので、旧名と綴りが変わる
3. **分類する**: 各ヒットを次に分ける。
   - 修正: 現行の手順・依存・正本の案内として生きている参照
   - 保持: 過去の議事録・作業ログなど履歴の記録、Prompt 一般の説明、LLM に渡す文面としての「プロンプト」
   - 要判断: 対応先が不明、挙動が変わる、承認が要るもの。検査・検出用に旧名を文字列として持つ処理（プレースホルダー検出、旧型ワークスペース検出）は、変えると検査の挙動が変わるので既定で保持し、1 回だけ確認する
4. **修正案を提示して確認を取る**: 対象・変更前後・理由・挙動への影響を表で示す。リネーム・移動・削除は dry-run を先に見せる。
5. **最小修正する**: 承認された範囲だけ直す。既存の未コミット変更を巻き込まない。編集前にファイルごとの改行コード（CRLF／LF の行数）と文字コードを実測して記録し、既存に合わせる。複数行の置換を CRLF ファイルへ行うと LF が混入し、編集ツールでは戻せないため、1 行単位で置換する。自動実行タスクは保存済み文面全体の置換になるので、旧参照以外を一字も変えず、cron・有効状態・model・実行モードは維持する。
6. **検証する**: 下記の完了条件を機械的に確認し、結果を報告する。

## 守ること

- 一括置換しない。ヒットごとに文脈を見て判断する。
- `disable-model-invocation` など呼び出し挙動の設定は、明示指示なしに変更しない。
- 移行ツールが付けた手動呼び出し専用（`disable-model-invocation: true`）は元が Prompt なので既定で維持する。ただし instructions に「自動で実行」の記述があれば、自動起動しない旨と `/名前` 案内への寄せ方を要判断として 1 回だけ確認する。
- Skill の `name` はフォルダ名と一致させる。不一致は修正案に挙げる。
- 移行と無関係な整理・リファクタ、コミット、push は行わない。
- Skill 一覧や登録カタログがある場合は、移行した Skill が載っているか確認する。自動生成ブロックがあるときは、その外側に追記する。
- 履歴として保持した参照は、残した理由を報告する。

## 完了条件

- 現行の手順・依存・正本の案内に旧 Prompt 参照が残っていない（保持分は理由つきで報告）
- 修正後の参照先がすべて実在する
- 移行した Skill の `name`・`description` が揃い、一覧に載っている
- 呼び出し設定が変更されていない（変更した場合は承認済み）
- 空白・文字コード・改行が崩れていない（編集前後で CRLF／単独 LF の行数を比較する。移行ツールが frontmatter だけ LF で書く既存の混在は崩れに数えない）
- 自動実行タスクを更新した場合は、保存後の文面を読み戻し、旧参照が無く、他の設定が不変であること
- 実機での呼び出し確認など、未実施の検証は「未確認」と明記する

詳細な検索観点と誤検出の扱いは [references/reconciliation-checklist.md](references/reconciliation-checklist.md)。
