---
name: humanize-writing
description: "AIっぽい文章を人間らしいトーンに直す／最初から書かせるSkill。日本語（Qiita/WordPress/note）と英語（Medium）に対応。定型接続詞・抽象語・整いすぎた文型・書き出し連発・過剰em-dashなど既知シグナルを検出して置換する。Use when: 原稿レビュー、AIっぽさ監査、Humanize、文体チェック、AI感を消したい、ChatGPT tells。"
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Humanize Writing

AI生成っぽさを検出して、人間らしい文章に直すSkill。

## When to Use

- 原稿の **AIっぽさ監査**（レビュー型）
- **最初から人間らしく書かせる**（生成指示型）
- 日本語記事（Qiita / WordPress / note）、英語記事（Medium）、技術ドキュメント・README
- キーワード: `AIっぽさ`, `humanize`, `人間らしく`, `文体チェック`, `AI感`, `ChatGPT tells`

## 関連 Instruction（任意）

このSkillは**単体で完結**する（他ファイルへの依存なし）。

ワークスペースに文体ルールを常時適用したい場合は、`.github/instructions/writing-style.md` のような instruction を併用するとよい（任意）。

Skill と instructions の棲み分け:
- **instructions**: 記事を書く全工程で常に適用されるルール（文体ポリシー）
- **SKILL.md**: AI文監査・変換という **特定タスク** の手順書（このファイル）

## Done Criteria

**レビュー型**:
- [ ] 検出された問題箇所を行番号／引用付きで列挙
- [ ] 各問題に「カテゴリ」「置換案」を付ける
- [ ] 温度感（敬体／常体／絵文字）が記事全体で一貫していることを確認
- [ ] 最終版に `つまり` / `要は` / `かなり` / `十分` / `実は` などの要注意語が残っていない、または意図的であると説明できる

**生成指示型**:
- [ ] 同じ書き出しの文が3連続しない
- [ ] 抽象語ではなく具体語で書く
- [ ] 体験と引用が主語レベルで分かれている（自分がやった／AIにやらせた／公式ドキュメントからの引用 を混同しない）

## Permissions

- ✅ `.md` 原稿の読み取り・編集・差分提案
- ❌ 文意の捏造・事実の追加（文体だけ直す）
- ❌ 未検証の断定語への書き換え

---

## Phase 1: スキャン（検出）

原稿から次のシグナルを列挙する。**検出は厳密に、修正は文脈判断で**。

### 日本語シグナル（高優先）

| カテゴリ | パターン | 置換方針 |
|---|---|---|
| 定型接続詞 | `つまり、` `要は` `言い換えると` `すなわち` | 削除、または具体語へ |
| 空虚な断定 | `かなり` `十分` `しっかり` `着実に` `安定して` | 数値・具体描写へ。NG多用 |
| 定型構文 | `〇〇そのものではなく△△すること` `〇〇というわけではなく` | 事実に沿って書き直す |
| 定型導入 | `実は〜なのです` `〜してみませんか？` | 削除 |
| 冗長助動詞 | `〜ということができます` `〜することが可能です` | `〜できます` |
| 過剰謙遜 | `〜かもしれません` の乱用 | 事実なら言い切る |
| 同じ文末連続 | `〜でした。` が3連続以上 | 一部を常体・体言止め・倒置に |
| 同じ書き出し連続 | `今回は`〜/`今回の`〜 が3連続 | 主語・視点を変える |
| 抽象名詞多用 | `重要性` `可能性` `効率化` `最適化` `活用` | 具体の動詞・名詞へ |
| 章末定型 | `いかがでしたか？` `この記事が〜の助けになれば` | 削除／体験ベースに |
| pivot構文 | `〇〇ではなく△△` `〇〇というより△△` | 読者視点で対比が成立するか検証。成立しなければ一文で言い切る |
| 章立て予告 | 冒頭で「この記事では次の流れで見ていきます」+ `1.〜N.` 列挙 | TL;DR と H2 目次で二重化。削除し 1 行導入に圧縮 |
| 教訓風総括段落 | 節末の「ここでの学びはシンプルで、〜ことでした」「一番のポイントは〜ことでした」 | 動詞に溶かすか削除して結論を直結 |
| 説教締め | まとめ末の「〇〇な人でも、まずは〜くらいの使い方からでも十分助かりました」 | 著者の予告・次の行動・主観で閉じる |
| 節冒頭テンプレ | 「〇〇だけだと△△までは届きません。ここも AI に任せました」 | 導入を落とし、指示内容から直入り |
| 見出し復唱 | H2/H3 直後の「ここが一番効いたポイントでした」 | 削除。見出しで言ったことは本文で繰り返さない |
| ポイント専用節 | 「試行錯誤で効いたコツ」「ここが効いた」の H2 独立 | まとめ節に吸収 |
| 当たり前解説 | コード/表直後の「こうしておくと〜が分かります」「〇〇だと把握しづらいです」 | 削除 |
| 内部資産列挙 | `SSOT` `handbook` `playbook` `checklist` `運営メモ` などの内部資産名を棚卸しする | 公開文では一覧化せず、「何がやりやすくなったか」に圧縮 |
| 便利語口癖化 | `一気に` `強い` `助かる` `そのまま` `しっかり` が同記事に3回以上 | 半分以上を削除または具体語に置換 |
| コア論点ずれ | TL;DR／振り返り節／まとめで「主な争点／答え」の語彙が一致しない | 3 箇所で同じ語彙を使う |
| オチ見出し | Step/章タイトルに「〜で全体像を掴む」「〜まで持っていく」「〜ラベル化したら読めるようになった」「〜実用的になる」など結果/教訓/感嘆を入れる | 見出しは**動作の目的**だけを名詞句/短い動詞句で（例: 「Python で可視化する」「IP にラベルを付ける」「Markdown レポートにまとめる」） |
| 余談マーカー見出し | 「ちなみに〜」「実際にやってみた感想」「やってみたら〜だった」の口語前置き | 「補足」「感想」「〇〇ではない」等の短い名詞句、または節ごと削除 |

