---
name: opportunity-factory
description: "Run a reusable opportunity-to-artifact workflow: discover unmet needs, set up workspace factories, schedule recurring commander/worker/reporter prompts, batch-refine many items, optionally use SQLite state, build small artifacts, review quality, and track outcomes. Use when the user wants to repeatedly create apps, games, products, content, or experiments from market/user needs."
argument-hint: "対象ドメイン、成果物タイプ、制約、今回の入力"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Opportunity Factory

ニーズ発見から小さな成果物、レビュー、計測、学習までを回す汎用ワークフロー。

## When to Use

- 「ニーズを探して、レビューして、作る」を継続的に回したい
- スマホアプリ、Steam ゲーム、SaaS、教材、社内改善などを量産したい
- アイデアをラバーダックで壁打ちし、実行可能な queue に分解したい
- 単発回答ではなく、反復可能な workspace factory を設計・運用したい
- テーマだけを与えて、workspace、状態管理、定期ワークフロー、レビューゲートを自律設計させたい
- 2〜3 個の定期プロンプトで状態を見ながら継続改善したい
- `/Refine-Product-100 all` のように多数の対象を複数passで改善したい

## When Not to Use

- 1 回だけの実装、調査、レビューなら通常対応でよい
- 常時守るコーディング規約なら instruction にする
- 特定 persona や tool 制限が主目的なら custom agent にする
- deterministic な同期、変換、検証だけなら script / hook にする

## Core Idea

抽象ループは次の通り。

```text
discover -> research -> evaluate -> design -> build -> review -> launch/track -> learn
```

各ループは「次に作るもの」ではなく「どの痛み・需要を検証するか」から始める。

## Workflow

1. **Frame the factory**
   対象ドメイン、成果物タイプ、成功指標、禁止事項を 5 行以内で定義する。
2. **Rubber-duck the intent**
   前提、誰の痛みか、既存代替、最小検証、失敗条件を質問で露出させる。
3. **Design the workspace loop**
   ユーザーがテーマだけを与えた場合は、状態ファイル、dashboard、Top-N/portfolio、候補深掘り、週次 workflow review まで含む自走ループを設計する。
4. **Create the queue**
   作業を `discover|research|evaluate|design|build|review|track|learn` に分ける。
5. **Produce artifacts**
   各 task は 1 つの evidence artifact を残す。判断、根拠、次アクションを分離する。
6. **Run review gates**
   UX、技術、法務/規約、配布、収益/成果指標をドメインに合わせて確認する。
7. **Track outcomes**
   実測、推定、未確認を区別し、当たりだけを次サイクルで厚くする。

## Operating Rules

- 先に「誰のどんな未充足ニーズか」を固定してから解決策を作る。
- 1 task は 1 artifact に収まる粒度にする。
- Advisory-only schedules are safe but too slow for a real factory; if the user expects progress, add at least one bounded mutating worker that writes one artifact and updates local state.
- 複数 worker で回す場合は、discovery/research worker、build/decision worker、reporter-learner など役割を分け、各 run は 1 task / 1 artifact / 明示的 state 更新に制限する。
- 小さい queue では commander/worker を別々にスケジュールせず、1本の single-cycle automation で `commander -> 1 worker -> reducer` を回してよい。ただし auto-eligible task、lock、JSON backup/parse validation が必須。
- Mutating workers need duplicate-run prevention such as a short-lived lock file before they update queue or outcome state.
- Maintain a canonical dashboard/status state for future sessions and user status answers; every workflow that changes artifacts, queues, gates, portfolio ranking, blockers, or schedules must update it with backup + stale-write checks.
- Add a workflow-review loop as a first-class workflow for self-improving factories; it reviews cadence, queue quality, Top-N replacements, dashboard drift, missing gates, and unsafe autonomy at a slower cadence than workers.
- Portfolio factories need a Top-N state with explicit replacement rules; do not grow candidate lists forever, and do not replace an incumbent without comparative evidence and reviewer critique.
- When a selected task hits an approval boundary, record it as blocked with the exact approval needed, then run or create one safe fallback task instead of stalling the factory.
- Do not rely on chat history for factory state; write a README/resume contract that tells future sessions which state, queue, outcome, log, and artifact files to read first.
- Keep prototype/build lanes in the same factory when the user wants end-to-end production, but gate source generation on a structured candidate-level `continue` decision plus an MVP boundary artifact.
- If the current host cannot build-verify the target platform, mark generated code as compile-oriented and verification-blocked; never report it as built, running, or tested without a platform verification artifact.
- 指標は実測、推定、仮説を明示して混ぜない。
- 課金、ログイン、外部公開、個人情報、法的リスクは人間承認の境界にする。
- ワークスペース固有パスや秘密情報を skill 本体へ埋め込まない。

## AI-Autonomous Operation

AUTO 既定。人間承認は `security-approve` バケットのみ。詳細は各 references。

