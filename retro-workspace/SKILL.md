---
name: retro-workspace
description: "Reflect reusable learnings into the selected workspace's authorized instructions and automation assets, such as AGENTS.md, copilot-instructions.md, scoped instructions, scripts, and tasks. Use only for an explicit workspace/repo retro request: retro workspace, repo retro, ワークスペース知見反映. Not for user-wide settings, installed Skill mirrors, or reusable Skill authoring."
argument-hint: "反映したい学び、エラーログ/git diff/会話要約、対象 workspace、mode（safe-auto / review-only / dry-run）"
disable-model-invocation: true
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# retro-workspace

明示された workspace retro 依頼だけを実行し、知見を選択workspaceの承認済み指示・automation資産へ最小差分で反映する。判定とフローはここで完結させる。

## When to Use

- 使う: バグ解決後 / 再発時 / workspace 設計ギャップ発見時
- 使う: 既存手順より安全・再現可能・高速な script / task / helper へ昇格すべき改善を見つけたとき
- 使う: `.github/**`、`AGENTS.md`、repo 固有 instructions / agents / hooks、scripts、tasks への反映
- 使わない: typo のみ / 環境固有問題のみ / user-wide settings / installed Skill mirrors / reusable Skill authoring（対象外の知見は反映せずhandoffする）

## 入力

エラーログ / Git diff / 会話履歴 / ターミナル履歴のいずれか 1 つ以上。なければ追加要求して停止。

## Workspace 検出（反映先決定）

実行環境によっては active workspace を取得できない場合がある。知見抽出の前に反映先を決める。

1. ユーザーまたは host context が workspace path を明示している場合: repo marker の有無を問わず、その folder を反映先にする。CWD や外部の新規プロジェクト候補で上書きしない
2. 明示 workspace path がない場合: CWD かその親に `.git` / `.github/` / `AGENTS.md` のいずれかがあれば、その repo ルートを反映先にする
3. workspace なし: ファイルもフォルダも作らず、ユーザーに確認する
   - 選択肢を提示: (a) 反映せず handoff（知見だけ提示） / (b) 既存の別フォルダを指定する
   - 新規プロジェクトフォルダは、ユーザーが作成先を自分で指定した場合を除き、作成も提案もしない

## Mode

- 既定は `safe-auto`。workspace scope が明確で、既存資産への小〜中規模更新で済む場合は確認なしで反映してよい
- `review-only` / `確認だけ` / `dry-run` / `プレビュー` が明示された場合だけ、変更案の提示で停止する
- Confirm only unclear scope, new privileges/destinations/visibility/defaults, destructive deletion or uncertain sensitive data. Bounded fixes need no reapproval; code/hooks widening permissions still do.

## Scope Gate

- 反映先は選択workspaceの承認済み指示・automation資産（例: `AGENTS.md`、`.github/copilot-instructions.md`、個別 `.instructions.md`、repo scripts/tasks）に限定する。ホスト名で反映先を固定せず、適用範囲と依頼で決める。他ホストの資産やoverride fileへ勝手に広げない
- secret / 認証情報 / 個人情報 / 顧客情報 / ローカル絶対パス / 端末固有値 / `/memories/**` は反映しない
- user-wide configuration と installed Skill mirrors はホストを問わずscope不一致として停止する
- `.github/skills/**` は直接編集せず、SKILL 向きなら提案して停止する
- このworkflowから公開・配布は行わない

## Edit Rules

