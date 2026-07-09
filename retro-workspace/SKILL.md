---
name: retro-workspace
description: Reflect reusable learnings into the current workspace / repository design and automation assets (.github/**, AGENTS.md, repo scripts/tasks). Use when running a workspace/repo retro from CLI or Scout. Detects whether a project folder exists and, if not, asks before creating one. Triggers on "retro workspace", "repo retro", "workspace cleanup", "ワークスペース知見反映".
argument-hint: "反映したい学び、エラーログ/git diff/会話要約、対象 workspace、mode（safe-auto / review-only / dry-run）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# retro-workspace

インシデント・会話から再利用可能な知見を抽出し、現在の workspace / repository の設計資産・automation 資産へ最小差分で反映する CLI / Scout 向け SKILL。VS Code では同名 prompt を使う。判定とフローはこの SKILL 内で完結させ、他の skill / prompt に委譲しない。

## When to Use

- 使う: バグ解決後 / 再発時 / workspace 設計ギャップ発見時
- 使う: 既存手順より安全・再現可能・高速な script / task / helper へ昇格すべき改善を見つけたとき
- 使う: `.github/**`、`AGENTS.md`、repo 固有 instructions / prompts / agents / hooks、scripts、tasks への反映
- 使わない: typo のみ / 環境固有問題のみ / User Data / `~/.copilot`（個人グローバルは別の retro が担当）

## 入力

エラーログ / Git diff / 会話履歴 / ターミナル履歴のいずれか 1 つ以上。なければ追加要求して停止。

## Workspace 検出（反映先決定）

VS Code と違い、CLI / Scout は workspace（プロジェクトフォルダ）外で実行されることがある。知見抽出の前に反映先を決める。

1. 現在地が workspace 内か判定する: CWD かその親に `.git` / `.github/` / `AGENTS.md` のいずれかがあれば workspace とみなす
2. workspace あり: その repo ルートを反映先にして通常フローを進める
3. workspace なし: 自動でファイルを作らず、ユーザーに確認する
   - 選択肢を提示: (a) この知見を残すプロジェクトフォルダを新規作成する / (b) 反映せず handoff（知見だけ提示） / (c) 既存の別フォルダを指定する
   - (a) を選んだ場合のみ、最小のプロジェクトフォルダ（kebab-case slug の `README.md` + `.github/` 雛形）を作成し、そこを反映先にする。作成場所は確認する
   - 確認なしに勝手にフォルダを作らない

## Mode

- 既定は `safe-auto`。workspace scope が明確で、既存資産への小〜中規模更新で済む場合は確認なしで反映してよい
- `review-only` / `確認だけ` / `dry-run` / `プレビュー` が明示された場合だけ、変更案の提示で停止する
- scope 曖昧、大規模削除、公開・同期範囲変更、高リスクな実行コード / hook 変更、workflow の意味変更、secret / 個人情報 / 環境固有値の扱いに迷う場合だけ確認で停止する

## Scope Gate

- 反映先は `AGENTS.md`、`.github/**`、repo 固有 scripts / tasks / helpers に限定する
- secret / 認証情報 / 個人情報 / 顧客情報 / ローカル絶対パス / 端末固有値 / `/memories/**` は反映しない
- User Data / `~/.copilot` は scope 不一致として停止する
- `.github/skills/**` は直接編集せず、SKILL 向きなら提案して停止する

## Edit Rules

- 新規ファイルより既存への統合を優先し、`削除 → 統合 → 分離 → 追加` の順で検討する
- 圧縮は AI が判断できる最小情報を主目的にし、人間向け可読性は二次とする
- 冗長説明は圧縮するが、根拠 URL と非自明手順は残す
- 同じ Learning / Evidence / Impact を言い換えて繰り返さず、1 論点 1 塊でまとめる
- `AGENTS.md` と `.github/copilot-instructions.md` のような入口ファイルは役割過多を先に疑う
- script / task 化は、再利用価値・検証可能性・影響範囲の狭さが揃う場合を優先する

## 実行手順

### 0. Pre-Flight Inventory

知見抽出に入る前に、反映先候補を inventory する。どの `.instructions.md` / `tasks.json` / `scripts/` / `AGENTS.md` が受け皿になりそうか、適用される scope gate は何かを先に見る。これで scope を早めに定め、複数ファイルへの分散反映や既存資産との重複を防ぐ。

### 1. 知見抽出

- 設計原則、workflow、context、automation 改善、繰り返し指示の既定化を優先して拾う
- 1 件ごとに Learning / Evidence / Impact を作る

### 2. 変更案作成

- 優先度: Impact x Recurrence（P1/P2/P3）
- まず既存 workspace 資産へ統合できるかを確認する
- script / task 化が適切なら既存 runner や script directory を優先する
- レポート/HTML化で実画面を扱う場合は、actual UI screenshots と生成した evidence view を明示的に分け、Teams/チャット等の共有画面は投稿先・ユーザー・チャネル・URL周辺をマスクしてから反映する
- entry file では追加より先に圧縮を検討し、`AGENTS.md` と `.github/copilot-instructions.md` の役割差分を崩さない
- safe-auto では最小差分で反映し、review-only と Gate 停止時だけ提案に留める

### 3. 反映 + 必要時承認

- safe-auto で編集する
- 確認が必要な条件に該当する場合だけ、対象・理由・影響を示して承認後に反映する

### 3.5. 肥大化チェック（反映後）

反映後、DRY 違反・冗長表現・重複定義があれば圧縮・削除・分離する。

## Example Report

```markdown
# Retro: [Title]
- Target workspace: <repo root | 新規作成したフォルダ | handoff>
- Learnings: ...
- Changes: ...
- Gate: pass / stop reason
```

Stop: 知見なし / ユーザー拒否 / Gate 失敗 / handoff-required / review-only / workspace 未確定

