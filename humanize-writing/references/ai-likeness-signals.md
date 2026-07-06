# AI-likeness Signals

Humanize Writing の検出辞書。検出は厳密に、修正は文脈判断で行う。

## Scan Priority

1. 事実が変わっていないか
2. 書き手の主語と判断が見えるか
3. 抽象語やつなぎ語で説明しすぎていないか
4. 構造が均一すぎないか
5. 反証可能な主張になっているか

## Japanese Signals

| Category                | Pattern                                                                                                                                    | Rewrite policy                                                                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 定型接続詞              | `つまり、` `要は` `言い換えると` `すなわち` `まとめると` `〜に他ならない`                                                                  | 削除、または具体語へ                                                                                                                                |
| 空虚な断定・抽象語      | `かなり` `十分` `しっかり` `非常に` `極めて` `大いに` `不可欠` `核心的` `根本的` `包括的` `総合的` `活用` `効率化` `土台` `価値`           | 数値、具体描写、動作へ戻す                                                                                                                          |
| 定型構文                | `〇〇そのものではなく△△すること` `〇〇というわけではなく`                                                                                  | 事実に沿って一文で書く                                                                                                                              |
| 定型導入                | `実は〜なのです` `〜してみませんか？`                                                                                                      | 削除                                                                                                                                                |
| メタ観察導入            | `面白いのは〜` `印象に残ったのは〜` `気になったのは〜` `いちばんメモしたのは〜` `刺さったのは〜` `実務っぽかったのは〜`                    | 見えた事実や出典の内容から始める。`〜なのは` の枕を削り、名詞句や短い判断文にする                                                                   |
| 冗長助動詞              | `〜ということができます` `〜することが可能です`                                                                                            | `〜できます`                                                                                                                                        |
| 過剰謙遜                | `〜かもしれません` `〜と言えるだろう` の乱用                                                                                               | 事実なら言い切る                                                                                                                                    |
| soft assertion 連続     | `〜と思います` `〜と感じています` `〜と考えています` が同セクションに 3 回以上                                                             | 事実は断定し、主観は 1 回だけ残す                                                                                                                   |
| 同じ文末連続            | `〜でした。` が 3 連続以上                                                                                                                 | 一部を常体、体言止め、倒置にする                                                                                                                    |
| 同じ書き出し連続        | `今回は` / `今回の` が 3 連続                                                                                                              | 主語や視点を変える                                                                                                                                  |
| 章末定型                | `いかがでしたか？` `この記事が〜の助けになれば`                                                                                            | 削除、または体験ベースにする                                                                                                                        |
| pivot 構文              | `〇〇ではなく△△` `〇〇というより△△`                                                                                                        | 読者視点で対比が成立するか確認する。成立しなければ一文で言う                                                                                        |
| 比較で逃がす要約        | `A より B` `X の話では終わっていない` `単なる〜ではなく`                                                                                   | 比較を先に立てず、観察した事実を書く                                                                                                                |
| 章立て予告              | 冒頭の「この記事では次の流れで見ていきます」+ `1.〜N.`                                                                                     | TL;DR と H2 目次の二重化なら削る                                                                                                                    |
| 教訓風総括段落          | `ここでの学びはシンプルで、〜ことでした` `一番のポイントは〜ことでした`                                                                    | 動詞に溶かすか削除する                                                                                                                              |
| 判断不在の正論          | 誰が書いても成立する一般論だけが並ぶ                                                                                                       | 何を重視したか、どこで迷ったか、何を先にやったかを残す                                                                                              |
| 観測後の抽象総評        | before / after や検証結果の直後に `期待どおり動きました` `〜と見てよさそうです` で締める                                                   | 確認できた変化そのもので閉じる                                                                                                                      |
| 説教締め                | まとめ末の「まずは〜くらいの使い方からでも十分助かりました」                                                                               | 著者の予告、次の行動、主観で閉じる                                                                                                                  |
| 節冒頭テンプレ          | `〇〇だけだと△△までは届きません。ここも AI に任せました`                                                                                   | 指示内容や観察結果から直入りする                                                                                                                    |
| 見出し復唱              | H2/H3 直後の「ここが一番効いたポイントでした」                                                                                             | 削除。見出しで言ったことを本文で繰り返さない                                                                                                        |
| ポイント専用節          | 「試行錯誤で効いたコツ」「ここが効いた」の H2 独立                                                                                         | まとめ節に吸収する                                                                                                                                  |
| 効く系の抽象評価        | `効いたポイント` `ここが効きます` `効くコツ` が、対象・変化・根拠を書かず自己評価だけになっている                                          | 禁止語にしない。実測結果や助かった場面があるなら残し、抽象的な見出しや復唱なら確認できた変化へ置換する                                              |
| 当たり前解説            | コードや表の直後の「こうしておくと〜が分かります」                                                                                         | 削除                                                                                                                                                |
| 無理な差し込み理由      | 画像・図・表の前に `〜を掴みやすくするためです` `〜のイメージを掴みやすいので` のような正当化を置く                                        | まず対象を普通に紹介する。例: `こちらは GitHub Codespaces です。〜という製品ですね。` 理由説明は必要なときだけ残す                                  |
| 教科書型橋渡し          | `この違いが分かると〜` `ここで重要なのは〜` `大事なのは〜` `〜と覚えておけば、ひとまず十分です`                                            | 半数以上を削除。残すなら事実か判断軸で閉じる                                                                                                        |
| 姿勢宣言                | `正面から扱う` `正面から回収する` `多角的に見る` `掘り下げる` `言語化する` `触れる` `言及する` が、何を見たかを増やしていない              | 姿勢ではなく、扱った対象・判断・結果を書く。新情報がなければ削る                                                                                    |
| 接続テンプレ            | `〜において` `〜という側面から` `〜の観点から` `さらに` `また` `加えて` の連打                                                             | 接続で論理を作ったように見せず、前後の関係や追加された事実を具体的に書く                                                                            |
| 予測的足場設営          | 章冒頭の `ここで大事なのは〜です` `〜が考慮すべき点です`                                                                                   | 予測を削り、本文へ直結させる                                                                                                                        |
| 内部資産列挙            | `SSOT` `handbook` `playbook` `checklist` `運営メモ` の棚卸し                                                                               | 公開文では一覧化せず、何がやりやすくなったかに圧縮する                                                                                              |
| 判断ログ露出            | `この記事では〜として扱う` `正本として扱う` `今の読み方` `この整理がいちばん無理がありません` `私の運用では〜です`                         | 公開文では表、注記、本文の事実に吸収する。標準規格や公式仕様は個人解釈に弱めない。事実文で終わるなら後続コメントを削る                              |
| 観測後の推測調          | 実測や引用の直後に `〜と見てよさそうです` `〜として扱うのが安全です` `〜として観測` を置き、本文の判断メモが露出している                   | 事実なら `〜でした` `〜と表示された`、本文上の約束なら `この記事では〜と呼びます` にする。根拠が弱い場合だけ未確認と書く                            |
| 無難な判定句            | `〜として見るのが自然です` `〜として読むほうが自然です` `〜と見るのが自然です` で締め、誰の判断かが消える                                  | 書き手の判断なら `私は〜と読みました`、事実なら主語を戻して具体的に書く。`自然です` で丸めず、何を根拠にそう読んだかを近くに置く                    |
| 検証台帳の本文化        | `確認済み` `未検証` `実機表示` `PTY lab 検証` などの台帳ラベルが本文前半で長い表になり、読者が結論に入る前に検証ログを読まされる           | 本文は「確認したこと / まだ見ていないこと」を短く出し、コマンドログ・細かい条件・失敗経路は付録や注記へ逃がす                                       |
| 検証手段の露出          | `PTY` `harness` `marker file` `dialog までは表示` など、読者の判断に不要な検証方法や実況が本文に出ている                                   | 読者が知るべき結果だけ残す。未完了なら `今回はそこまで見ていない` など短く保留し、検証手段名や一時ファイル名は削る                                  |
| 確認済み alias のヘッジ | 実機で alias と確認できたものを `alias として観測` `実機表示ベースの alias として扱う` と弱めたり、alias 同士を別ユースケースとして並べる  | 確認済みなら `X は Y の alias` と書く。例や使いどころは 1 行にまとめ、仕様差がある場合だけ別途短く補足する                                          |
| 直訳用語                | `席課金` のように英語 UI / 契約語を機械的に和訳した不自然語                                                                                | 業界で自然な語へ戻す。例: `seat-based` は文脈により `シート課金` `シート料金` `ライセンス` などで表す                                               |
| 時点注記不足            | 価格、preview、公開料金の有無、仕様制限が変わりうる話題で、公開 Docs ベースと調査時点が見えない                                            | 冒頭か注記で `YYYY-MM-DD 時点の公開 Docs ベース` を短く補う。断定を弱める必要があるなら本文も合わせて調整する                                       |
| 便利語口癖化            | `一気に` `強い` `助かる` `そのまま` `しっかり` `土台` や、著者固有の比喩動詞・口癖（`殴る` `気持ちよく` `シュッと` 等）が同記事に 3 回以上 | 半分以上を削除または具体語に置換する。著者の voice として意識的に残している語は全消去ではなく頻度を半減する                                         |
| 類義語の機械置換        | `速い` を timing の意味で使う、`早い` を処理速度の意味で使う、`把握が速い` のように日本語として少し硬い近似語で止める                      | 速度・時期・容易さを分ける。必要なら `早く立ち上がれる` `把握しやすい` `早く成果にたどり着ける` のように意味で言い換える                            |
| 整理語で締める          | `前に出ています` `話がつながります` `見えてきます` `腑に落ちます` `いちばんしっくり来ます` `読みやすくなります`                            | 観察した事実で止める。事実で終わるなら後続の整理コメントは足さない                                                                                  |
| 抽象カテゴリ列挙        | `〜面` `足回り` `地図がつながる` `runtime / context / tooling` だけで観察を運ぶ                                                            | 具体名詞や動作へ戻す                                                                                                                                |
| 和文と英数字の密着      | `Factory活用` `33件` `WS資料` `2FA(2要素認証)`                                                                                             | 本文として読む箇所は境目に半角スペースを入れる。`GH-300` `#49` `1on1` URL は崩さない                                                                |
| コア論点ずれ            | TL;DR、振り返り、まとめで争点や答えの語彙がずれる                                                                                          | 3 箇所で同じ語彙を使う                                                                                                                              |
| オチ見出し              | Step/章タイトルに結果、教訓、感嘆を入れる                                                                                                  | 見出しは動作の目的だけを名詞句か短い動詞句で書く                                                                                                    |
| 余談マーカー見出し      | `ちなみに〜` `実際にやってみた感想` `やってみたら〜だった`                                                                                 | `補足` `感想` など短い名詞句へ                                                                                                                      |
| 断片ヘッダ              | 見出し直後の `まずはこちらです` `この節では〜`                                                                                             | 見出しに吸収し、本題から始める                                                                                                                      |
| 急な文体シフト          | 1 段落だけ広報文、論文調、テンプレ文に跳ねる                                                                                               | 周囲の温度に合わせて解体する                                                                                                                        |
| 過剰無難化              | 修正後に安全な一般論へ丸まり、元文の体温や観察場面が消える                                                                                 | 実際に見た場面、言い回し、判断順を少し戻す                                                                                                          |
| 安全圏フレーズ          | `〜の方が安全です` `〜と見るのが安全です` `〜と読むのが安全です` `そのまま覚えない方が安全です`                                            | security / safety 文脈以外では避ける。注意喚起が必要なら `一時的な増量です` のように事実で閉じ、本文中に近接する出典リンクを置く                    |
| 温度の不一致            | 絵文字や口語だけ残り、本文が研修資料のように硬い                                                                                           | 媒体の温度をそろえる                                                                                                                                |
| Copula 回避             | `〜として機能する` `〜の役割を果たす` `〜を誇る` `〜を提供する`                                                                            | `〜です` `〜である` `〜がある` に戻す                                                                                                               |
| 過剰言い換え            | 同一概念を毎回違う語で指す                                                                                                                 | 一貫した用語を使う                                                                                                                                  |
| 曖昧な帰属              | `専門家は〜と指摘している` `〜と言われている`                                                                                              | 出典を具体名で示すか、自分の判断として書く                                                                                                          |
| 実測と補完の混線        | `実際に返ってきました` と書きながら、手で補った URL や説明まで同じ文で扱う                                                                 | ツール応答、AI 補完、著者補足を分ける                                                                                                               |
| メタ前置き宣言          | `隠す必要もないので素直に書きます` `ぶっちゃけ書きます`                                                                                    | 削除して結論や感想を直接書く                                                                                                                        |
| 整合確認文              | `〜と整合します` `矛盾しません` `あなたの状況と一致します`                                                                                 | 削除。結論または事実だけで止める                                                                                                                    |
| 締めの俗称初出          | まとめで本文未登場の俗称や自分用ラベルを初出させる                                                                                         | 本文で導入していない呼称は出さない                                                                                                                  |
| エッセイ締め調          | セクション末を「私はこの流れが好きです。A → B → C と出てきました。」のように散文詩的余韻で閉じる                                           | 事実か次の行動で止める。感想を残すなら 1 文だけ                                                                                                     |
| キャッチコピー再利用    | タイトルや TL;DR のフレーズをまとめ節で畳みかけて「名言感」を出す                                                                          | 観察で止めるか、読者の行動につなげる                                                                                                                |
| コンサル語彙混入        | `メンタルモデル` `ジャーニー` `パラダイムシフト` `橋渡し` など、書き手の普段の語彙と合わない術語                                           | 書き手がチャットで使う語彙に戻す。「付き合い方」「感覚」「流れ」で済むなら置換する                                                                  |
| 英語術語の未説明        | `Gotchas` `Progressive Disclosure` など、英語圏の開発用語が日本語記事で初出補足なしに出る                                                  | 初出で日本語の意味を括弧や短文で補う。例: `Gotchas（落とし穴・ハマりどころ）`                                                                       |
| false agency            | モノが主語で人間の動詞を取る。`データが示している` `文化が醸成される` `お弁当が設計されていた`                                             | 誰が何をしたかを書く。主体を人や組織に戻し、データは根拠の位置におく                                                                                |
| 命題型 H2               | `〇〇は△△だ` `〇〇は△△にした` のように主張を見出しで言い切る、が連続する                                                                   | 見出しはテーマを示す名詞句にし、主張は本文で展開する                                                                                                |
| 3項並列の過剰           | `3 つのポイント` `3 つの観点` `3 つの理由` が記事内で繰り返される                                                                          | 2 つか 1 つに削れないか検討する。並列を崩して一部を文章に戻すとムラが出る                                                                           |
| 中間温度の欠如          | 全体が `すごい` `最高` `ヤバい` `助かる` だけで構成される、または全体が 警告・否定だけで裏返される                                         | `悪くない` `まあまあ` `微妙` など、推奨一色でも否定一色でもない中間温度を混ぜ、強度を一段下げる                                                     |
| 両論併記での判断放棄    | `〇〇もあり、△△もあります` `ケースバイケースですね` で章を閉じる                                                                           | どちらを選んだか、なぜそう考えたかを書く。選べないなら選べない理由を書く                                                                            |
| 反証可能性の欠如        | `重要だ` `本質的だ` `構造的だ` `鍵となる` で文章を締める、読み手が反論できない                                                             | 誰かが具体的に反論できる主張に降りる。数字、固有名、判断した軸で閉じる                                                                              |
| 演出の過剰              | 溜め、修辞疑問、短い決め台詞、太字強調が山場以外で繰り返される                                                                             | 一律削除せず、議論上の山場だけ残す。説明で足りる箇所は普通の文に戻す                                                                                |
| 読者への不誠実          | 作為的な例を自然な事実のように書く、未確認のことを確認済みのように滑らかに書く                                                             | 作為性・未確認性を短く認め、出典・観測結果・読者が納得できる一般的事実へ寄せる                                                                      |
| 証拠の型違い            | 例・研究・概念が、支えたい主張とは別の問いに答えている                                                                                     | 主張を根拠に合わせて狭めるか、実際にその主張を支える根拠へ差し替える                                                                                |
| 比較対象のズレ          | 事業会社の AI 活用を論じたいのに、OpenAI / Anthropic など AI provider 側の採用・報酬・研究事例を主例にしてしまう                           | 比較軸を本文の問いに合わせる。事業会社の制度・業務実装なら、主業が AI 提供でない会社の公式発表・採用・IR を優先し、AI provider 事例は補助線に下げる |

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
- A paragraph cannot say what it receives from the previous paragraph, what role it plays, or what it passes to the next paragraph. Treat it as an argument-flow gap.
- Public-facing paragraphs explain internal structure too long. Write what became easier for the reader or operator.
- Fact, feeling, and intent are mixed in one paragraph. Separate numbers, hand-feel, and aim.
- All paragraphs have the same heat. Let important sections carry more weight.
- Observation is preceded by a label such as `〜として見ると追いやすい` or `〜に見える`. Put the observed fact first.
- The framework announced in the opening does not match the section structure. Remove, move, or fold out-of-axis topics.
- Sentence length variance is too low. Mix short and long sentences intentionally.
- The ending follows a problem-to-future template. Close with a concrete next action.
- The ending has multiple routes for the reader. Keep one main route and move the rest to references.
- Documentation or comments narrate the diff (`added this`, `replaced the old approach`) instead of describing current behavior. Unless it is a changelog or migration guide, write what the thing does now.
- The prose turns ordinary claims into aphorisms (`X is the language of Y`, `X becomes a trap`, `X is a mirror`). Replace the formula with the concrete claim.
- Several clipped fragments stack up to manufacture drama. One short emphatic sentence is fine; repeated fragments should become ordinary prose.
- Bold-label vertical lists repeat (`**Speed:**`, `**Quality:**`, `**Security:**`). Keep only when the list is genuinely useful; otherwise fold the points into prose.

