---
name: repurpose-deck-from-reference
description: Build a new-topic PPTX by reusing an existing reference deck's template (layouts / footers / fonts / palette) while replacing all content from primary sources. Use when "this Scout deck → make a GitHub Copilot app deck", "use this deck as template for new topic", "参照デックの体裁で別内容を作る", "既存 PPTX を流用して別テーマで作り直す". Different from translation (use powerpoint-automation) and from-scratch generation.
argument-hint: "<reference.pptx> と <new topic> + 一次情報 URL / 出典"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Repurpose Deck From Reference

参照 PPTX のテンプレ体裁（レイアウト・フッター・フォント・配色・章割りの作り）だけを残し、内容を **新トピックの一次情報** で書き直す skill。

## When to Use

- "この Scout 紹介資料の体裁で GitHub Copilot app 資料を作って" のような依頼
- 既存テンプレ deck を別プロダクト / 別テーマ向けに作り変える
- 一次情報（公式 docs / repo / changelog）を集めて新内容を組み立て、実機スクショで強化したい
- セクション構成も新トピックに合わせて再設計してよい

Use a different skill if:
- 翻訳・content.json 抽出ベースで作りたい → **powerpoint-automation**
- ゼロから作る → **powerpoint-automation** の create-from-template
- 設計・骨子だけ作りたい → **powerpoint-planning**

## Workflow

```
COPY → RESEARCH → PLAN → WIPE → BUILD → SCREENSHOTS → QA → POLISH
```

| Phase | 目的 | 主な落とし穴 |
| --- | --- | --- |
| **COPY** | 参照 deck を新ファイル名でコピー、編集対象を固定 | 参照を破壊しない |
| **RESEARCH** | 一次情報を `web_fetch` で複数 ドキュメント / repo README / changelog を取得 | スニペットだけで決めない、最新版を確認 |
| **PLAN** | セクション構成と各スライド要旨を SQL todos か markdown で先に固める | 参照のセクション数に縛られない |
| **WIPE** | 各スライドの shape を整理。layout を「白紙」に揃え、layout 由来 `p:bg` を除去 | hidden slide の扱いに注意 |
| **BUILD** | スライドごとに add_shape / add_textbox で再構築。footer ロゴ・ページ番号を付与 | 負数 width/height で COM open 不能になる |
| **SCREENSHOTS** | 実機の UI を `PrintWindow` でキャプチャ、PII を mask して挿入 | 個人 PJ 名・リポ名・ユーザー名を必ず黒塗り |
| **QA** | 全スライド PNG 化して **sub-agent で批評** させる、自分で見ずに済まさない | "looks fine" の自己評価は禁止 |
| **POLISH** | QA 結果を 1 ファイルにまとめて一括反映、再 QA | カードに空白多すぎ / 色 system 揺れを必ず潰す |

## Core Rules

- **One file, not multiple drafts.** 参照を直接コピーして、その 1 ファイルを iterate する。古い draft は残さない。
- **Lock-first.** 編集前に必ず `Get-Process POWERPNT | Stop-Process -Id`。OneDrive 同期完了を待つ。
- **Layout reset.** 参照のコンテンツスライドは原則「白紙」レイアウトに切替＋`<p:bg>` 除去。これをやらないと旧テンプレの装飾が透けて見える。
- **No negative dimensions.** `Emu(w - X)` で X > w の状況を作らない。`max(min_h, h - margin)` でクランプ。
- **COM cache bypass.** 直近編集ファイルを COM で開くと古いコンテンツが返る場合あり。**毎回別ファイル名にコピーしてから Open**。
- **Primary source over memory.** 仕様・対象プラン・価格は memory に頼らず必ず一次情報を `web_fetch`。例: GitHub Copilot app の対象プランは公式 README で "Pro / Pro+ / Max / Business / Enterprise" と最新化されている。
- **Section list = raw XML.** `python-pptx` は PowerPoint セクションをサポートしない。`presentation.xml` に `p14:sectionLst` を直接挿入する。**`&` は必ず `&amp;` にエスケープ**しないと COM 開けない。
- **Layout consistency before content polish.** 18 枚作って 6 セクション正しく入る、ページ番号通る、フッター揃う、を先に確認してからコンテンツ詳細を直す。

## Hard Gotchas

- **Negative dim corruption**: `add_textbox(..., h=h-650000)` で h が 650000 未満になると、python-pptx は保存できるが PowerPoint COM Open が失敗する。GUI からは開ける。バイセクションでスライド単位の犯人探しが必要になる。
- **COM Export cache**: `app.Presentations.Open(SAME_PATH)` を連続で叩くと、PowerPoint 内部が古い CRC を持つ場合あり、Export 画像が更新後の中身を反映しない。**新しいファイル名へ copy してから Open**。
- **OneDrive 同期と Office lock**: OneDrive 配下 PPTX の編集中、`FileCoAuth` が `PackageNotFoundError` を起こすことがある。`Stop-Process -Id <FileCoAuth_PID>` で解放。
- **Section XML escape**: `<p14:section name="D. Customize & Collaborate">` は `&` で XML 不正。`&amp;` に escape。
- **Hidden slide page numbering**: `show="0"` のスライドをスキップしてページ番号を振ると、見えないスライド以降の番号が前にずれる。**hidden を含めた絶対インデックス** で振る方が一貫する。

## Quick Start

詳細は [references/](references/) を参照。

```text
1. ユーザー: "この Scout deck の体裁で GitHub Copilot app 資料作って"
2. COPY: 参照を新ファイル名でコピー
3. RESEARCH: web_fetch で公式 docs / repo README / changelog を取得
4. PLAN: SQL todos で section 構成 + 各 slide 要旨を確定
5. WIPE → 白紙レイアウト + bg 削除 + footer 維持
6. BUILD: スライドごとに rebuild_deck.py で再構築
7. SCREENSHOTS: PrintWindow キャプチャ → PII mask → 挿入
8. QA: sub-agent で全 PNG 批評 → 修正
9. POLISH: 色 system 統一、約物統一、余白統一
```

## References

- [references/workflow-detail.md](references/workflow-detail.md) — 各 phase のコマンド例
- [references/screenshot-mask-pattern.md](references/screenshot-mask-pattern.md) — PrintWindow + Gaussian blur + 説明 overlay
- [references/com-and-xml-pitfalls.md](references/com-and-xml-pitfalls.md) — 既知の COM / XML 罠
- [references/section-xml-template.md](references/section-xml-template.md) — `p14:sectionLst` 挿入のひな型

## Done Criteria

- 参照 deck のコピー 1 ファイルを正として iterate できている
- セクション構成が新トピックに最適化されている（参照と同じである必要なし）
- 全本文が一次情報出典付き（Source: 行をスライド下部に明記）
- 実機スクショは PII マスク済み（個人 PJ 名・リポ・ユーザー名・チャット名）
- sub-agent による視覚 QA を 1 回以上回している
- 色は 5 色程度に絞られ、未定義色（赤・マゼンタ等の浮き）が無い
- COM Open テストが通っている（負数 dim / XML escape / cache を踏んでいない）
