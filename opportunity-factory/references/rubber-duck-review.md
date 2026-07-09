# Rubber-Duck Review

Use this when the user has an intuition but the factory frame is not yet sharp.

## Question Ladder

Ask only the questions that change the next action.

1. Who exactly has the pain?
2. What do they do today instead?
3. What repeated complaint, workaround, bad review, or spending proves the pain?
4. What is the smallest artifact that can test the riskiest assumption?
5. What would make this idea not worth doing?
6. What platform, legal, privacy, or cost boundary can block it?
7. What metric would make the next cycle obvious?

## Review Frames

| Frame        | What to catch                                                   |
| ------------ | --------------------------------------------------------------- |
| Audience     | Too broad, unreachable, or imaginary user                       |
| Pain         | Nice-to-have disguised as urgent need                           |
| Substitute   | Existing tool already solves it well enough                     |
| Distribution | No believable way to reach first users                          |
| Scope        | MVP still too large for one cycle                               |
| Risk         | Store policy, TOS, privacy, copyright, safety, or payment issue |
| Metric       | Outcome cannot be measured without guessing                     |

## Response Shape

Return the review in this shape:

```markdown
## Sharpest Version

<one sentence opportunity statement>

## Assumptions to Test

- <assumption> -> <how to test>

## Kill Risks

- <risk> -> <early signal>

## First Queue Slice

- discover: <task>
- research: <task>
- build/design: <task>
- review/track: <task>
```

## Opportunity Statement Pattern

```text
For <specific audience> who struggle with <repeated pain>, create <small artifact> that helps them <measurable outcome>, validated by <metric>.
```

## Bias Checks

- If the idea starts from technology, force one pass from user pain.
- If the idea starts from money, force one pass from distribution.
- If the idea starts from a cool mechanic, force one pass from retention or replay value.
- If the idea starts from automation, force one pass from policy and trust risk.

---

# Role-Level Critic Checkpoints (Layer 1: Light Self-Critic)

上のセクションは **opportunity ideation review** (workspace 全体の meta critic)。ここから下は **4 role の各 final-decision 前** に走らせる短い self-critic checkpoint。1 role あたり最大 5 質問、通常 1-2 分の pause だけ。全 role で共通の判定枠。

## Layer 位置付け

| Layer                         | 実行者                                      | 起動タイミング                                                                                       | 出力                                             | 詳細                                           |
| ----------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------- |
| **Layer 1 Light Self-Critic** | 各 role 自身 (context 内で観点切替)         | 各 role の final decision 前、常時                                                                   | 内部 log (dashboard-state.critic-log に summary) | 本ページ                                       |
| **Layer 2 Advisory Critic**   | Critic role invocation (rubber-duck 深掘り) | Fallback lane #3、Persistence Exhaustive の task                                                     | `critic-report.md` (advisory)                    | Fallback-lane.md #3 参照                       |
| **Layer 3 Blocking Critic**   | Critic role invocation (blocking)           | 重要 gate: portfolio promote / focus theme apply / prompt-self-improvement commit / external publish | `critic-report.md` (blocking, verdict=pass 必須) | 本ページ末尾 + prompt-self-improvement.md 参照 |

- Advisory は verdict = reject でも proceed 可、log 化必須
- Blocking は verdict = pass 以外は proceed 不可、user 明示 override は security-approve 経由

## Role 別 Checkpoint (Layer 1)

### Commander (task selection bias check)

Final task dispatch 前に自問:

1. この task は north-star / focus theme に照らして今 top priority か? 他の候補と比較したか?
2. Portfolio Top-N に対して機会損失を起こしていないか?
3. Persistence profile は task class に妥当か?
4. Anti-pattern registry の同一 fingerprint を warn していないか?
5. Fallback lane #3 (advisory critic) を過去 5 サイクル呼んだか? (呼んでなければ dispatch 対象に加える)

### Worker (approach sanity check)

Final artifact commit / handoff 前に自問:

1. 選んだ approach は anti-pattern registry の count=3 に触れないか? (触れるなら別 approach)
2. Reversible な操作か? Backup-First 手順は取ったか?
3. Real-surface で verify 可能か? mock だけで完了扱いにしていないか?
4. Approval bucket は auto か security か? security ならなぜ user 承認を skip して commit しようとしているか?
5. Attempt-log に verdict と evidenceRef を記録したか?

### Reporter-Learner (confirm bias check)

Learning append 前に自問:

1. 成功事例だけを拾っていないか? 直近 failure fingerprint を registry に反映したか?
2. Evidence は "実測 / 推定 / 仮説" に分けたか?
3. Next queue seed は learning から演繹しているか? それとも既存 candidate の焼き直しか?
4. Diminishing returns / persistence 閾値超過を見落としていないか?
5. Critic verdict (Layer 2/3) を learning materials に統合したか?

### Workflow-Review (meta critic)

Cadence / prompt / gate 変更提案前に自問:

