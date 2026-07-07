---
name: powerpoint-planning
description: "Plan high-quality PowerPoint presentations before file creation or editing. Use when designing slide structure, storyline, section flow, executive summaries, local PowerPoint production briefs, Copilot prompts, or slide-review/revision prompts."
argument-hint: "資料テーマ、読者、用途、スライド数、参考資料、求めるトーン"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# PowerPoint Planning

PowerPoint 資料の上流設計 Skill。目的、読者、ストーリーライン、章立て、各スライドの主張、情報階層、視線誘導、生成プロンプト、レビュー観点、修正指示を設計する。

この Skill は PPTX ファイル操作ではなく、資料の構成設計と品質ディレクションを担当する。PPTX 生成、編集、検査、COM Automation、レンダー QA などの実ファイル操作は対象外にする。

## When to Use

- **PowerPoint 構成**, **スライド構成**, **PPT 企画**, **資料設計**, **ストーリーライン**
- 経営向け、顧客向け、社内向け、勉強会、ワークショップ、プロジェクト報告の構成を作るとき
- コンサル風の高密度資料、明るい社内資料、読み物として成立するビジネス資料を設計したいとき
- ローカル PowerPoint、手作業制作、Copilot Chat、PowerPoint for the web / Edit with Copilot に渡すブリーフやプロンプトを作るとき
- 生成済みスライドが AI っぽい、章立てが弱い、視線誘導がない、主張が薄いとき

## When Not to Use

- PPTX の読み取り、保存、結合、変換、レンダー出力、COM 編集が主目的のとき。
- Word / PDF / Excel など PowerPoint 以外が主成果物なら、それぞれの document skill を使う。
- 1 枚だけの軽い文章修正なら、Skill 化せず通常応答で足りる。

## Modes

- `consulting`: 経営、顧客、戦略、意思決定、プロジェクトガバナンス向け。結論、根拠、示唆、推奨、リスク、次アクションを明確にする。
- `internal-friendly`: 社内展開、勉強会、ワークショップ、啓発、コミュニティ共有向け。明るく親しみやすいが、子どもっぽくしない。

指定ブランド、テンプレート、Corporate Brand がある場合は mode より優先する。

## Workflow

1. **Brief**: テーマ、読者、利用シーン、読後アクション、避ける表現、希望枚数、参考資料、mode を確認する。
2. **Source Handling**: 情報を確認済み事実、仮説、推奨、未確認、human review required に分ける。数字、価格、日付、顧客事実、契約条件を勝手に作らない。
3. **Section Architecture**: スライド単位の前に、3-5 個程度の章立て、Agenda、必要な section divider、まとめを設計する。
4. **Slide Planning**: 各スライドの title、lead sentence、primary message、evidence、supporting detail、quiet note、layout、visual entry point、reading path を決める。
5. **Prompt / Brief Output**: ローカル PowerPoint、手作業制作、Copilot Chat、Edit with Copilot、または別の制作実行フローで使える制作ブリーフを出す。
6. **Review / Revision**: 生成後は章立て、主張、視線誘導、文字サイズ、カード余白、AI っぽさ、事実性をレビューし、slide-specific revision prompt を作る。

ゼロから起こす資料、多論点の資料、顧客レビューや意思決定を挟む資料では、Workflow 2-4 の中間成果物を 1 つのメモに混ぜず、planning 用フォルダに 4 ファイルへ分けて保存する。詳細は [references/structure-and-storyline.md](references/structure-and-storyline.md) の Planning Artifacts を参照する。

## Output Patterns

- Clarifying questions and missing inputs
- Deck objective, audience, usage context, reader action
- Recommended mode and tone
- Section architecture and Agenda
- Slide-by-slide plan
- Slide titles and lead sentences
- Page-level emphasis plan
- Local PowerPoint / Copilot / production brief
- Review checklist and revision prompts
- Handoff notes for slide production or file-operation workflows

## Core Rules

- Start from business outcome and reader action, not from slide decoration.
- Design section flow before slide details.
- Make each slide answer one question and carry one main takeaway.
- Make the title and lead sentence enough to understand the slide point.
- For executive or customer-facing decks, make the slide message short, position-taking, and readable at a glance; split the slide if that cannot be done.
- Use narrative lead sentences, not teaser copy.
- Keep assumptions and hypotheses distinct from confirmed facts.
- Let slide count increase when section dividers or split slides improve comprehension.
- Use visual hierarchy deliberately: one entry point, clear reading path, quiet caveats.
- Do not make every card, icon, text box, and color equally loud.
- Do not shrink text to hide overload; reduce wording, split the slide, or simplify the layout.
- For customer-facing, executive-facing, legal, brand, pricing, staffing, timeline, commitment, or customer-specific content, require human review before final use.

## References

- Structure and storyline: [references/structure-and-storyline.md](references/structure-and-storyline.md)
- Prompting and execution: [references/prompting-and-execution.md](references/prompting-and-execution.md)
- Review and revision: [references/review-and-revision.md](references/review-and-revision.md)
