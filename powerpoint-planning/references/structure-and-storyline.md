# Structure and Storyline

Use this reference when shaping the deck before writing slide details.

## Briefing Questions

- What is the deck about?
- Who will read it?
- Where and how will it be used?
- What should the reader understand, decide, agree to, or do after reading it?
- What is the main claim?
- What topics, expressions, or risks should be avoided?
- What slide count and density are expected?
- What source materials, URLs, files, or data are available?
- Which mode fits: `consulting` or `internal-friendly`?
- Is there a brand, Corporate Brand, template, or tone constraint?

If the request is vague, propose 2-3 storyline options and help the user choose.

## Experience-Based Narrative Gate

For a deck built around an experience, incident, or failure, confirm whether the case itself is the primary narrative before leading with concepts. If it is, preserve this causal flow and prioritize a user-specified form such as `起承転結`:

- Normal context -> event or turning point -> response and decisions -> outcome -> reusable practice
- Before detailed slide planning, rubber-duck whether the audience can follow what happened, who responded, why the response mattered, and what to do differently next time.
- When details must be anonymized, retain enough context and causality for the lesson to remain credible; label or omit unsupported specifics.

## Source Classification

Classify each input as one of:

- Confirmed fact
- Assumption
- Hypothesis
- Recommendation
- Open question
- Human-review-required information

Never present assumptions as confirmed facts. If source material conflicts, surface the conflict instead of resolving it silently.

## Section Architecture

For decks longer than 6 slides, create section-level flow before slide-by-slide planning. For shorter decks, still consider section roles even if divider slides are not needed.

Recommended patterns:

- Executive Summary / Agenda / Current situation / Key message / Details / Decision or next action
- Executive Summary / Agenda / Business context / Recommendation / Evidence / Risks and mitigation / Next steps
- Context / What this is / Why it matters / How it works / Scenarios / Quality model / Next step
- Problem framing / Capability overview / Use cases / Implementation approach / Governance / Next action
- はじめに / 基本情報 / 機能紹介 / 活用シナリオ / 品質・運用 / まとめ

Rules:

- Group slides into 3-5 logical sections when possible.
- Include an early Executive Summary and Agenda for executives, steering committees, board-style meetings, customer executives, or important decision meetings unless the user opts out.
- Use plain, descriptive section titles.
- Add section divider slides when they improve pacing, even if the slide count increases.
- Make Agenda and divider slides visually distinct from content slides.
- Do not use dense card/table layouts for navigation slides.

## Customer Proposal Fit Gate

For customer-facing sales, proposal, or account decks, make the storyline prove both fit and differentiation.

- **Fit to customer**: identify the customer's environment, risk, problem, constraint, timing, or success condition before proposing the answer.
- **Differentiation**: explain why this offer, product, team, or approach is objectively stronger, safer, faster, cheaper, or more unique than plausible alternatives.
- If the deck only says generic benefits, add customer-specific risk/problem framing before the recommendation.
- If the deck only says the customer has a problem, add comparative reasons to choose this solution or vendor now.
- Keep competitor or vendor claims evidence-based and conservative; mark unsupported positioning as a hypothesis or presenter note.

## Slide Message Discipline

For executive, customer-facing, or decision decks, define the slide message before layout details.

- Use one slide for one message; if two conclusions compete, split the slide.
- Make the message take a position, not just name a topic or category.
- Keep the message short enough to read at a glance; a two-line lead is the practical upper bound.
- If the message cannot be shortened, clarify the claim or remove secondary information before shrinking text.
- Treat charts, tables, diagrams, footnotes, sources, and page numbers as support for the message, not substitutes for it.

### Slide Body Language Rules (customer-facing)

- **Internal slide numbers (`s06` / `S14` / `Slide 3` 等) を本文・タイトル・参照テキストに書かない**。モデルが構造把握用に振る一時 ID や planning artifact 側の管理番号は内部専用。会議中の顧客には意味不明で議論を止める。参照が必要なら日本語ラベル (「Scoping ページ」「チェックリスト」等) で言い換える
- **Appendix 系スライドに連番を振らない** (`Appendix 1` / `Appendix 2` はやめる)。タイトルは **「Appendix — 内容説明」** で統一 (例: `Appendix — Portal 操作イメージ (ソース RG を開く)`)。並び替えや追加削除で連番修正が発生するのを防ぐ
- Speaker notes と planning artifact の中では内部番号使用可 (作業効率のため)。本文への流出だけ避ける

## Slide Planning Fields

For each slide, define:

- Section name
- Slide title
- Lead sentence
- Primary message
- Main evidence
- Secondary information
- De-emphasized notes
- Recommended layout
- Visual entry point
- Reading path
- What to make prominent
- What to make quiet

Each slide should work as a reading document, not only as speaker support.

## Planning Artifacts

ゼロから起こす資料、多論点の資料、外部レビューや意思決定を挟む資料では、planning 段階の中間成果物を 1 ファイルに混ぜず、専用フォルダに次の 4 ファイルへ分けて保存する。会議資料ならプロジェクト直下ではなく、会議フォルダ配下の `slide-planning/` を優先する。1 ファイルに混ぜると根拠・不明点・弱点・構成が絡み、構成だけやり直すのが難しくなる。