### 英語シグナル（高優先）

| カテゴリ | パターン | 置換方針 |
|---|---|---|
| Buzz nouns | `delve`, `tapestry`, `realm`, `landscape`, `testament`, `paramount`, `cornerstone`, `beacon`, `symphony`, `crucible`, `nuance`, `intricacies` | 具体名詞へ |
| Buzz verbs | `embark`, `unleash`, `unlock`, `harness`, `leverage`, `navigate`, `foster`, `streamline`, `empower`, `elevate`, `orchestrate`, `bolster`, `cultivate` | 普通の動詞へ |
| Buzz adjectives | `ever-evolving`, `seamless`, `robust`, `cutting-edge`, `game-changing`, `transformative`, `unparalleled`, `pivotal`, `holistic`, `multifaceted`, `meticulous` | 事実の描写へ |
| Filler openers | `In today's fast-paced world`, `In the rapidly evolving world of`, `In the ever-changing landscape of`, `It is important to note that`, `It's worth noting that`, `At its core` | 削除 |
| Exploratory openers | `Let's explore`, `Let's dive into`, `Let's take a closer look at`, `Let's unpack`, `step-by-step guide` | 削除 or 題材名から書き始める |
| Pivot constructions | `Not just X but Y`, `X isn't just Y, it's Z`, `It's not about X, it's about Y`, `Rather than X, consider Y` | 一文で言い切る |
| Parallel triples | `A, B, and C` が段落ごとに反復 | 1〜2個は崩す |
| Em-dash 多用 | 段落内 `—` が 2 回以上 | 句点・括弧に置換 |
| Hedge stacking | `can`, `may`, `might`, `could`, `potentially`, `arguably` の連鎖 | 断定可なら断定 |
| Transition tells | `Furthermore,`, `Moreover,`, `Additionally,`, `That said,`, `Having said that,`, `As we've seen,` の乱用 | 削除 or `Also,` |
| Conclusion tell | `In conclusion,`, `Ultimately,`, `To sum it all up,`, `In a nutshell,`, `All in all,` の多用 | 削除 |
| Engagement tell | `I hope this helps!`, `Feel free to reach out`, `Happy coding!` をテンプレで付ける | 本物の一言に差し替え |
| Rhetorical Q | `But what does this really mean?`, `Why does this matter?` | 具体主張に |
| Throat-clearing | `Before we dive in,`, `With that out of the way,` | 削除 |
| Emoji-heading | 見出し先頭の 🚀 ✨ 🔥 が毎節 | 必要な節だけ残す |

