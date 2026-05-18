---
name: web-accessibility
description: "Build and review accessible web products using WCAG 2.2 AA. Use when implementing or reviewing forms, dialogs, navigation, keyboard flows, focus management, ARIA, color contrast, responsive UI, or framework-specific accessibility in React/Next.js, Angular, and Vue."
argument-hint: "対象ファイル、画面、コンポーネント、または気になる accessibility 課題"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Web Accessibility

Product 実装や UI レビューで、a11y を後付けの監査ではなく設計・実装フローの中へ入れるための skill。

## When to Use

- Web UI を新規実装するとき
- 既存 UI の keyboard / focus / form / ARIA / contrast 問題を直すとき
- Dialog、navigation、table、toast、validation などの振る舞いを見直すとき
- React / Next.js、Angular、Vue の framework 癖込みで review したいとき
- 「merge 前に a11y の観点で見てほしい」という依頼を受けたとき

## Not the Best Fit

- Web UI ではない extension host / CLI 中心の変更
- 既にブラウザ上で再現済みで、runtime の証跡収集と検証を主目的にするケース
  - その場合は Accessibility Runtime Tester のような runtime 検証 agent を優先する
- Markdown 文書だけのアクセシビリティ改善

## Operating Principles

- Native HTML first. `div role="button"` より `<button>` を優先する
- Severity first. `CRITICAL` を潰してから `IMPORTANT`、最後に `SUGGESTION` を見る
- Keyboard first. マウスでしか確認していない UI は未完了とみなす
- Name / role / state を明確にする。見た目だけで意味が伝わっても不十分
- Review と fix を往復しやすいよう、指摘は component 単位・flow 単位で束ねる

## Workflow

1. **Scope the surface**
   対象の page / flow / component、主要タスク、入力手段、利用者制約を確認する。
2. **Hit the blocking issues first**
   semantics、keyboard、focus、label、error identification、accessible name を優先する。
3. **Check the UI pattern**
   form、dialog、navigation、table、media、notification などの pattern ごとに要件を確認する。
4. **Apply framework-safe fixes**
   React / Next.js、Angular、Vue で壊れやすい箇所を framework の流儀で直す。
5. **Re-check responsive and visual access**
   contrast、320px reflow、reduced motion、color-only signaling を見直す。
6. **Close with a verification note**
   直した点、未確認の runtime リスク、残件を短く残す。

## Decision Points

- Native element で解けるなら ARIA を増やさない
- Browser 上の focus trap、route announce、hover/focus popup を確証付きで見たいなら runtime 検証へ切り替える
- Quick review 依頼なら [review checklist](references/review-checklist.md) を先に回す
- 実装中なら [common UI failures](references/common-ui-failures.md) から直しやすい欠陥を先に潰す

## Escalation Paths

- 深い設計レビューや WCAG 観点の広い棚卸しが必要なら `Accessibility Expert` を使う
- Browser 上の keyboard flow、dialog、focus return、live region を証跡付きで確認したいなら `Accessibility Runtime Tester` を使う
- Markdown 文書の読みやすさや GitHub 上の文書 a11y が主題なら `markdown-accessibility` を使う

## Expected Output

- 主要な blocking issue を severity 順に並べる
- 修正する場合は component / flow 単位でまとめて直す
- 未検証の runtime 挙動は「推測で完了」にせず明示する
- Browser 実機確認が必要な場合は、可能な static guard や checklist も添える

## Reference Map

- Priority and legal baseline: [references/wcag-priority-map.md](references/wcag-priority-map.md)
- Common defects and fixes: [references/common-ui-failures.md](references/common-ui-failures.md)
- Framework notes: [references/framework-patterns.md](references/framework-patterns.md)
- Final pass checklist: [references/review-checklist.md](references/review-checklist.md)

## Done Criteria

- [ ] Keyboard だけで主要フローを操作できる
- [ ] Focus が見え、閉じた dialog や overlay から適切に戻る
- [ ] Interactive element に accessible name / role / state がある
- [ ] Form の label、required、error、status message が関連付いている
- [ ] Contrast、reflow、color-only signaling、motion の見落としがない
- [ ] Framework 固有の a11y regressions を確認した
- [ ] 未検証の runtime 挙動があれば明示した