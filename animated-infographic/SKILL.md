---
name: animated-infographic
description: "Create reproducible animated infographic GIFs from structured data or measured results, with audience-language labels, explicit timing semantics, representative-frame QA, and a static fallback. Use when asked for GIF生成, animated infographic, 動的インフォグラフィック, 結果が流れる図, animated benchmark, or a blog/SNS animation whose displayed metrics must remain traceable to source data."
argument-hint: "可視化するデータ、用途、言語、比率、演出時間か実測時間か"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Animated Infographic

## When to Use

- JSON / CSV / benchmark resultsからGIFや動く図を作る。
- カード移動、ランキング、比較棒、状態遷移をアニメーションで見せる。
- 数値の正確性と、演出時間・実測時間の区別が重要な記事 / SNS資産を作る。

静止PNGだけなら`visualize-as-infographic`、既存動画の分析なら`video-watch`、編集可能な構成図ならdraw.io系workflowを使う。

## Inputs

- Source artifact: JSON / CSV / text。測定値がある場合はこれをSSOTにする。
- Audience language and target medium: Japanese blog、X、slideなど。
- Timing mode:
  - `illustrative`: 動きは演出。処理速度を表さない。
  - `measured`: frame timingを実測timestampから作る。
  - `mixed`: 数値は実測、カードや棒の動きは演出。
- Output size。既定はblog/X向け`1200x675`、必要なら静止fallbackも作る。

## Workflow

1. **Freeze the evidence**
  - source artifact、取得日時、対象件数、測定境界を固定する。
  - latencyは`1 request`、`serial total`、`fresh-process end to end`など、何を測った値か決める。
2. **Design the story**
  - 1 GIFは1つの主張に絞る。長文説明は本文へ戻す。
  - 入力 → 判断 → 次処理、before → after、比較 → 結論など、読み順を固定する。
3. **Localize before rendering**
  - 説明UI、status、captionは読者言語へ合わせる。日本語記事に汎用英語UIを残さない。
  - 製品名、API field、model IDなどの固有名詞は公式表記を保つ。
  - 直訳調を避ける。例: `段階で採点`ではなく`定義した基準のどの段階に近いか`。
4. **Make timing explicit inside the asset**
  - `illustrative`: `カード移動は演出（実測速度ではありません）`を表示する。
  - `measured`: 測定境界と単位を表示し、frame durationを実測値から作る。
  - `mixed`: `表示値は実測 / 棒・カードの動きは演出`の両方を書く。
5. **Generate reproducibly**
  - generator script、GIF、静止fallback、必要ならsource snapshotを残す。
  - 数値を手入力せずsource artifactから読む。
6. **Validate mechanically**
  ```powershell
  python scripts/validate_animation.py output.gif `
    --expected-width 1200 --expected-height 675 `
    --timing-mode illustrative `
    --contact-sheet output-contact.jpg `
    --report output-validation.json
  ```
7. **Inspect visually**
  - 開始・中間・終了frameを原寸とtarget embed幅（mobileは約360px）で確認する。
  - text overlap、clip、順序、空白、読めない注記、英語UI残存を直して再生成する。

## Timing Rules

- GIFの総再生時間がAPI latencyと一致するとは限らない。自動で同一視しない。
- 複数requestの合計は、並列か直列かを表示する。
- 比較対象の測定境界が違う場合は、`model speed`ではなく`observed end-to-end time`として扱う。
- 推定費用、正解率、token数もsource artifactと照合し、asset単体で誤読しない注記を入れる。

## Done Criteria

- [ ] GIFがanimatedで、期待寸法・最小frame数を満たす。
- [ ] timing modeと測定境界がasset内に見える。
- [ ] source artifactの数値と表示値が一致する。
- [ ] 説明UIが読者言語に統一されている。
- [ ] 開始・中間・終了frameとループ再生を確認した。
- [ ] target embed幅で文字が読める。
- [ ] generator、GIF、静止fallback、validation reportの所在を報告した。
