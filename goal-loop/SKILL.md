---
name: goal-loop
description: "Run an explicit end-to-end goal loop with frozen Scope/criteria, worker delegation, external verification, evaluator review, and bounded retries. Use when the user asks for 'goal-loop', 'ゴールまで回す', '必ずやり遂げる', 'loop until done', 'until it actually works', or an orchestrator + evaluator loop. Do not use for ordinary planning, casual advice, reviews, or small single-file fixes."
argument-hint: "達成したいゴール（成果物・終了条件・制約があれば一緒に）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Goal Loop

合意した Scope と success criteria を満たすまで、worker / verifier / evaluator を使ってゴールをやり遂げる手順書。
このスキルを起動した現在の agent が orchestrator になり、criteria、ledger、evidence reconciliation、次の一手の決定を担う。

## When to Use

- ユーザーが `goal-loop` / `ゴールまで回す` / `必ずやり遂げる` / `loop until done` / `until it actually works` と依頼した。
- 成果物を end-to-end に完成させる必要があり、単発修正ではなく検証・再試行・評価のループが必要。
- worker 生成と evaluator 判定を分ける価値がある、中規模以上または不可逆・多段の作業。

## Do Not Use For

- 1 ファイル・自明・低リスクの修正。通常 agent が直接実行する。
- 普通の相談、計画だけ、コードレビューだけ、事実確認だけ。
- skill / prompt / instruction / agent 自体の設計レビュー。まず `skill-creator-plus` や `agentic-workflow-guide` を使う。

## Core Rules

- **Scope 合意は必須**。Phase 1 で Scope Terminus、Goal、Acceptance Criteria、Primary Verifier、Out of Scope、must NOT、Autonomy Mode、Persistence Profile を合意して freeze する。合意前に実行へ進まない。
- **外部 signal を一次情報にする**。test / lint / build / grep / schema / live surface の exit code や観測結果で判定する。自己評価だけで PASS しない。
- **orchestrator は実作業を抱え込まない**。調査・実装・検証は利用可能な subagent tool（例: `runSubagent` がある環境ではそれ）で worker / verifier に委譲し、delta evidence だけ受け取る。
- **workers は goal state を所有しない**。worker は evidence を返すだけ。checkpoint / complete / blocked 判定は orchestrator が ledger で行う。
- **大きな変更は Small-Bet-First**。backup → pilot → verify → expansion の順で進める。
- **ループは多層 stop で止める**。max iteration だけに頼らず、stall / oscillation / diminishing returns / budget / genuine blocker を見る。

## Phase 1: Scope + Criteria Freeze

Use [criteria-agreement.md](./references/criteria-agreement.md).

- ゴールの終点に幅がある場合は、実行前に選択式の確認を 1 回だけ挟む。
- 各 Acceptance Criteria には `verify:` を必ず付ける。検証不能な基準は検証可能な形に書き直す。
- deploy / runtime / UI / app では、build や control-plane 成功を primary verifier にしない。ユーザーが触れる live surface を primary にする。
- Normal では criteria を自分で緩めない。超自律でも criteria 変更は記録+通知し、original と revised の達成状態を分ける。

## Phase 2: Plan Minimal Subgoals

Use [steering-and-final-gates.md](./references/steering-and-final-gates.md) and [ledger-templates.md](./references/ledger-templates.md).

- Effort Scaling で重さを選び、些末タスクならこの skill から降格する。
- 検証可能な最小サブゴール列へ分解する。
- `pending` / `in_progress` / `complete` / `failed` / `blocked` / `review_blocked` / `superseded` で状態を記録する。
- 独立した read-only 調査だけ並列にし、mutation は直列にする。

## Phase 3: Delegate Workers

Use [loop-control.md](./references/loop-control.md).

- 大きい変更は pilot から始める。FAIL した pilot を全体へ展開しない。
- worker prompt には該当サブゴール、受入基準、境界、禁止事項、過去 attempt の教訓、期待する evidence だけ渡す。
- subagent tool が無い環境では黙って main context で代行しない。小規模へ降格するか degraded mode を ledger に記録して進める。

## Phase 4: External Verification

- worker / verifier が Phase 1 の `verify:` を実行し、exit code と実出力を返す。
- primary verifier が capability gap で実行不能なら、弱い検証で完了扱いにしない。Deferred / Next Actions に手動検証手順と必要 evidence を残す。

## Phase 5: Evaluate

Use [evaluation-rubric.md](./references/evaluation-rubric.md).

- 外部検証の出力を rubric で criteria と項目単位に突合する。
- 小規模・read-only・低リスクを除き、evaluator は worker とは別 subagent にする。
- PASS はすべての must 基準 PASS かつ confidence 閾値以上のときだけ。

## Phase 6: Loop Control

Use [loop-control.md](./references/loop-control.md).

- 未達なら Progress Ledger を更新し、外部 signal 起点で reflection する。
- 前進が止まったら worker 増設ではなく replan する。
- Blocker Test で本物のブロッカーと判定できるまで HITL に逃げない。

## Phase 7: Report or Handoff

- 各 AC の `verify:` 結果、primary verifier、supporting checks を分けて示す。
- 大きな変更では final quality gate と independent review を通す。orchestrator が自分の成果に最終 PASS を出さない。
- Deferred / Next Actions、backup の場所と戻し方、criteria 変更、残リスクを簡潔に報告する。
- 一時ファイルや scratch ledger は cleanup する。途中停止時は再開に必要な ledger state を残す。

## References

- [criteria-agreement.md](./references/criteria-agreement.md): Scope / criteria freeze テンプレ。
- [ledger-templates.md](./references/ledger-templates.md): Task / Progress ledger と attempt table。
- [loop-control.md](./references/loop-control.md): stop、replan、Small-Bet、reflection、HITL。
- [evaluation-rubric.md](./references/evaluation-rubric.md): rubric と judge bias 対策。
- [steering-and-final-gates.md](./references/steering-and-final-gates.md): Effort Scaling、dynamic steering、final gate、worker boundary。
- [design-rationale.md](./references/design-rationale.md): 設計根拠と出典。
