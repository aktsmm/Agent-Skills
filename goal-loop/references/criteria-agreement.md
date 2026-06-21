# Criteria Agreement テンプレ

Phase 1 でユーザーと合意する内容。合意後は **freeze**（ループ中に自分で緩めない）。
このテンプレを埋め、合意できたら Task Ledger（[./ledger-templates.md](./ledger-templates.md)）へ転記する。

## なぜ最初に固定するか

evaluator-optimizer ループは「**明確な評価基準があり、反復で測定可能に改善するとき**」だけ有効に働く。
criteria が曖昧だと、評価が当てにならず、ループが収束しない／無駄に回る。だから最初に固定する。

## テンプレ

```markdown
## Goal

<達成状態を 1 文で。「何が」「どうなっていれば」完了か>

## Acceptance Criteria（各に verify: を必須）

- [ ] AC1: <満たすべき条件>
  - verify: <コマンド or 観測手順。例: `pytest -q` が exit 0 / 画面に X が表示される>
- [ ] AC2: <...>
  - verify: <...>
- [ ] AC3: <...>
  - verify: <...>

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

## Autonomy Mode（起動時に明示がなければ聞く）

- mode: <Normal / 超自律（AUTO / FULL / ALL）>
  - Normal: backup を取れる破壊的操作は backup→自律実行。backup 不能の不可逆操作と criteria 変更は HITL。
  - 超自律: 上記に加え、backup 不能の破壊的操作も実行可（rollback 不能は明記）、criteria 緩和・再定義も自分で行い記録+通知して継続。
  - どちらも `verify:` 検証手段の修正は自由、秘密/個人情報の露出・外部公開は対象外。

## Stop Conditions

- max iteration: <例: 12（粘り寄りの既定。複雑・長期なゴールは 15～、単純なものは 5～8 へ）>
- budget: <時間 / コスト上限があれば>
- confidence 閾値: <例: 0.8。これ未満は PASS としない>
```

## 良い基準の条件

- **検証可能**: 人間や推測でなくコマンド・観測で PASS/FAIL が決まる。
- **二値化できる**: 「良い感じ」ではなく「`build` が exit 0」「リンク 200」のように切れる。
- **intent を含む**: 形式だけ満たして本来の目的を外す抜け道を must NOT で塞ぐ
  （specification gaming / reward hacking 対策）。
- **非ゴールが明示**: スコープ膨張を防ぐ。

## 検証手段が無い基準の扱い

自動検証コマンドが書けない基準（主観的な品質など）は:

1. できる限り客観プロキシに置き換える（例: 「読みやすい」→「見出し階層が 3 段以内・1 段落 5 文以内」）。
2. それでも残る主観部分だけ Phase 5 の LLM 評価（rubric + reference）で判定する。
3. 重要かつ主観的なら、Phase 6 の HITL でユーザー確認を必須にする。