1. 提案は直近 3 サイクル以上の evidence を持つか? (単発の思いつきではないか)
2. 外部 evidence (別 workspace / documented pattern / benchmark) を 1 件以上参照したか?
3. 変更は reversible か? Rollback 手順を pair で用意したか?
4. Critic-log の verdict 分布を分析したか? (Rubric 調整の signal がないか)
5. 変更 apply 後の smoke test / validate script pass を必須にしたか?

## Layer 1 Output Contract

各 role は checkpoint 完了で `dashboard-state.critic-log` に append:

```json
{
  "ts": "ISO-8601",
  "layer": 1,
  "role": "commander|worker|reporter-learner|workflow-review",
  "task_id": "...",
  "questions_passed": 5,
  "questions_failed": [],
  "verdict": "proceed|revise|escalate-to-layer2",
  "note": "short"
}
```

- Verdict = `proceed`: そのまま次アクション
- Verdict = `revise`: role 内で 1 回だけ再検討、再 checkpoint
- Verdict = `escalate-to-layer2`: fallback lane #3 (Critic Role invocation) を明示 request

## Layer 3 Blocking Critic (重要 gate) — SSOT

**このリストが Layer 3 blocking gate の SSOT**。他 references (tunable-defaults.md, prompt-self-improvement.md, workspace-setup.md, SKILL.md) はこの節を参照する。gate 追加/変更は本節でのみ行う。

以下の task は Layer 3 を **必ず経由** させる (Layer 1 だけでは不十分):

- Portfolio candidate の **promote** (Top-N 昇格)
- **Focus theme apply** (3 ヶ月更新の確定 — 期間は tunable、apply gate は **hard rule**)
- **Prompt self-improvement の commit** (壊れた prompt 抑止)
- **External publish** 承認直前 (Marketplace / npm / SNS 等)
- **Small-Bet Pilot → 本実装 昇格**

上記 5 種は **hard rule** (変更禁止)。詳細: `references/tunable-defaults.md` の Hard Rule 一覧。

### Layer 3 契約

- Critic Role を新規 context (chat thread 分離 or subagent) で起動
- Input: 対象 artifact + 判定 rubric (下記) + 関連 anti-pattern entries
- Output: `critic-report.md` (verdict: pass | reject | conditional)
- Verdict = `pass`: proceed
- Verdict = `reject`: task 停止、`security-approve` 経由で user override 可
- Verdict = `conditional`: 修正条件明示、worker が対応してから re-critic

### Rubric (severity 5 段階)

**段階名 (info/minor/major/critical/blocking) は hard rule** (verdict 比較保護のため変更禁止)。各段階の**判定基準**は tunable、workflow-review が調整可。

| Severity     | 基準                           | Verdict 影響 |
| ------------ | ------------------------------ | ------------ |
| **info**     | 参考情報、改善余地             | pass 可      |
| **minor**    | 軽微、非阻害                   | pass 可      |
| **major**    | 修正推奨、非致命               | conditional  |
| **critical** | 修正必須、実害あり             | reject       |
| **blocking** | 反対理由あり、進めるべきでない | reject       |

- Critic は severity 分布を artifact 末尾に必ず出力
- Workflow-review が critic-log の severity 分布を追跡し、rubric 調整の signal を検出

## Independence 契約 (Layer 2/3)

同じ LLM が producer と critic を演じても、context 分離が不十分だと bias が残る。

- Critic dispatch 時は **完全に新規 context** (chat thread 切替 or subagent 呼び出し) で起動
- Persistence = Exhaustive の task では **duck-critic skill 経由の別モデル critic** を default
- Layer 3 では別モデル critic を強く推奨 (可能なら必須)
- Critic verdict は producer の context には戻さない、`critic-report.md` を artifact として handoff

## Iteration 抑制

Layer 1 は毎 role 1 回、Layer 2 は fallback lane #3 経由、Layer 3 は 5 gate のみ。iteration 倍増を避けるため:

- Layer 1 は 1-5 質問だけ、深掘りしない
- Layer 2 は 1 artifact に 1 回だけ (再 critic は artifact hash 変更時のみ)
- Layer 3 は上記 5 gate に限定、他 task は Layer 1 / 2 で完結
- Blocker Test (fallback-lane.md 参照) の 4 問 gate は Layer 1 と別、blocker 認定専用

## Override (Layer 3 blocking)

Blocking verdict = reject でも user は override 可:

1. User が `override --reason "..."` を dashboard 経由で送る
2. Approval log と critic-log 両方に reject verdict + override reason を残す
3. Override 後の task は特別 tag `overridden-critic-reject` で追跡
4. Workflow-review が override 頻度を監視 (5% 超過で rubric 見直し提案)

## Log Retention

- Layer 1 log: 30 日で rotation (直近だけ意味あり)
- Layer 2/3 critic-report: 90 日、archive に押し出す
- Rubric 調整 event: 恒久 (workflow-review 学習資産)

## See Also

- `references/fallback-lane.md`: Layer 2 (fallback lane #3 Advisory Critic)
- `references/persistence-profile.md`: Exhaustive task の critic 強制
- `references/prompt-self-improvement.md`: Layer 3 commit gate
- `references/approval-policy.md`: security-approve 経由 override
- `assets/prompts/*.md`: 各 role prompt に Layer 1 checkpoint を埋め込む
