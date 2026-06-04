# AI-likeness Signals

Humanize Writing の検出辞書。検出は厳密に、修正は文脈判断で行う。

## Scan Priority

1. 事実が変わっていないか
2. 書き手の主語と判断が見えるか
3. 抽象語やつなぎ語で説明しすぎていないか
4. 構造が均一すぎないか

## Japanese Signals

| Category             | Pattern                                                                                                         | Rewrite policy                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 定型接続詞           | `つまり、` `要は` `言い換えると` `すなわち`                                                                     | 削除、または具体語へ                                                                 |
| 空虚な断定・抽象語   | `かなり` `十分` `しっかり` `活用` `効率化` `土台` `価値`                                                        | 数値、具体描写、動作へ戻す                                                           |
| 定型構文             | `〇〇そのものではなく△△すること` `〇〇というわけではなく`                                                       | 事実に沿って一文で書く                                                               |
| 定型導入             | `実は〜なのです` `〜してみませんか？`                                                                           | 削除                                                                                 |
| メタ観察導入         | `面白いのは〜` `印象に残ったのは〜` `気になったのは〜`                                                          | 見えた事実や出典の内容から始める                                                     |
| 冗長助動詞           | `〜ということができます` `〜することが可能です`                                                                 | `〜できます`                                                                         |
| 過剰謙遜             | `〜かもしれません` の乱用                                                                                       | 事実なら言い切る                                                                     |
| soft assertion 連続  | `〜と思います` `〜と感じています` `〜と考えています` が同セクションに 3 回以上                                  | 事実は断定し、主観は 1 回だけ残す                                                    |
| 同じ文末連続         | `〜でした。` が 3 連続以上                                                                                      | 一部を常体、体言止め、倒置にする                                                     |
| 同じ書き出し連続     | `今回は` / `今回の` が 3 連続                                                                                   | 主語や視点を変える                                                                   |
| 章末定型             | `いかがでしたか？` `この記事が〜の助けになれば`                                                                 | 削除、または体験ベースにする                                                         |
| pivot 構文           | `〇〇ではなく△△` `〇〇というより△△`                                                                             | 読者視点で対比が成立するか確認する。成立しなければ一文で言う                         |
| 比較で逃がす要約     | `A より B` `X の話では終わっていない` `単なる〜ではなく`                                                        | 比較を先に立てず、観察した事実を書く                                                 |
| 章立て予告           | 冒頭の「この記事では次の流れで見ていきます」+ `1.〜N.`                                                          | TL;DR と H2 目次の二重化なら削る                                                     |
| 教訓風総括段落       | `ここでの学びはシンプルで、〜ことでした` `一番のポイントは〜ことでした`                                         | 動詞に溶かすか削除する                                                               |
| 判断不在の正論       | 誰が書いても成立する一般論だけが並ぶ                                                                            | 何を重視したか、どこで迷ったか、何を先にやったかを残す                               |
| 観測後の抽象総評     | before / after や検証結果の直後に `期待どおり動きました` `〜と見てよさそうです` で締める                        | 確認できた変化そのもので閉じる                                                       |
| 説教締め             | まとめ末の「まずは〜くらいの使い方からでも十分助かりました」                                                    | 著者の予告、次の行動、主観で閉じる                                                   |
| 節冒頭テンプレ       | `〇〇だけだと△△までは届きません。ここも AI に任せました`                                                        | 指示内容や観察結果から直入りする                                                     |
| 見出し復唱           | H2/H3 直後の「ここが一番効いたポイントでした」                                                                  | 削除。見出しで言ったことを本文で繰り返さない                                         |
| ポイント専用節       | 「試行錯誤で効いたコツ」「ここが効いた」の H2 独立                                                              | まとめ節に吸収する                                                                   |
| 当たり前解説         | コードや表の直後の「こうしておくと〜が分かります」                                                              | 削除                                                                                 |
| 教科書型橋渡し       | `この違いが分かると〜` `ここで重要なのは〜` `大事なのは〜` `〜と覚えておけば、ひとまず十分です`                 | 半数以上を削除。残すなら事実か判断軸で閉じる                                         |
| 予測的足場設営       | 章冒頭の `ここで大事なのは〜です` `〜が考慮すべき点です`                                                        | 予測を削り、本文へ直結させる                                                         |
| 内部資産列挙         | `SSOT` `handbook` `playbook` `checklist` `運営メモ` の棚卸し                                                    | 公開文では一覧化せず、何がやりやすくなったかに圧縮する                               |
| 判断ログ露出         | `この記事では〜として扱う` `正本として扱う` `今の読み方` `この整理がいちばん無理がありません`                   | 公開文では表、注記、本文の事実に吸収する。事実文で終わるなら後続コメントを削る       |
| 便利語口癖化         | `一気に` `強い` `助かる` `そのまま` `しっかり` `土台` が同記事に 3 回以上                                       | 半分以上を削除または具体語に置換する                                                 |
| 整理語で締める       | `前に出ています` `話がつながります` `見えてきます` `腑に落ちます` `いちばんしっくり来ます` `読みやすくなります` | 観察した事実で止める。事実で終わるなら後続の整理コメントは足さない                   |
| 抽象カテゴリ列挙     | `〜面` `足回り` `地図がつながる` `runtime / context / tooling` だけで観察を運ぶ                                 | 具体名詞や動作へ戻す                                                                 |
| 和文と英数字の密着   | `Factory活用` `33件` `WS資料` `2FA(2要素認証)`                                                                  | 本文として読む箇所は境目に半角スペースを入れる。`GH-300` `#49` `1on1` URL は崩さない |
| コア論点ずれ         | TL;DR、振り返り、まとめで争点や答えの語彙がずれる                                                               | 3 箇所で同じ語彙を使う                                                               |
| オチ見出し           | Step/章タイトルに結果、教訓、感嘆を入れる                                                                       | 見出しは動作の目的だけを名詞句か短い動詞句で書く                                     |
| 余談マーカー見出し   | `ちなみに〜` `実際にやってみた感想` `やってみたら〜だった`                                                      | `補足` `感想` など短い名詞句へ                                                       |
| 断片ヘッダ           | 見出し直後の `まずはこちらです` `この節では〜`                                                                  | 見出しに吸収し、本題から始める                                                       |
| 急な文体シフト       | 1 段落だけ広報文、論文調、テンプレ文に跳ねる                                                                    | 周囲の温度に合わせて解体する                                                         |
| 過剰無難化           | 修正後に安全な一般論へ丸まり、元文の体温や観察場面が消える                                                      | 実際に見た場面、言い回し、判断順を少し戻す                                           |
| 安全圏フレーズ       | `〜の方が安全です` `〜と見るのが安全です` `〜と読むのが安全です`                                                | security / safety 文脈以外では避ける。根拠を近くに置き、言い切れるか見る             |
| 温度の不一致         | 絵文字や口語だけ残り、本文が研修資料のように硬い                                                                | 媒体の温度をそろえる                                                                 |
| Copula 回避          | `〜として機能する` `〜の役割を果たす` `〜を誇る` `〜を提供する`                                                 | `〜です` `〜である` `〜がある` に戻す                                                |
| 過剰言い換え         | 同一概念を毎回違う語で指す                                                                                      | 一貫した用語を使う                                                                   |
| 曖昧な帰属           | `専門家は〜と指摘している` `〜と言われている`                                                                   | 出典を具体名で示すか、自分の判断として書く                                           |
| 実測と補完の混線     | `実際に返ってきました` と書きながら、手で補った URL や説明まで同じ文で扱う                                      | ツール応答、AI 補完、著者補足を分ける                                                |
| メタ前置き宣言       | `隠す必要もないので素直に書きます` `ぶっちゃけ書きます`                                                         | 削除して結論や感想を直接書く                                                         |
| 整合確認文           | `〜と整合します` `矛盾しません` `あなたの状況と一致します`                                                      | 削除。結論または事実だけで止める                                                     |
| 締めの俗称初出       | まとめで本文未登場の俗称や自分用ラベルを初出させる                                                              | 本文で導入していない呼称は出さない                                                   |
| エッセイ締め調       | セクション末を「私はこの流れが好きです。A → B → C と出てきました。」のように散文詩的余韻で閉じる                | 事実か次の行動で止める。感想を残すなら 1 文だけ                                      |
| キャッチコピー再利用 | タイトルや TL;DR のフレーズをまとめ節で畳みかけて「名言感」を出す                                               | 観察で止めるか、読者の行動につなげる                                                 |
| コンサル語彙混入     | `メンタルモデル` `ジャーニー` `パラダイムシフト` `橋渡し` など、書き手の普段の語彙と合わない術語                | 書き手がチャットで使う語彙に戻す。「付き合い方」「感覚」「流れ」で済むなら置換する   |

