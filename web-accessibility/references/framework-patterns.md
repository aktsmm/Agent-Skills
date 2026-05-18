# Framework Patterns

## React / Next.js

- JSX の label は `for` ではなく `htmlFor`
- Route change 後は page title と main heading の整合を保つ
- Re-render で focus が飛ぶなら DOM identity を安定させる
- Rich text を注入するなら heading、alt、ARIA を含めて sanitize する
- Icon-only button、dialog close、toast announce は component 化して再利用する

## Angular

- `(click)` を `div` に置くより button を使う
- Modal は Angular CDK Dialog / `cdkTrapFocus` を優先する
- Router 遷移時の announce は `LiveAnnouncer` を使う
- Template-driven form でも `aria-invalid` と `aria-describedby` を忘れない

## Vue

- `@click` を non-interactive element に置くなら role、tabindex、keyboard handling まで実装する
- `v-if` で開く panel / dialog は `nextTick` 後の focus 移動を入れる
- `v-html` は sanitize と structure validation を前提にする

## Cross-framework Guardrails

- Native component に寄せられるところは headless custom control を増やしすぎない
- Design system component を直すときは a11y fix を利用側ではなく component 側へ寄せる
- Browser runtime でしか確証が持てない挙動は、実装レビューだけで完了扱いにしない