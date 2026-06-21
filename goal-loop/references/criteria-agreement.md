# Criteria Agreement テンプレ

Phase 1 でユーザーと合意する内容。合意後は **freeze** する。
Normal ではループ中に自分で緩めない。超自律では `criteria_change` として記録+通知した場合だけ再定義できる。
このテンプレを埋め、合意できたら Task Ledger（[./ledger-templates.md](./ledger-templates.md)）へ転記する。

## なぜ最初に固定するか

evaluator-optimizer ループは「**明確な評価基準があり、反復で測定可能に改善するとき**」だけ有効に働く。
criteria が曖昧だと、評価が当てにならず、ループが収束しない／無駄に回る。だから最初に固定する。

## テンプレ

```markdown
## Goal

<達成状態を 1 文で。「何が」「どうなっていれば」完了か>

## Scope Terminus（終点。曖昧なら実行前に 1 問で確認）

- depth: <source 修正のみ / build まで / ライブ反映まで（例: デプロイして URL が新表示で応答）>
- surface: <アプリのみ / docs のみ / 両方 / 生成物・履歴記録まで含むか>
- naming: <確定した表記をそのまま引用。スペース有無・大小・語順を固定（例: ラベルや製品名の表記揺れ）>

## Grounding

- audience: <誰にとって成功か>
- destination: <どこに反映 / 提出 / 配置されるか>
- baseline: <現状態 / exact failure / starting metric>
- constraints: <時間・範囲・承認・環境・互換性>
- evidence gaps: <まだ裏取りできていないが finish line に影響しうること>

## Acceptance Criteria（各に verify: を必須）

- [ ] AC1: <満たすべき条件>
  - verify: <コマンド or 観測手順。例: `pytest -q` が exit 0 / 画面に X が表示される>
- [ ] AC2: <...>
  - verify: <...>
- [ ] AC3: <...>
  - verify: <...>

## Verification Design

- primary verifier: <最も実際の成功面に近い検証。失敗と成功を分け、次の修正に使える evidence を返すもの>
- supporting checks: <build / unit test / lint / schema / mock / static analysis など補助証跡>
- real surface: <必要なら URL / app / account type / device / starting state / clean-state 手順>
- evidence to capture: <commands, outputs, paths, screenshots, logs, readbacks>
- capability gaps: <tool / account / device / credential / environment が無い場合の handoff>

## Out of Scope（非ゴール）

- <やらないこと>

## must NOT（抜け道の封鎖）

- test を削除・skip して通さない
- 出力を切り詰めて見かけ上 PASS にしない
- TODO / ダミー / ハードコードで基準を偽装しない
- <このゴール固有の禁止近道>

## Constraints

- 触ってよい範囲: <ディレクトリ / ファイル>
- 使ってよい tool: <...>
- 破壊的操作: <可 / 不可 / 要承認>

## Architecture / Domain Invariants（あれば）

- <壊してはいけない設計境界 / データ契約 / 用語定義 / 外部互換性>
- verify: <どの test / grep / review / 観測で守られたと判断するか>

## Ledger Mode

- mode: <conversation / durable>
  - conversation: 会話内の Task / Progress Ledger だけで管理する。
  - durable: 長期・多段・再開前提のときだけ、作業フォルダ配下に brief / plan / event log を置く。

## Autonomy Mode（起動時に明示がなければ聞く）

- mode: <Normal / 超自律（AUTO / FULL / ALL）>
  - Normal: backup を取れる破壊的操作は backup→自律実行。backup 不能の不可逆操作と criteria 変更は HITL。
  - 超自律: 上記に加え、backup 不能の破壊的操作も実行可（Phase 1 の制約で許可済み範囲のみ。rollback 不能は明記）、criteria 緩和・再定義も自分で行い記録+通知して継続。
  - どちらも `verify:` 検証手段の修正は自由。秘密/個人情報の露出・未許可の外部公開は対象外で、安全弁は Autonomy Mode より優先する。
  - 超自律で criteria を改定した場合、完了報告では original criteria と revised criteria の達成状態を分ける。

## Persistence Profile（粘り強さ。起動時に明示がなければ聞く）

- profile: <Standard / Persistent / Exhaustive>
  - Standard: 通常。max iteration 12 / stall→replan 4 / replan→HITL 4 / blocker 前の別 approach 4。
  - Persistent: なるべく何度も試す既定。max iteration 20 / stall→replan 5 / replan→HITL 5 / blocker 前の別 approach 6。
  - Exhaustive: 重要・難所向け。max iteration 30 / stall→replan 6 / replan→HITL 6 / blocker 前の別 approach 8。durable ledger 推奨。
- 明示回答が無い場合は Persistent として Task Ledger に固定する。

## Stop Conditions

- max iteration: <profile 既定 or 明示した上限>
- budget: <時間 / コスト上限があれば>
- confidence 閾値: <例: 0.8。これ未満は PASS としない>
```

## 良い基準の条件

- **検証可能**: 人間や推測でなくコマンド・観測で PASS/FAIL が決まる。
- **二値化できる**: 「良い感じ」ではなく「`build` が exit 0」「リンク 200」のように切れる。
- **実成功面に近い**: UI / browser / app / 認証 / OS 連携が本質なら、mock や unit test だけを primary にしない。
- **intent を含む**: 形式だけ満たして本来の目的を外す抜け道を must NOT で塞ぐ
  （specification gaming / reward hacking 対策）。
- **非ゴールが明示**: スコープ膨張を防ぐ。
- **不変条件が明示**: 大きな変更では「何を変えないか」を先に固定し、最終 gate で証跡を出す。

## 検証手段が無い基準の扱い

自動検証コマンドが書けない基準（主観的な品質など）は:

1. できる限り客観プロキシに置き換える（例: 「読みやすい」→「見出し階層が 3 段以内・1 段落 5 文以内」）。
2. それでも残る主観部分だけ Phase 5 の LLM 評価（rubric + reference）で判定する。
3. 重要かつ主観的なら、Phase 6 の HITL でユーザー確認を必須にする。

## Research Enough

- canonical local source、既存 attempt、test / benchmark / repro、必要な実行 capability を確認する。
- volatile facts が finish line を左右するときだけ一次情報で更新する。
- finish line と primary verifier が支えられたら調査を止める。
- 観測事実、ユーザー要件、推測を混ぜない。
