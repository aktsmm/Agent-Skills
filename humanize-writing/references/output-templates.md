# Humanize Writing: Output Templates and Reference Material

This file holds the long-form output templates, anti-patterns, self-scoring rubric, and example prompts for the `humanize-writing` skill. Keep the main SKILL.md lean by linking here for detail.

## Review Output

監査結果は次の形式で返す。検出ゼロの場合でも、温度感、見出し、まとめの最終チェックを書く。

```markdown
## AI-likeness Audit

### High-priority (要修正)

- L42 「つまり、〜」 -> 定型接続詞。削除 or 具体語
  before: つまり、サービス名に近い根拠を優先します。
  after : サービス名に近い根拠を優先する、という順番です。

### Medium

- L58-L62 文末「〜でした」x4 連続 -> 一部崩す

### Low (任意)

- L110 「かなり読みやすい」 -> 具体数値があれば置換

### Structure

- 見出し語尾: 8 箇所中 7 箇所が「〜した」 -> 1 箇所変える
- 段落長: 全段落 3-4 文で均一 -> 短段落を 2 つ混ぜる
```

## Rewrite Output

- 原則は before / after で返す
- 長文を丸ごと直す場合は、変更理由を先に短くまとめ、本文をその後に出す
- 置換は一括処理しない。`つまり` や `かなり` のような語も、文脈上必要なら残す

## Self-scoring

判断に迷うときは 5 軸で 1-10 点を付ける。合計 35/50 未満は再修正の合図。

- 立場 — 反証可能な具体的主張があるか
- リズム — 文長と段落長にムラがあるか
- 主体性 — 誰がやって何を判断したかが読めるか
- 具体性 — 抽象語ではなく固有名・数字・場面が出ているか
- 削減 — 削っても意味が変わらない文を残していないか

## Anti-patterns

- 全文を機械的に置換する
- 専門用語まで噛み砕き、読者層を無視する
- 絵文字を足して親しみやすく見せる
- 内部資産名や執筆時の判断ログを公開文に並べる
- 事実・感想・意図を 1 文で全部処理する
- 書き手の判断を消し、誰が書いても同じ一般論だけにする
- ユーザーの口癖や署名表現まで矯正する

## Example Prompts

- `この記事のAIっぽさを監査して`
- `humanize this draft`
- `文体チェックだけして、修正はしないで検出だけ出して`
- `生成指示モードで、次の記事の指示プロンプトを作って`
- `つまり・要は・かなり・十分 の残りを全部探して`
- `説明文ではなく、判断の跡が残る文章にして`

## Standard Output Modes

- 監査: `AI-likeness Audit`
- 変換: before / after または修正文
- 生成指示: 文体指示プロンプト
