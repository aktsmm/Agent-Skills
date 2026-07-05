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
- 類義語の一対一置換で直した気にならない。特に日本語の `速い` / `早い` は、速度、時期、理解しやすさのどれを言いたいのかを先に分け、必要なら `しやすい` や `早く〜できる` にほどく。
- プロダクト、課金、契約まわりの用語は、直訳より業界で自然な日本語を優先する。必要なら公式英語を括弧で補う。
- 直した後に、無難な啓発文へ寄りすぎていないか確認する。
- 文体修正だけでは直らない体験不足・判断不足は、捏造せず `【← ここに〜】` のような穴として返す。- **自称を三人称ニックネームで呼んだ表現**（`◇◇視点` `◇◇個人の` `◇◇的には`）を見つけたら `振り返り` `個人の` `私は` など中立表現に置き換える。タイトル直下の挨拶・署名だけは認める。ユーザーが「痛い」と感じる長期トリガーなので、一脚でも見逃さない。
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
8. 重要な原稿では、初稿と同じモデルで自己監査して取りこぼしを許容しない場合、**別モデルまたは subagent を skeptic として 1 回走らせる**。同じモデルは自分の出力を褐める傾向があり、副詞偏愛 cluster や TL;DR の取りこぼしが残る（Generator/Evaluator パターン）。

## Fix Order

時間が限られているなら上から順に処理する。下位だけ直しても AI 臭は残る。

1. 立場 — 反証可能な具体的主張があるか。`重要だ` `本質的だ` で終わらせない。
2. 主体 — false agency（モノが主語で人間の動詞）をなくし、誰が何をしたかを書く。
3. 構造 — 命題型 H2、テンプレ序文、ムラの欠如を崩す。
4. 語彙 — 偏愛語、横文字メタファー、副詞スタックを削る。
5. 記号 — 全角ダッシュ、不要な「」、中黒並列、装飾絵文字を整理する。

## High-priority Signals

- 定型接続詞: `つまり` `要は` `言い換えると` で説明をまとめる。
- 抽象語: `かなり` `十分` `活用` `効率化` `価値` で丸める。
- pivot 構文: `A ではなく B` `A というより B` で観察の代わりに対比を置く。
- 抽象比喩の二項対比: `治療になるか加速剤になるか` のように、強い比喩を二択で置いて主張を大きく見せる。何が起きるかをそのまま書けるなら、比喩より現象を優先する。
- 判断ログ露出: `正本として扱う` `今の読み方` など、執筆時の整理を本文へ出す。
- 効果・姿勢の宣言: `効きます` `正面から` `多角的に` `掘り下げる` が、観察や判断の代わりに置かれる。
- **主観動詞型の前振り**: `ここで一気に効いたのが` `ここからが一番ピンと来た話` など、接続詞の代わりに `効いた` `ピンと来た` のような主観動詞を置く。`ここまでの話の核になるのが` `ここで関わってくるのが` などにほどく。
- 主語混線: 自分がやったこと、AI にやらせたこと、公式情報からの引用が混ざる。
- 構造の均一化: 段落長、見出し語尾、箇条書き数が揃いすぎる。
- **副詞偏愛 cluster**: 1 記事内で `個人的に` `本当に` `ちゃんと` `ものすごく` など同じ副詞が **3 回以上**出たら、個々は High でなくても累積で AI 臭になる。箇所リストを作って 3 件以上は减らす。
- 英語 tell: `delve`, `leverage`, `robust`, `Let's dive into`, `In conclusion`, `Not just X but Y`。

## Output

詳細テンプレ（Review / Rewrite / Self-scoring / Anti-patterns / Example Prompts）は [references/output-templates.md](./references/output-templates.md) を参照する。要点だけ:

- 監査: `AI-likeness Audit` 形式で High / Medium / Low + Structure を返す
- 変換: before / after または修正文。一括置換しない
- 生成指示: 文体指示プロンプトを返す（生成指示モード）

## Done Criteria

レビュー型:

- 問題箇所を行番号または引用付きで列挙している
- 各問題にカテゴリと置換案がある
- 同じ箇所の重複シグナルを水増ししていない
- 単独 tell で決めつけず、cluster / stacking pattern として説明できるか確認している
- 温度感（敬体／常体／絵文字）が記事全体で一貫している
- 事実、感想、意図が混線していない
- 一般論ではなく、書き手の判断が読めるか確認している
- 実測結果、公式ソース、AI が補った整形結果が混ざっていない

生成・変換型:

- 同じ書き出し・同じ文末が 3 連続していない
- 抽象語ではなく具体語で書いている
- 自分がやったこと、AI にやらせたこと、引用したことが主語レベルで分かれている
- 文例がある場合、その人の voice に寄っている
- 初稿後に残った AI っぽさを 1 回だけ自己監査し、最終稿で潰している
- 直した後も、動機・迷い・判断が必要な分だけ残っている

## References

- [output-templates.md](./references/output-templates.md) — 出力テンプレ、Self-scoring、Anti-patterns、Example Prompts
- [ai-likeness-signals.md](./references/ai-likeness-signals.md) — 詳細 tell 辞書
- [generation-style-prompt.md](./references/generation-style-prompt.md) — 生成指示モードの追加指示
- [iKora128/stop-ai-slop-jp](https://github.com/iKora128/stop-ai-slop-jp) (MIT) — 修正優先順位と 5 軸採点の発想を参考にした
- [k16shikano/japanese-tech-writing](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d) (Unlicense) — LLM 口調と技術文書の誠実さの観点を参考にした
