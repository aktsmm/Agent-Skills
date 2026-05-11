---
name: retro-copilot
description: "Run a retro for ~/.copilot assets. Use when reflecting learnings from incidents or conversations into copilot-instructions, instructions, skills, agents, hooks, or related .copilot config without touching memory."
argument-hint: "エラーログ、diff、会話要約、既存 .copilot 資産、またはインシデント内容"
user-invocable: true
---

# Retro Copilot

インシデント・会話から再利用可能な知見を抽出し、`~/.copilot` 配下の instructions / skills / agents / hooks / related config へ反映するための変更案を作る。

## When to Use

- 使う: バグ解決後 / 再発発生時 / レビューで `.copilot` 配下の個人用資産の設計ギャップが見つかったとき
- 使う: `~/.copilot/copilot-instructions.md`、`~/.copilot/instructions/**`、`~/.copilot/skills/**`、`~/.copilot/agents/**`、`~/.copilot/hooks/**` へ反映すべき運用知見があるとき
- 使わない: typo など軽微修正のみ / 環境固有問題のみ
- 使わない: workspace / repository 固有の内容。代わりに `retro-workspace` を使う
- 使わない: VS Code User Data の内容。代わりに `retro-user` を使う

## Core Rules

- `memory` は反映先にしない
  - `/memories/**`、user memory、session memory、repo memory を対象にしない
- 既定モードは `safe-auto`。`.copilot` scope が明確で、Safety & Scope Gate を通過し、既存資産への小〜中規模な統合・更新で済む場合は、確認なしで反映まで実行してよい
- `review-only` / `確認だけ` / `dry-run` / `プレビュー` が明示された場合だけ、変更案の提示で停止する
- 次の場合だけユーザー確認で停止する: scope 判断が曖昧、大規模削除、公開・同期範囲変更、hook / config の高リスク変更、既存 agent / skill の意味を大きく変える変更、secret / 個人情報 / 環境固有値の扱いに迷う場合
- 新規ファイル作成より既存ファイルへの統合を優先する
- 他スコープの内容なら自分で編集せず handoff する

## Workflow

```text
Context -> Extract -> Safety & Scope Gate -> Decide Action & Target -> Validate & Output
```

## Phase 1: Context Collection

- 入力（1つ以上必須）
  - エラーログ、diff/commit、会話履歴、ターミナル履歴、既存 `.copilot` 資産
- 既定の反映スコープ
  - `~/.copilot` 配下の個人グローバルカスタマイズ資産を優先する
  - workspace / repository や VS Code User Data へ反映すべき知見はこの skill では扱わず、handoff を提案する
  - memory 系スコープは反映先にしない
- ターミナル観点
  - Exit Code != 0
  - Ctrl+C（中断）
  - 同コマンド反復
  - 長時間実行
- Gate: 入力なしなら追加要求して停止

## Phase 2: Extract Learnings

- カテゴリ
  - 設計原則（SRP/SSOT/idempotency）
  - ワークフロー
  - プロンプト設計
  - コンテキスト設計
  - エラーパターン
- 1件ごとに `Learning / Evidence / Impact` を作成
- Gate: actionable な知見がなければ停止

## Phase 2.5: Safety & Scope Gate

- 反映禁止または抽象化が必要な情報
  - secret、認証情報、API キー、接続文字列
  - 個人情報、顧客情報、個人アカウント値
  - ローカル絶対パス、端末固有値、一時ディレクトリ
  - 外部共有に不向きな会話本文やログ断片
- No Memory Targets Gate
  - `/memories/**`、user memory、session memory、repo memory を反映先にしない
  - memory に残す必要がある依頼は、この skill では実行せず別タスクとして明示確認する
- Scope Gate
  - `~/.copilot` 配下の資産に置くべき内容か確認する
  - workspace / repository や VS Code User Data に置くべき内容なら、この skill では反映せず handoff を提案する
- Gate（全必須）
  - 永続化する知見は再利用可能なルールに抽象化されている
  - 証拠は必要最小限で、機微情報を含まない
  - `~/.copilot` 配下に置くべき内容か確認済み
  - No Memory Targets Gate を通過済み

## Refactor Context Rules

- SSOT を守る。重複定義は統合する
- 新規ファイル作成より既存ファイルへの統合を優先する
- 既存ファイルに 1 セクション追加や 1 ルール追記で済むなら、新規ファイルを作らない
- 単一ルール追加や導線追加は catch-all な既存ファイルを優先し、新規ファイルは最後の手段にする
- 新規ファイルは、既存ファイルの役割に収まらず `Target Rationale` で必要性を説明できる場合だけ許可する
- 50 行以下の小さいファイルは、明確な価値がない限り変更不要または最小差分とする
- 冗長説明は圧縮するが、根拠 URL・非自明な手順・運用メタコメントは消さない
- `Target Rationale` では「なぜ新規作成でなく既存統合か」を必ず説明する

## Phase 3: Decide Action & Target

- 優先度: Impact x Recurrence（P1/P2/P3）
- 反映先
  - 共通原則 → `~/.copilot/copilot-instructions.md`
  - domain instructions → `~/.copilot/instructions/**/*.instructions.md`
  - skills → `~/.copilot/skills/**/SKILL.md`
  - agents → `~/.copilot/agents/**/*.agent.md`
  - hooks → `~/.copilot/hooks/**/*.json`
  - related config → 次に限定する
    - `~/.copilot/config.json`
    - `~/.copilot/settings.json`
    - `~/.copilot/permissions-config.json`
    - `~/.copilot/mcp-config.json`
    - `~/.copilot/mcp-oauth-config/**`（customization と直接整合するものだけ）
- 反映禁止
  - workspace / repository の `AGENTS.md`、`.github/**`、workspace docs
  - VS Code User Data の `*.prompt.md` / `*.instructions.md` / `*.agent.md`
  - `/memories/**`、user memory、session memory、repo memory
  - `command-history-state.json`、`session-store.db`、`vscode.session.metadata.cache.json`
  - `session-state/**`、`logs/**`、`pkg/**`、`crash-context/**`、`restart/**` のようなランタイム生成物やキャッシュ
- 反映先ファイルが存在しない場合:
  - safe-auto で新規作成してよい。ただし既存資産に統合できる場合は統合を優先する
  - ディレクトリも不在なら、作成予定のパスと理由を示す
  - scope や公開可否に迷う場合だけユーザー承認後に重複/矛盾チェックへ進む

## Decision Rules

- まず既存 `.copilot` 資産へ統合できないかを見る
- instructions は原則、skills はタスク手順、agents は役割分離、hooks は決定的自動化の棲み分けで選ぶ
- 新規作成は既存の役割に収まらない場合だけ
- workspace / repository へ反映すべき内容は `retro-workspace` に handoff する
- VS Code User Data へ反映すべき内容は `retro-user` に handoff する
- memory 系スコープは反映先にしない
- 最小差分で反映する

## Output Requirements

- `## Learnings`
- `## Changes`
- `## Target Rationale`
- `## Review Checkpoint`

`## Review Checkpoint` には最低限次を含める:

- [ ] safe-auto executed or user approval obtained when gated
- [ ] Copilot scope confirmed
- [ ] No duplicate rules verified
- [ ] Target files are writable
- [ ] Safety & Scope Gate passed
- [ ] No memory target selected