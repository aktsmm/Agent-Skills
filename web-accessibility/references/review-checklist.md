# Review Checklist

## Perceivable

- [ ] 画像に適切な alt がある
- [ ] Decorative image は空 alt か `aria-hidden` で処理されている
- [ ] Headings と landmarks が論理的
- [ ] Text contrast が十分
- [ ] Color だけで状態や意味を伝えていない
- [ ] 320px 幅でも主要 UI が崩れない
- [ ] Media には captions や control がある

## Operable

- [ ] Keyboard だけで主要操作が完了できる
- [ ] Focus indicator が見える
- [ ] No keyboard trap
- [ ] Dialog / menu / popover に Escape と focus return がある
- [ ] Hover-only interaction になっていない
- [ ] Skip link が必要な画面にある

## Understandable

- [ ] Form field に label がある
- [ ] Required と error が text でも伝わる
- [ ] Error が input と関連付いている
- [ ] Unexpected context change を起こさない
- [ ] SPA route change の title / announce / focus が整理されている

## Robust

- [ ] Interactive element に name / role / state がある
- [ ] Invalid / redundant ARIA がない
- [ ] Dynamic status が live region で伝わる
- [ ] Focusable element と hidden state が矛盾していない

## Close-out Note

- [ ] 直した点を component / flow 単位で要約した
- [ ] Runtime 未確認の点を明記した
- [ ] 追加テストが必要なら残件として分離した