## English Signals

| Category            | Pattern                                                                                                                                                       | Rewrite policy                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Buzz nouns          | `delve`, `tapestry`, `realm`, `landscape`, `testament`, `paramount`, `cornerstone`, `beacon`, `symphony`, `crucible`, `nuance`, `intricacies`                 | Use concrete nouns               |
| Buzz verbs          | `embark`, `unleash`, `unlock`, `harness`, `leverage`, `navigate`, `foster`, `streamline`, `empower`, `elevate`, `orchestrate`, `bolster`, `cultivate`         | Use plain verbs                  |
| Buzz adjectives     | `ever-evolving`, `seamless`, `robust`, `cutting-edge`, `game-changing`, `transformative`, `unparalleled`, `pivotal`, `holistic`, `multifaceted`, `meticulous` | Describe the fact                |
| Filler openers      | `In today's fast-paced world`, `It is important to note that`, `At its core`                                                                                  | Delete                           |
| Exploratory openers | `Let's explore`, `Let's dive into`, `Let's unpack`, `step-by-step guide`                                                                                      | Delete or start with the subject |
| Pivot constructions | `Not just X but Y`, `X isn't just Y, it's Z`, `It's not about X, it's about Y`                                                                                | State the point directly         |
| Parallel triples    | Repeated `A, B, and C` patterns                                                                                                                               | Break some into one or two items |
| Em-dash overuse     | More than one `—` in a paragraph                                                                                                                              | Use periods or parentheses       |
| Hedge stacking      | Repeated `can`, `may`, `might`, `could`, `potentially`, `arguably`                                                                                            | Assert when evidence supports it |
| Transition tells    | `Furthermore,`, `Moreover,`, `Additionally,`, `That said,`, `As we've seen,`                                                                                  | Delete or use `Also,` sparingly  |
| Conclusion tell     | `In conclusion,`, `Ultimately,`, `To sum it all up,`, `In a nutshell`                                                                                         | Delete                           |
| Engagement tell     | `I hope this helps!`, `Feel free to reach out`, `Happy coding!`                                                                                               | Replace with a real closing line |
| Rhetorical question | `But what does this really mean?`, `Why does this matter?`                                                                                                    | Replace with a concrete claim    |
| Throat-clearing     | `Before we dive in,`, `With that out of the way,`                                                                                                             | Delete                           |
| Emoji-heading       | Emoji at the start of every heading                                                                                                                           | Keep only where intentional      |
| Copula avoidance    | `serves as`, `stands as`, `represents`, `boasts`, `features`, `offers` used to avoid `is` / `has`                                                             | Use `is` / `has`                 |
| Elegant variation   | The same concept gets a new synonym every time                                                                                                                | Use one term consistently        |
| Sycophantic tone    | `Great question!`, `You're absolutely right!`, `Excellent point!`                                                                                             | Delete and answer                |
| Generic conclusions | `The future looks bright`, `only time will tell`, `remains to be seen`                                                                                        | End with a concrete next action  |