## Detection Notes

- When multiple tells overlap in the same sentence or paragraph, report them as one `stacking pattern`.
- Count em dashes, triples, repeated endings, and same-shaped lists instead of relying on impression.
- Say which structure creates the AI-like feel before saying it is AI-like.
- Prioritize sentences that catch when read aloud.
- For texts under 300 Japanese characters or 100 English words, add a confidence note because false positives are more likely.

## False Positive Guard

- Perfect grammar, tidy headings, and readable tables are not AI tells by themselves. Professional editing and CMS templates can produce the same surface.
- Em dashes, curly quotes, transitions, or polite openings count only when they appear with other formulaic tells.
- Preserve specific, hard-to-fabricate details, era-bound phrasing, mixed feelings, and word choices the writer can defend.
- For technical, legal, reference, or encyclopedic text, neutral and plain may be the right human voice. Do not inject personality where the genre calls for restraint.

## Experience-writing Signals

- Separate `I did this` from `AI did this` at the subject level.
- Include the improvement process when only the result is written.
- Separate lived experience from knowledge added through AI or Web search.
- Do not mix fact, feeling, and intent in one sentence.
- Prefer wording that shows how the writer judged the situation.
- For API / MCP / CLI results, separate observed output from model-readable formatting.
- Remove process logs that do not help readers; keep outcomes and judgments.
- Do not end with instruction phrases such as `〜を意識すべき` or `〜が大事` unless the reason is already in the text.
