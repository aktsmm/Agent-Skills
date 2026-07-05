# Loop Control: Stop 条件 / Replan / Small-Bet-First / Reflection / Escalation

Phase 6 の詳細。ループが「必ず止まる」「同じ失敗を繰り返さない」「大事故を起こさない」ための仕組み。

## 多層 Stop 条件（MANDATORY）

max iteration だけに頼らない。次のどれか 1 つでも該当したらループを止める/分岐する。

| 種類                | 判定                                          | アクション      |
| ------------------- | --------------------------------------------- | --------------- |
| 収束                | 全 must 基準 PASS かつ confidence ≥ 閾値      | 完了（Phase 7） |
| stall               | `stall_counter` が profile の `stall→replan` 閾値に到達 | replan          |
| oscillation         | 同一 `(action, target)` を繰り返している      | replan か HITL  |
| diminishing returns | 改善幅が ε 未満で連続                         | HITL            |
| budget              | max iteration / 時間 / コスト 上限超過        | HITL            |
| confidence 低迷     | 改善しても閾値に届かない見込み                | HITL            |

`stall_counter` の更新: そのループで「PASS した基準が 1 つも増えず、gap も縮まなかった」なら +1、
前進があれば 0 にリセット。

## Persistence Profile（粘り強さ）

Phase 1 で retry budget を明示する。どの profile でも同じ approach の反復、criteria の弱体化、検証の甘化は禁止。

| profile    | 用途                         | max iteration | stall→replan | replan→HITL | blocker 判定前の別 approach | diminishing returns |
| ---------- | ---------------------------- | ------------- | ------------ | ----------- | ---------------------------- | ------------------- |
| Standard   | 通常の中規模作業             | 12            | 4            | 4           | 4                            | 2 連続              |
| Persistent | なるべく何度も試したい作業   | 20            | 5            | 5           | 6                            | 3 連続              |
| Exhaustive | 長期・重要・難所のやり切り   | 30            | 6            | 6           | 8                            | 4 連続              |

既定は **Persistent**。些末・低リスクは Standard へ下げてよい。Exhaustive は durable ledger 推奨。
時間・コスト・外部操作の budget が先に尽きた場合は profile より budget を優先する。

## Replan（stall / oscillation 時）

worker を増やす前に **計画そのものを疑う**（Magentic-One の task ledger 再構築に相当）。

1. Task Ledger の「確定した事実」と「未確定の推測」を見直す。失敗は推測が外れたサインのことが多い。
2. 分解の粒度・順序・前提を組み替える（別アプローチ）。
3. 新しいサブゴール列で Phase 2 からやり直す。
4. それでも profile の `replan→HITL` 回数まで replan して進まなければ HITL。

（しきい値は粘り寄りの既定。もっと粘らせたい/早く上げたい場合は Phase 1 でユーザーと調整してよい。）

## Dynamic Steering（サブゴール変更）

replan でサブゴール列を変えるときは、criteria を緩めるのでなく steering として扱う。

許可する mutation:

- `add_subgoal`
- `split_subgoal`
- `reorder_pending`
- `revise_pending_wording`
- `annotate_ledger`
- `mark_blocked_superseded`

Steering invariants:

- original brief、Acceptance Criteria、must NOT、quality gate、completion status は変更しない。
- hard-delete / auto-complete / verification 弱体化 / silent mutation は禁止。
- accepted / rejected の両方を ledger に証跡付きで残す。
- `superseded` goal は scheduling から外してよいが、監査可能な状態で残す。
- replacements なしの `blocked` は final completion をブロックする。

## Small-Bet-First（大きな変更の前に）

「全体に適用してから失敗に気づく」事故を防ぐ。

**大きい変更の判定**（どれか該当で small-bet 必須）:

- 多数ファイルへの一括変更 / 一括置換
- 不可逆・破壊的操作（削除・移動・スキーマ変更・本番反映）
- 新規依存の追加
- 広範囲に波及する設計変更

**手順**:

1. **Backup-first**: 破壊的変更なら、可能な限り先に backup を取る（git branch/stash/commit、ファイル copy、
   DB dump/snapshot、export）。backup の場所と戻し方を ledger に記録する。戻せるなら Autonomy Mode に関わらず進めてよい。
2. **pilot**: worker が最小スコープ（1 ファイル / 1 ケース / dry-run）でだけ変更する。
3. **verify**: worker / verifier がその pilot に Phase 1 の `verify:` を実行し、exit code と実出力を orchestrator へ返す。
4. **判定**:
   - PASS → 同じパターンを残りへ展開（独立なら並列）。
   - FAIL → **本適用しない**。reflection → approach 変更 → 別の小さい pilot から。

低リスク・小規模変更では pilot 省略可（Effort Scaling）。

## Reflection（外部 signal 起点）

