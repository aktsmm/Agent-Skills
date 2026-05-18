# Common UI Failures

実装で頻出する欠陥を、直し方の方向まで含めて短くまとめる。

## Structure and Semantics

- `div` soup で landmark がない
  - `header` `nav` `main` `footer` を使う
- Heading level が飛ぶ
  - 見た目ではなく文書構造で選ぶ
- Link text が `click here` や `more`
  - 行き先や動作が text だけで分かるようにする
- Layout table と data table が混ざる
  - Layout は CSS、data table には `caption` と `th` を付ける

## Keyboard and Focus

- `div` や `span` に click だけある
  - `<button>` へ戻す。戻せないなら role、tabIndex、Enter / Space を実装する
- `outline: none` で focus ring が消えている
  - `:focus-visible` を作る
- Custom dialog に Escape、Tab trap、focus return がない
  - Native `dialog` か、等価の keyboard/focus 管理を入れる
- Hover-only UI
  - `focus` / `blur` でも同じ内容へ到達できるようにする

## Forms and Validation

- Placeholder を label 代わりにしている
  - Visible label を置く
- Error message が input と結び付いていない
  - `aria-describedby` と `aria-invalid` を使う
- Required が色や `*` だけ
  - `required` と説明文を加える
- Submit 後に最初の error へ focus しない
  - error summary か first invalid field へ誘導する

## Dynamic Content

- Toast や save message が screen reader に届かない
  - `role="status"` または `role="alert"`
- Icon-only button に name がない
  - `aria-label` を付ける
- Hidden 状態と focusable 状態が矛盾する
  - `aria-hidden`、`hidden`、`inert`、focusability の整合を取る

## Visual Access

- Text contrast 不足
  - Normal text は 4.5:1、large text は 3:1 を下回らない
- Color だけで error / success を伝える
  - icon、text、border などを重ねる
- Narrow viewport で横スクロール前提になる
  - 320px 幅で reflow する layout に戻す
- 強い motion を常時出す
  - `prefers-reduced-motion` を考慮する

## Media

- Informational image に alt がない
  - 意味を伝える alt か、装飾なら空 alt にする
- Video に captions がない
  - `track kind="captions"` を付ける
- Audio / video autoplay
  - 原則避ける。必要でも mute と control を前提にする