### 構造シグナル（言語共通）

- 段落の長さが**均一すぎる**（AIは揃えがち）→ 1-2 文の短段落を混ぜる
- 見出しの語尾が**毎回同じ**（例: 全部「〜する」）→ 少なくとも1つは変える
- 箇条書きが**常に3点or5点**で統一 → 実際に必要な数でよい
- ヘッダー下の**導入文が毎回1文**→ 不要な段は削る
- 公開向けの段落で**内部構造の説明が長すぎる** → 何を管理したかではなく、読者が受け取る効果へ圧縮する

### 体験談シグナル（writing-style 3 連携）

- 自分主語と AI 主語の混同 → L1「自分がやった」vs「AIにやらせた」の分離
- 結果だけ書いて改善プロセスが欠落 → プロセスごと書く
- 実体験と AI が Web 検索で補充した知識の混同 → 分離して明記

---

## Phase 2: 出力（検出レポート）

Phase 1 の検出結果を次の形式で返す。

```markdown
## AI-likeness Audit

### High-priority (要修正)
- L42 「つまり、〜」→ 定型接続詞。削除 or 具体語
  before: つまり、サービス名に近い根拠を優先します。
  after : サービス名に近い根拠を優先する、という順番です。

### Medium
- L58-62 文末「〜でした」×4 連続 → 一部崩す

### Low (任意)
- L110 「かなり読みやすい」→ 具体数値があれば置換

### 構造
- 見出し語尾: 8箇所中7箇所が「〜した」→ 1箇所変える
- 段落長: 全段落 3-4 文で均一 → 短段落を2つ混ぜる
```

**検出ゼロの場合でも**、温度感の揃い具合（TL;DR / 見出し / まとめ）を最終チェックする。

---

## Phase 3: 変換（修正モード）

ユーザーが「直して」と言ったら、差分で提案する。**一括置換はしない**（文脈で適否が変わる）。

原則:

1. 文意・事実を変えない
2. 断定を増やす場合は根拠が既存本文にあるときだけ
3. 敬体／常体は**既存優勢**に合わせる
4. 絵文字・顔文字は既存と同密度（増やさない／減らさない）

---

## Phase 4: 生成指示（書かせるモード）

**最初から人間らしく書かせる**場合、プロンプトに次を添える。

```markdown
## 文体指示

- 1 文 1 アイデア。長い文は切る
- 同じ書き出し・同じ文末を3連続させない
- 「つまり」「要は」「かなり」「十分」「実は」は使わない
- 抽象語（重要性・効率化・活用）より具体動詞を選ぶ
- handbook / playbook / checklist / SSOT などの内部資産名を、そのまま公開文に列挙しない
- 何を管理したかより、何がやりやすくなったかを書く
- 英語の場合: delve / tapestry / realm / leverage / ever-evolving / seamless / robust / embark / unlock / harness を使わない
- 英語の場合: `Let's explore` / `Let's dive into` / `step-by-step guide` で書き出さない
- 英語の場合: `Furthermore` / `Moreover` / `That said` / `In conclusion` / `Ultimately` を使わない
- 英語の場合: `Not just X but Y` / `It's not about X, it's about Y` 構文を避ける
- 英語の場合: 段落内 em-dash（—）は1回まで。挨拶 `I hope this helps!` で締めない
- AI が何をやったか／人間が何をやったかを主語で分ける
```

---

## アンチパターン（このSkillが作らないもの）

- 全文を機械的に置換する（文脈を見ないので破綻する）
- 専門用語まで噛み砕く（読者層を無視しない）
- 絵文字を足して「親しみやすく」する（既存文体を壊す）
- handbook / playbook / checklist / SSOT などの内部資産名を、そのまま公開文に並べる
- ユーザーの口癖・署名表現まで矯正する（「やまぱん」調のような意図的な文体は保護）

---

## Example Prompts

- `この記事のAIっぽさを監査して`
- `humanize this draft`
- `文体チェックだけして、修正はしないで検出だけ出して`
- `生成指示モードで、次の記事の指示プロンプトを作って`
- `つまり・要は・かなり・十分 の残りを全部探して`

---

## Standard Output

**監査結果**（Phase 2 形式のMarkdown）または **差分提案**（before/after）。
どちらを返すかは最初のユーザーメッセージで判定する。
