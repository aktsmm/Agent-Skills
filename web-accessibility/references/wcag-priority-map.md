# WCAG Priority Map

Web product 実装でまず見るべき順番を、WCAG 2.2 AA ベースで圧縮した地図。

## Baseline

- Target: WCAG 2.2 AA
- Legal shorthand:
  - EAA: EU 向け digital product なら無視しにくい前提
  - ADA Title II: 公共系では 2026 以降さらに重い
  - Section 508: 米国 federal 調達文脈では継続して意識が必要

## Priority Order

### P0: Blocking issues

- `lang` がない、heading / landmark が壊れている
- Keyboard で操作できない
- Focus trap から出られない、focus が見えない
- Label がない、error が text で伝わらない
- Button / link / custom control に accessible name がない
- Table header がない
- Alt text や captions が欠けている
- Text contrast が不足している

### P1: Significant barriers

- Skip link がない
- Dialog close 後に focus が戻らない
- Hover / focus で出る content が dismissible でない
- Color だけで状態を伝えている
- 320px で reflow しない
- Dynamic status が screen reader に伝わらない
- Route change が SPA で告知されない

### P2: Quality improvements

- `prefers-reduced-motion` への追従
- target size と spacing の改善
- redundant ARIA の削減
- heading の細かな階層改善

## Native Before ARIA

1. Native element で解けるならそれを使う
2. Native semantics を ARIA で上書きしない
3. ARIA control を置くなら keyboard support まで実装する
4. Focusable element に `aria-hidden="true"` を付けない
5. Interactive element の accessible name を欠かさない

## Quick Triage by Request

- "操作できない": keyboard / focus / trap を最優先
- "フォームが使いづらい": label / required / error / describedby を最優先
- "見た目は平気だが不安": contrast / landmarks / headings / names を先に見る
- "SPA 遷移で違和感": title / live region / focus management を見る