## Structure Signals

- Paragraph lengths are too uniform. Mix in one- or two-sentence paragraphs.
- Heading endings repeat too much. Change at least one if all headings end the same way.
- Lists always collapse to 3 or 5 items. Use the number the content actually needs.
- A short post has both a neat 3-point summary and a 2-point advice list. Return one list item to prose or keep only the needed count.
- The opening has too much runway: disclaimers, background, glossary, digressions. Put the main claim, axis, or TL;DR first.
- Every heading has a one-sentence intro. Delete intros that only restate the heading.
- Public-facing paragraphs explain internal structure too long. Write what became easier for the reader or operator.
- Fact, feeling, and intent are mixed in one paragraph. Separate numbers, hand-feel, and aim.
- All paragraphs have the same heat. Let important sections carry more weight.
- Observation is preceded by a label such as `〜として見ると追いやすい` or `〜に見える`. Put the observed fact first.
- The framework announced in the opening does not match the section structure. Remove, move, or fold out-of-axis topics.
- Sentence length variance is too low. Mix short and long sentences intentionally.
- The ending follows a problem-to-future template. Close with a concrete next action.
- The ending has multiple routes for the reader. Keep one main route and move the rest to references.

## Detection Notes

- When multiple tells overlap in the same sentence or paragraph, report them as one `stacking pattern`.
- Count em dashes, triples, repeated endings, and same-shaped lists instead of relying on impression.
- Say which structure creates the AI-like feel before saying it is AI-like.
- Prioritize sentences that catch when read aloud.
- For texts under 300 Japanese characters or 100 English words, add a confidence note because false positives are more likely.

## Experience-writing Signals

- Separate `I did this` from `AI did this` at the subject level.
- Include the improvement process when only the result is written.
- Separate lived experience from knowledge added through AI or Web search.
- Do not mix fact, feeling, and intent in one sentence.
- Prefer wording that shows how the writer judged the situation.
- For API / MCP / CLI results, separate observed output from model-readable formatting.
- Remove process logs that do not help readers; keep outcomes and judgments.
- Do not end with instruction phrases such as `〜を意識すべき` or `〜が大事` unless the reason is already in the text.
