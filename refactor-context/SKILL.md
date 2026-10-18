---
name: refactor-context
description: "指定スコープの instruction / agent / skill をコンテキスト最適化する。単一ファイルも複数ファイル群の MECE 横断レビューも扱う。構造レビューは review-workflow-structure の担当"
disable-model-invocation: true
argument-hint: "対象ファイルまたはスコープ（ALL / Global / ALL + Global）、モード（auto / 確認）"
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

# refactor context

## When to Use

- 使う: 単一ファイル内のコンテキストを圧縮・整理
- 使う: 複数ファイル群を横断して SSOT / DRY / SRP / MECE / スコープ適合を見る
- 使わない: SKILL 本文の設計、新規 agent / workflow の scaffold

## モードとスコープ

- モード: `自動` / `オート` / `auto` 含む → オート（不可逆・影響大は提案止まり）。それ以外は確認モード
- スコープ: `指定なし` は対象のみ / `ALL` / `Global` (=`~/.copilot/` の instructions・skills・agents) / `ALL + Global`
- 対象外（明示指定なき限り）: `.github/skills/`, `.vscode/settings.json`
- スコープ境界: `Global` 対象は `~/.copilot` 内で完結させる。明示許可なしに現在の workspace / repo へ移動・分割・SSOT 化を提案しない
- 現在 workspace は参照情報としてだけ使う。配置先提案の既定にしない


## 判断ルール

目標: 対象ファイルを AI が判断できる最小情報に圧縮する。人間向け可読性は二次

- 削除を先に判定し、必要な残りだけを圧縮する。記述なしでも正常・例外・停止時の判断が変わらない一般論 / 自明な説明 / 装飾 / metadataの言い換え / 重複 / 役割が消えた節 / 無効なルール・exampleは、短く言い換えて残さない
- 残す: 判断に必要なユーザー固有事実 / ID / パス / 方針、参考 URL・判断に効く設計根拠、Example（最低 1 つ）、非自明な手順。具体的な失敗条件・引数・承認範囲・未検証要件・停止・復旧手順は自明扱いせず残す
- 圧縮: 必要だが冗長な定義・前置き・エラー例。統合済みの重複を削るときは、許可スコープ内の参照先と実際の読み込み経路で同じ判断が成立することを確認する
- 履歴: 古さだけで削除しない。現行判断に不要で原文の保存を確認できた履歴は削除候補にし、必要なら固定リビジョン等の再取得先だけ残す。未保存の追記は保存を確認するまで保持する
- 削除禁止: 運用メタコメント（`syncToGlobal` / `author` / `repository` / `license` / `copyright`）

## レビュー観点

- SSOT / DRY / SRP / スコープ適合
- `applyTo` / 常時ロード / 手動呼び出しの整合
- agent は本文の tool reference が frontmatter `tools` と整合しているか（不一致は lint エラー）
- 適用範囲・ルーティング（いつ使う / 使わない / どこへ逃がす）が、見出しだけに依存せず各ルールで明確か
- 意味保持: 主語・対象・適用条件、必須／任意、優先／禁止、例外、停止・検証条件を変えていないか。統合で対象を意図せず広げない（例: script不在の実行停止を新規ファイル作成禁止へ広げない）。意図した挙動変更は圧縮と区別し、承認範囲を確認する
- 判断の整合: 経路選択 → 実行 → 検証 → 停止がつながり、後続ルールが先に選んだ経路や制約を覆さないか
- Global 対象の逃がし先は `~/.copilot` の instruction / agent / skill に限る。workspace へ逃がす案は「明示許可が必要」と書く

複数ファイル時のみ追加:

- MECE: 同じ概念の重複定義なし / 想定タスクに空白なし
- 配置適合（always-on / scoped / 手動参照）
- 逃がし先有効性: 対象スコープ内の `applyTo` 付き instruction / 明示呼び出し型 agent・skill / references のいずれか。**不可**: 別スコープへの移動・参照リンク（明示許可がある場合を除く）
- ファイル提案順序: 削除（役割消失 / 重複） → 既存への統合 → 既存ファイル内の整理 → 分割 → 新規追加。新規ファイルは最後の手段
- Global 対象のファイル提案順序: Global 内で削除 → Global 既存へ統合 → Global 既存内で整理 → Global 内で分割 → Global 新規追加。workspace 化は提案順序に含めない
- ファイル削除は破壊的なのでオートモードでも提案止まり

## 手順

1. 対象全件の全文で削除候補を先に判定し、必要な残りを圧縮する。直近の変更節だけで評価しない。Before→After を提示（文字数は改行を同じ条件で計測し、行数/見出し数も示す）
2. 文字数・行数は補助指標とし、短くても曖昧さ・矛盾・重複をレビューする。明確な問題がなければ変更不要
3. 適用は 1 ファイルずつ
4. 適用後は原文と変更後で、対象に該当する正常時・例外時・停止時の代表入力に対する判断を比較する。意図しない差を修正し、キーワード残存だけで合格にしない。複数ファイル時は MECE（重複消失 / 空白未増）も確認