- 新規ファイルより既存への統合を優先し、`削除 → 統合 → 分離 → 追加` の順で検討する
- 新しいルールを書く前に、同じ判断が scripts / 生成物 / 既存資産に実装済みでないか確認する。実装と矛盾するルールは、次の run に正しい資産を壊させる
- 外付けドライブ上の repo で編集ツールが eDLP（`os error 449`。読み取りと `Copy-Item` は通る）に止められたら、内蔵ドライブへステージして編集し、`Copy-Item` で戻してハッシュを照合する。この遮断に限った手順で、ステージ後も同内容の書き込みが 2 回失敗したら、別の回避をせず停止して報告する
- 設定を根拠にする場合はnested値までparseして機微値を除去し、raw設定blockやsecret-bearing行を貼らない
- Use an isolated clean checkout for authorized Git mutations; preserve unrelated dirty, avoid blanket staging/autostash, and group owning-scope edits. Refresh ledger IDs before appending and verify uniqueness after an authorized commit. Do not add unrequested commits/pushes.
- For an explicitly authorized push, fetch, inspect the permitted ahead range and integrate behind/divergence in the clean execution checkout first; never use force or stale tracking refs.
- After moving a multi-paragraph Markdown section, verify heading order, exactly one occurrence of the moved heading and its first content line, and `git diff --check`; delete-plus-insert moves can otherwise leave an omission or duplicate.
- 圧縮は AI が判断できる最小情報を主目的にし、人間向け可読性は二次とする
- 正常・例外・停止時の判断を変えない不要・自明・重複の説明は先に削除し、必要な残りだけ圧縮する。根拠 URL・非自明な手順・承認範囲・未検証要件・停止／復旧条件・必要な実例・metadataは残す。履歴は古さだけで削らず、原文の保存を確認し、未保存の追記は保持する
- 同じ Learning / Evidence / Impact を言い換えて繰り返さず、1 論点 1 塊でまとめる
- `AGENTS.md` と `.github/copilot-instructions.md` のような入口ファイルは役割過多を先に疑う。ただし詳細を別資産へ移すときは、入口に1行のポインタを残す（リンクがないと発見されない。入口サイズを理由に先送りしない）
- script / task 化は、再利用価値・検証可能性・影響範囲の狭さが揃う場合を優先する

## 実行手順

### 0. Pre-Flight Inventory

知見抽出に入る前に、反映先候補を inventory する。どの `.instructions.md` / `tasks.json` / `scripts/` / `AGENTS.md` が受け皿になりそうか、適用される scope gate は何かを先に見る。これで scope を早めに定め、複数ファイルへの分散反映や既存資産との重複を防ぐ。

### 1. 知見抽出

- 設計原則、workflow、context、automation 改善、繰り返し指示の既定化を優先して拾う
- 一度の否定的観測（「その機能は無い」）を規則にしない。認証状態、拡張のアクティブ化、モードを潰してから確定し、潰しきれないなら観測条件を添えて残す
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

不要・自明・重複だけを先に除き、通常・例外・停止の判断を変えずに圧縮・分離する。根拠、非自明な手順、scope、必須例、metadata、承認、未検証要件、失敗・復旧条件、未保存メモは保持し、古さだけで履歴を削らない。入口から分離した資産へは発見用の短い参照を残す。
変更箇所と適用scopeを読み戻し、関連するvalidationを実行する。未実行・能力不足は`NOT_RUN`とし、編集できたことだけで動作確認済みにしない。

## Next Candidates

List up to three scoped read-only follow-ups: dirty authoring/private-push/distribution gaps. Use the owning workflow, honor holds/visibility, and never widen scope or execute suggestions.

## Example Report

```markdown
# Retro: [Title]

- Target workspace: <repo root | ユーザー指定フォルダ | handoff>
- Learnings: ...
- Changes: ...
- Outcome: applied / already-covered / skipped / handoff / needs-confirmation / review-only
- Verification: <check>: PASS / FAIL / NOT_RUN
- Gate: pass / stop reason
```

Stop: 知見なし / ユーザー拒否 / Gate 失敗 / handoff-required / review-only / workspace 未確定

Source: yamapan's workflows from `aktsmm/Agent-Skills` and `aktsmm/Agent-Customization`; capability and verification safeguards consolidated from the author's Codex adaptation under the existing CC BY-NC-SA 4.0 license.