未達かつ前進している（`making_progress=true`）ときの再試行は、必ず次を満たす:

1. **失敗した検証出力（外部 signal）を起点**にする。「なんとなく直す」をしない。
2. 「何を仮定し / 何が観測され / どこがズレたか」を 1–3 行で言語化する。
3. その教訓を **attempt 教訓 table**（[./ledger-templates.md](./ledger-templates.md)）へ記録する。
4. **同じ approach を 2 回繰り返さない**。table に既出なら別手を選ぶ。

自己評価だけ（外部 signal 無し）の reflection で再試行しない — 改善せず劣化することがある。

## Genuine Blocker の判定（粘る vs 上げる）

HITL トリガー3「自力解決の見込みが立たない」を主観で決めない。**本物のブロッカー = 自分が制御
できない外的・構造的な障害**。次のテストで切り分ける。

### Blocker Test（4 問。エスカレーション前に必ず通す）

1. 失敗は **外部 signal（verify 出力）** で確認したか？（勘・推測だけなら blocker ではない）
2. profile で定めた数以上の **異なる approach** を試したか？（attempt 教訓 table で確認。同じ手の反復は blocker でない）
3. **replan（再分解）** も試して進まなかったか？
4. 残った障害は **自分が制御できない**ものか？

4 問すべて Yes → 本物のブロッカー → HITL。1 つでも No → まだ粘る（replan / 別 approach / reflection）。

final gate や independent review が non-clean の場合は、即 HITL ではなく `review_blocked` にして
blocker 解消サブゴールを追加できないか先に見る。自力で解消できる blocker はループ内で処理する。

### 本物のブロッカー（→ HITL。これ以上ループしても解けない）

| 種類                 | 例                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| 権限・アクセス不足   | 認証情報が無い / 権限不足 / 対象リソースに到達できない                                           |
| 情報・入力の欠落     | 判断に要る事実が存在せず調査でも得られない（ユーザーしか知らない値・未定義仕様）                 |
| 仕様・物理的に不可能 | criteria が技術的に矛盾 / 外部制約で達成不能（※緩和可なら Escalation 表の「criteria 再定義」へ） |
| 外部依存待ち         | 第三者の承認・レビュー・システム復旧待ちで自分の操作では進まない                                 |

（「不可逆・破壊的操作が必要」「criteria の変更が必要」は別トリガー。Blocker Test ではなく
下の Escalation 表（Autonomy Mode 依存）で扱う。）

### 本物のブロッカーでない（→ 粘る。上げない）

- まだ試していない別アプローチがある
- 同じ手を繰り返しているだけ（→ oscillation 検知 → replan）
- エラーメッセージを読めば直せる（→ reflection）
- 一時的失敗（ネットワーク等、リトライで直る）

## Escalation（HITL） — Autonomy Mode で変わる

criteria 合意後は自律で回す。人へ上げるか自律で進めるかは、Phase 1 で合意した Autonomy Mode（Normal /
超自律 AUTO・FULL・ALL）に従う。**起動時にモードが明示されていなければ Phase 1 で聞く**。

| 状況                                 | Normal（既定）                | 超自律（AUTO / FULL / ALL）                           |
| ------------------------------------ | ----------------------------- | ----------------------------------------------------- |
| backup を取れる破壊的操作            | backup→自律実行（止まらない） | backup→自律実行                                       |
| backup 不能の不可逆操作              | **HITL**                      | 実行可（許可済み範囲のみ。rollback 不能を明記しログ） |
| criteria の緩和・再定義              | **HITL（再合意）**            | 自分で緩和/再定義し、記録+通知して継続                |
| `verify:` 検証手段の修正             | 常に自由（止まらない）        | 常に自由（止まらない）                                |
| 本物のブロッカー（Blocker Test 4/4） | **HITL**                      | **HITL**（外的障害は自力で解けない）                  |

補足:

- **Backup-first** を必ず先に試す。backup を取れた破壊的操作は Normal でも自律実行してよい（「戻せる」から）。
- **verify 手段の修正は criteria 変更ではない**。どちらのモードでも止まらず直す。ただし「何を満たせば達成か」の意味は変えない。
- **安全弁は Autonomy Mode より優先**する。超自律でも **秘密情報の露出・個人情報の公開・未許可の外部公開は対象外**
  （別途明示許可）。must NOT と達成の偽装禁止も維持。
- 超自律で criteria を緩和・再定義した場合、完了報告では original criteria と revised criteria の達成状態を分けて示す。

HITL または自律実行時に示す/残すもの:

- 現状（Progress Ledger の要約：満たした基準 / 残 gap）
- 試した approach と失敗理由（attempt 教訓 table）
- （HITL 時）推奨案と選択肢（A/B/C）とトレードオフ、ユーザー判断が要る具体ポイント
- （自律実行時）取った backup の場所と戻し方、緩和した criteria とその理由
