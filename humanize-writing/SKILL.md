---
name: humanize-writing
description: "Remove AI-generated tone and make writing sound more human in Japanese and English. Use when reviewing drafts for AIっぽさ, humanizing article/blog text, 文体チェック, AI感を消したい, or ChatGPT tells."
argument-hint: "直したい原稿、対象媒体、気になる AI っぽさ"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Humanize Writing

AI 生成っぽさを検出し、人間が書いた文章として読める形へ戻す Skill。

中核は、説明を増やすことではなく、**書き手の判断の跡を戻すこと**。整った正論を並べるより、「なぜそうしたか」「どこを重視したか」が見える文章を優先する。

## When to Use

- 原稿の AI っぽさ監査（レビュー型）
- 原稿の humanize / 文体修正（変換型）
- 最初から人間らしく書かせるための生成指示作成（生成指示型）
- 日本語記事（Qiita / WordPress / note）、英語記事（Medium）、技術ドキュメント、README
- キーワード: `AIっぽさ`, `humanize`, `人間らしく`, `文体チェック`, `AI感`, `ChatGPT tells`

## Scope

- この Skill は監査・変換という特定タスクの手順書。
- 記事を書く全工程で常時効かせる文体ポリシーは `.github/instructions/writing-style.instructions.md` を使う。
- 詳細な tell 辞書は [references/ai-likeness-signals.md](./references/ai-likeness-signals.md) を参照する。
- 生成指示モードの長い追加指示は [references/generation-style-prompt.md](./references/generation-style-prompt.md) を参照する。

## Operating Rules

- 文意・事実を変えない。
- 事実の追加や未検証の断定語への書き換えをしない。
- 断定を増やすのは、根拠が既存本文にある場合だけ。
- 料金、仕様、preview、公開価格の有無など時間で動く話題では、必要に応じて公開 Docs ベースと調査時点を短く明示する。
- 敬体／常体、絵文字、温度感は既存優勢に合わせる。
- ユーザーが過去記事や文例を出した場合は、その voice を優先する。
- 単独の記号、整った文体、丁寧な構成だけで AI 判定しない。複数 tell の cluster として説明できるかを見る。
- 要注意語を機械的に全削除しない。SNS や話し言葉で意図的に効いている語は残してよい。
- プロダクト、課金、契約まわりの用語は、直訳より業界で自然な日本語を優先する。必要なら公式英語を括弧で補う。
- 直した後に、無難な啓発文へ寄りすぎていないか確認する。
- 文体修正だけでは直らない体験不足・判断不足は、捏造せず `【← ここに〜】` のような穴として返す。

## Workflow

1. 入力の目的を判定する。
   - 監査だけ: 問題箇所、カテゴリ、置換案を返す。
   - 直して: before / after か差分案を返す。
   - 生成指示: [generation-style-prompt.md](./references/generation-style-prompt.md) を基準にプロンプトを作る。
2. 媒体と voice を確認する。
   - Qiita / WordPress / note / Medium / README など。
   - 文例があれば、文の長さ、段落長、つなぎ語、句読点、言い切りの強さを合わせる。
3. 次の順でスキャンする。
   - 事実が変わっていないか。
   - 書き手の主語と判断が見えるか。
   - 抽象語やつなぎ語で説明しすぎていないか。
   - 構造が均一すぎないか。
4. 詳細 tell が必要な場合は [ai-likeness-signals.md](./references/ai-likeness-signals.md) を使う。
5. 同じ箇所に複数の tell が重なる場合は `stacking pattern` として 1 件にまとめる。
6. 変換型では初稿後に「まだ AI っぽく見える理由」を短く洗い出し、必要な箇所だけ最終稿で直す。
7. 最後に声に出して読んだとき、同僚や知人にそのまま話せる文かを見る。

## High-priority Signals

- 定型接続詞: `つまり` `要は` `言い換えると` で説明をまとめる。
- 抽象語: `かなり` `十分` `活用` `効率化` `価値` で丸める。
- pivot 構文: `A ではなく B` `A というより B` で観察の代わりに対比を置く。
- 判断ログ露出: `正本として扱う` `今の読み方` など、執筆時の整理を本文へ出す。
- 主語混線: 自分がやったこと、AI にやらせたこと、公式情報からの引用が混ざる。
- 構造の均一化: 段落長、見出し語尾、箇条書き数が揃いすぎる。
- 英語 tell: `delve`, `leverage`, `robust`, `Let's dive into`, `In conclusion`, `Not just X but Y`。

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

- 原則は before / after で返す。
- 長文を丸ごと直す場合は、変更理由を先に短くまとめ、本文をその後に出す。
- 置換は一括処理しない。`つまり` や `かなり` のような語も、文脈上必要なら残す。

## Done Criteria

レビュー型:

- 問題箇所を行番号または引用付きで列挙している。
- 各問題にカテゴリと置換案がある。
- 同じ箇所の重複シグナルを水増ししていない。
- 単独 tell で決めつけず、cluster / stacking pattern として説明できるか確認している。
- 温度感（敬体／常体／絵文字）が記事全体で一貫している。
- 事実、感想、意図が混線していない。
- 一般論ではなく、書き手の判断が読めるか確認している。
- 実測結果、公式ソース、AI が補った整形結果が混ざっていない。

生成・変換型:

- 同じ書き出し・同じ文末が 3 連続していない。
- 抽象語ではなく具体語で書いている。
- 自分がやったこと、AI にやらせたこと、引用したことが主語レベルで分かれている。
- 文例がある場合、その人の voice に寄っている。
- 初稿後に残った AI っぽさを 1 回だけ自己監査し、最終稿で潰している。
- 直した後も、動機・迷い・判断が必要な分だけ残っている。

## Anti-patterns

- 全文を機械的に置換する。
- 専門用語まで噛み砕き、読者層を無視する。
- 絵文字を足して親しみやすく見せる。
- 内部資産名や執筆時の判断ログを公開文に並べる。
- 事実・感想・意図を 1 文で全部処理する。
- 書き手の判断を消し、誰が書いても同じ一般論だけにする。
- ユーザーの口癖や署名表現まで矯正する。

## Example Prompts

- `この記事のAIっぽさを監査して`
- `humanize this draft`
- `文体チェックだけして、修正はしないで検出だけ出して`
- `生成指示モードで、次の記事の指示プロンプトを作って`
- `つまり・要は・かなり・十分 の残りを全部探して`
- `説明文ではなく、判断の跡が残る文章にして`

## Standard Output

- 監査: `AI-likeness Audit`
- 変換: before / after または修正文
- 生成指示: 文体指示プロンプト
