# Evaluation Rubric と Judge Bias 対策

Phase 5（評価）で使う。評価の信頼性が低いとループ全体が壊れるので、ここを厳格にする。

## 大原則：外部検証が一次、LLM 評価は補助

- 自動検証できる基準は、必ず Phase 4 の `verify:` 出力（exit code・実ログ）で判定する。
- LLM 評価は、検証コマンドが書けない基準（主観品質）と、外部検証結果の **解釈・統合**にだけ使う。
- 自己評価だけで PASS を出さない。外部 signal が無い反省は精度を下げうる。

## Rubric の作り方

各受入基準について次を用意する:

```markdown
### AC<n>: <基準名>

- 満たす条件: <PASS とみなす具体状態>
- 反例（FAIL の例）: <これらが見えたら FAIL>
- 判定の根拠にする検証: <Phase 4 のどのコマンド出力を見るか>
- reference（任意）: <理想の出力例 / 既知の正解>
```

判定は基準ごとに `PASS | FAIL` + 根拠（どの検証結果に基づくか）+ gap（不足点）を出す。

## 総合判定ルール

- **全体 PASS = すべての must 基準が PASS、かつ confidence ≥ 閾値**。
- must でない（nice-to-have）基準は記録するが、合否は must で決める。
- 曖昧・判断がつかない・同点 → PASS にしない。Phase 6 の HITL へ回す。

## Judge Bias と対策（LLM 評価を使うとき）

LLM-as-judge には系統的バイアスがある。次で抑える。

| バイアス         | 症状                       | 対策                                                          |
| ---------------- | -------------------------- | ------------------------------------------------------------- |
| self-enhancement | 自分が作った出力を甘く採点 | 生成と評価のロール/subagent を分ける。別 system prompt で評価 |
| position bias    | 比較で先（または後）を優遇 | pairwise の提示順を randomize、両順で評価                     |
| verbosity bias   | 長い出力を高評価           | 長さでなく rubric 充足だけを見ると明示。簡潔さを criteria 化  |
| leniency         | とりあえず PASS にしがち   | 反例リストと confidence 閾値で甘い PASS を弾く                |

## 評価を別 subagent にするとき

- evaluator subagent には **成果物 + rubric + Phase 4 検証出力**だけ渡す（生成過程は渡さない）。
- 「あなたは生成者ではなく審査員。rubric の反例に該当しないかを探せ」と役割を固定する。
- 出力フォーマットを固定する: 基準ごとに `PASS/FAIL`・根拠・gap、最後に総合 `PASS/FAIL`・confidence。

## confidence の扱い

- confidence は「criteria を本当に満たしている確度」。検証が決定論的（exit code）なら高い。
- LLM 判断に依存する部分が多いほど下げる。閾値未満は未達扱いでループ継続 or HITL。