| # | 章 | 骨子 | 詳細 |
| --- | --- | --- | --- |
| A | Approval Policy | 2 バケット (`auto` / `security-approve`)。金銭発生は後者の 1 例。AI usage は skill 対象外。Backup-First で reversible は auto。 | `references/approval-policy.md` |
| B | Autonomy Mode | Normal / **AUTO 既定** / FULL / ALL の 4 段階。setup で mode 未指定なら Phase 1 で聞く。secret 露出等は全 mode で対象外。 | `references/runtime-modes.md` (`ai-autonomous` preset) |
| C | Fallback Lane | blocked/stall/idle 時 10 lane 順次 auto-dequeue (1 Portfolio → 2 Prompt review → 3 Advisory Critic → 4 Anti-pattern → 5 Discovery → 6 Small-Bet → 7 Learning → 8 Cleanup → 9 Real-surface RO → 10 Digest)。Discovery Floor 5 サイクル。browser 書込みは defer。 | `references/fallback-lane.md` |
| D | Genuine Blocker Test | failed/stall で即 blocker 認定せず 4 問 gate (外部 signal 確認 / 別 approach N / replan / 制御不能)。4/4 Yes のみ HITL、以外は fallback へ。 | `references/fallback-lane.md` |
| E | Persistence Profile | Standard / **Persistent (既定)** / Exhaustive。task class 別マッピング。cost/quota は skill 対象外 (adapter 任せ)。worker は自分で approach 増やさず commander が replan。 | `references/persistence-profile.md` |

## Output Modes

- **Rubber Duck**: 質問と仮説の穴を返す。
- **Factory Plan**: roles、queue、artifact contract、review gates を設計する。
- **Workspace Setup**: target surface、state store、prompt runner、schedule、approval policy を決める。
- **Self-Designing Workspace Setup**: ユーザーのテーマから workspace layout、dashboard state、portfolio/Top-N、candidate advancement、idea discovery、workflow review の各ループを設計する。
- **Run Slice**: 直近 1 サイクル分の task と artifact 雛形を作る。
- **Periodic Runtime**: commander / worker / reporter prompts で状態を見て回し続ける。
- **Throughput Setup**: commander、research worker、build/decision worker、weekly reporter のように安全境界付きで分業し、進捗速度を調整する。
- **Prototype Lane**: validated candidates only; create prototype plans, dummy-data source, review/test artifacts, and platform-verification notes under the same workspace.
- **Review**: 既存 factory の詰まり、過剰設計、欠けた gate を指摘する。

## References

- Detailed workflow: [references/workflow.md](references/workflow.md)
- Battle-tested patterns: [references/battle-tested-patterns.md](references/battle-tested-patterns.md)
- Workspace setup: `references/workspace-setup.md`
- Self-designing factory loop: `references/self-designing-factory.md`
- Canonical dashboard state: `references/dashboard-state.md`
- Prompt self-improvement loop: `references/prompt-self-improvement.md`
- Runtime modes and scheduler presets: `references/runtime-modes.md`
- Batch refinement: `references/batch-refinement.md`
- Optional SQLite state store: `references/sqlite-state-store.md`
- Rubber-duck + role-level critic (Layer 1/2/3): [references/rubber-duck-review.md](references/rubber-duck-review.md)
- Approval policy: `references/approval-policy.md`
- Fallback lane + anti-pattern registry: `references/fallback-lane.md`
- Persistence profile: `references/persistence-profile.md`
- Periodic prompts: `assets/prompts/commander.md`, `assets/prompts/worker.md`, `assets/prompts/reporter-learner.md`
- Preflight checklist: `assets/templates/setup-preflight.md`
- Validation script: `scripts/validate_factory_skill.py`
- Workspace initializer: `scripts/init_factory_workspace.py`
- SQLite initializer: `scripts/init_factory_sqlite.py`
- Initializer smoke test: `scripts/smoke_test_initializers.py`
- Setup packet examples: `assets/examples/setup-packets.md`
- Factory plan template: [assets/templates/factory-plan.md](assets/templates/factory-plan.md)
- State template: `assets/templates/factory-state.json`
- Dashboard state template: `assets/templates/dashboard-state.json`
- SQLite schema template: `assets/templates/factory-state.sqlite.sql`
- First-run queue template: `assets/templates/first-run-queue.json`
- Task template: [assets/templates/task.json](assets/templates/task.json)
- Artifact template: [assets/templates/artifact.md](assets/templates/artifact.md)

## Done Criteria

- Primitive choice is still Skill, not prompt/instruction/agent/hook
- Domain, artifact type, success metric, and constraints are explicit
- Target surfaces, state store, prompt runner, schedule capability, and approval boundaries are explicit
- Queue has at least one next executable task
- Every task has an artifact contract and review gate
- Human approval boundaries are named
- A canonical status dashboard or equivalent resume contract exists, and status answers use it first
- Self-improving factories include a scheduled or manual workflow-review loop
- Prompt self-improvements are workspace-local, evidenced by an artifact, reversible, and dashboard-recorded
- Portfolio factories define Top-N capacity, replacement criteria, and demotion/watchlist/rejected states
- If scheduled progress is expected, at least one safe mutating worker exists; advisory-only automation is called out as intentionally slow
- Approval-boundary blockers do not empty the run: the runtime records the blocker and keeps at least one safe fallback lane available
- Future sessions can resume from durable state files without reading the original chat transcript
- Prototype/source-generation tasks require candidate-level continue state, an MVP boundary artifact, dummy data only, WIP limits, and honest platform-verification status
