# Workflow Detail

各 phase の代表的な手順とコマンド例。

## COPY

```powershell
$src = "<reference.pptx>"
$dst = "<new-topic>.pptx"
Copy-Item -LiteralPath $src -Destination $dst -Force
```

参照は読み取り専用扱い。以降の編集は全部 `$dst` に対して。

## RESEARCH

公式 docs / repo / changelog を `web_fetch` で複数取得し、対象機能と最新仕様を把握。

- 製品公式 docs（概念・howto・getting-started）
- 公式 GitHub repo の README
- changelog.md（直近 2-3 リリース分）
- 価格 / 対象プランは特に注意（一次情報の表記が他より新しいことがある）

例:

```text
web_fetch https://docs.github.com/en/copilot/concepts/agents/github-copilot-app
web_fetch https://raw.githubusercontent.com/github/app/main/README.md
web_fetch https://github.com/github/app/blob/main/changelog.md
```

## PLAN

SQL `todos` or `new_deck` テーブルに 1-N 枚分の `(slide_idx, title, source)` を入れる。

```sql
CREATE TABLE new_deck (idx INT PRIMARY KEY, title TEXT, source TEXT);
INSERT INTO new_deck VALUES
  (1, 'Title', 'kept'),
  (2, 'XXX とは', 'docs.github.com/...');
```

参照 deck のセクション数に縛られない。新トピックに合わせて再設計する。

## WIPE

- 不要スライドを削除（`sldIdLst` から remove + `drop_rel`）
- 各スライドのレイアウトを「白紙」に変更
- レイアウト由来の `<p:bg>` を削除（白紙レイアウトでも slide 自体に残る場合あり）

## BUILD

1 ファイル `rebuild_deck.py` に全スライド分の生成コードを書く。共通ヘルパー:

- `add_text(slide, left, top, w, h, text, *, size, bold, color, font)`
- `add_card(slide, left, top, w, h, title, body, accent)` — 角丸 + 上端カラーバー + title + body
- `add_numbered_step(slide, ..., num, title, body, accent)` — number circle + title + body
- `add_screenshot(slide, png, ..., caption)` — drop shadow + picture + caption

カードの高さは body の行数で min/max クランプ。`max(min_h, h - margin)`。

## SCREENSHOTS

[screenshot-mask-pattern.md](screenshot-mask-pattern.md) を参照。

## QA

`task` ツールで sub-agent (`general-purpose`) に全スライド PNG を見せて、issues を列挙させる。

```text
You are a strict visual designer. Inspect each slide image carefully.
Assume there are problems — find them all.

For each slide report: overlapping elements, text overflow, low contrast,
inconsistent gaps, insufficient margins, leftover placeholder content,
information density issues.

Read all N images, report ALL issues including minor ones.
Do not say "looks fine".
```

## POLISH

QA 結果を 1 つの修正スクリプトにまとめて適用。色 system 統一、余白統一、約物統一を優先。