- `research-deepdive.md` — Workflow 2 の出力。出典、引用 URL、GA/Preview/Retired の状態、代替選択肢まで。可能なら Deep Research 系サブエージェントに委譲して根拠を集約する。TL;DR と参考 URL 一覧を先頭・末尾に置く。
- `discovery-todo.md` — 不明点とヒアリング項目を owner (自分側 / 相手側 / 両者確認) 別に分類。優先順位を付け、Workflow 3-4 で埋まらなかった前提を可視化する。
- `rubber-duck-review.md` — 構成を書く前の自問自答。「1 ページで足りるか」「その章は誰にどう刺すか」「Preview / 未確定を見せてよいか」「代替案を出さなくて良いか」など、後で構成を守るためのガード。リスクと弱点も箇条書きで残す。
- `slide-structure.md` — Workflow 4 の最終構成案。各ページに layout 名、talking point、visual、参考 URL、レビュー観点を明示する。実制作の唯一の入口として使う。

小規模資料 (概ね 6 枚未満、単一論点、社内向け通知系) では 1 ファイルに畳んでよい。分けるか畳むかは Brief の複雑度と読者の意思決定コストで決める。ファイル名・フォルダ名はプロジェクト側の命名規約に合わせて調整する。

### Meeting Folder SSOT

会議で使う PowerPoint は、**会議単位フォルダを SSOT にする**。project root に `slide-planning/` や日付フォルダを増やし続けない。

推奨構造:

```text
_meetings/
  YYYY-MM-DD-topic/
    YYYY-MM-DD_deck-name.pptx   # 会議で使った正本。無版番で 1 個だけ
    minutes.md                  # 議事録
    decisions.md                # 決定事項サマリ
    slide-planning/             # 中間生成物
      slide-structure.md
      research-deepdive.md
      discovery-todo.md
      checklist-impact-notes.md
      rubber-duck-review.md
      archive/                  # build script / image素材 / 再生成用 asset
```

Rules:

- 会議で使った pptx は会議フォルダ直下に置き、`_v01` などの版番を外した canonical name にする
- planning artifacts や build script は会議フォルダ配下の `slide-planning/` に置く。`slide-planning/archive/` は再生成用 infrastructure であり、単なる一時ファイルとして削除しない
- 次回会議は `_meetings/YYYY-MM-DD-next-topic/` を新規作成し、前回フォルダをコピーするか、SSOT pptx を COM 編集で更新してから複製する
- pptx なしの短い会議は `_meetings/YYYY-MM-DD-topic.md` の単発メモでよい。pptx や planning artifacts が発生したらフォルダ形式に昇格する

## Checklist Impact Notes (顧客回答分岐の事前準備)

顧客ミーティングで「その場で Yes/No/不明 を書き込むチェックリスト slide」を出すときは、**必ず「回答別の影響と打ち手」をスライドノートに埋め込む**。顧客は「これが Yes だったら / No だったら / 何が起きる?」を必ず聞く。事前準備なしだと会議が止まる。

パターン:

1. `checklist-impact-notes.md` を planning フォルダに新規で作る (planning artifact の第 5 ファイル扱い)
2. 各質問について次のブロックを書く:
   - 質問文 (原文まま)
   - **Yes の場合**: 何が起きる / 何を追加でやる (2-4 行)
   - **No の場合**: 何が起きる / どこまで単純化できる (1-3 行)
   - **不明の場合**: どうやって確認する / どの CLI or Portal 画面で調べる (1-2 行)
   - **根拠 URL**: 公式ドキュメント (ja-jp 優先) を 1-2 本
3. Deep Research 系サブエージェントに丸投げする (質問数 10 以上ある場合は特に)。Learn / 公式 Docs の検索クエリを英語で列挙して渡す。GA/Preview/Retired の区別を必ず明記させる
4. build script では、詳細版 md をそのまま notes に貼らず、**「サマリ + 各質問 3-4 行」に圧縮したノート版**を slide の speaker notes に流し込む (`add_notes()` ヘルパー相当)
5. 詳細版 md は会議中の tab 開き用に残す

Rationale: スライド本文は「Y/N/不明 チェックボックス + メモ欄」だけで簡潔にし、`Y/N/不明 の分岐で会話が発散したときの答え` はノートに寄せる。会議中に発表者ビューで見ればその場で回答できる。詳細版 md への URL 参照はノートの先頭に添えると再検索コストが低い。

## Customer Concerns Slide (相手側リスクをその場で書き取る)

顧客対面 deck では **Next Steps (合意 slide) の直前** に「相手側の懸念事項・見えているリスクを会議中にフリー記述する slide」を必ず 1 枚挟む。事前調査で全論点を潰していても、顧客側からしか出てこないビジネス / 内部政治 / スケジュール制約が必ずある。それを Next Steps 合意の前に回収しないと、決めた方針が後から覆る。

パターン:

- 3 カラム構成: `内部射程 (人/時間/スキル)` / `技術・運用の懸念` / `ビジネス / ステークホルダー`
- 各カラムに空の bullet 行 (中点だけ) を 5-6 個。書き込みやすい余白と font size (18pt 程度) にする
- Speaker notes に「引き出しの問い方 3 パターン」を書く:
  - 「今のところ一番心配な点は何ですか?」
  - 「この進め方で、人 / 時間 / 予算面で問題になりそうな点は?」
  - 「以前やった似た作業でハマったことは?」
- 拾ったリスクは会議後にリスク台帳化し、Next Steps の「MS 側 next actions」へ「今日拾ったリスクのうち MS 側で受け止めるもの」項目で流し込む
- Section は Next Steps と同じ「本日のアクション」区分に入れる

Rationale: 「顧客に懸念を聞く時間」を明示的に slide として確保することで、facilitator の力量に依らず必ず回収できる。フリー記述の見た目 (空 bullet 6 行) は顧客に「今書いていい場」と伝わる。
