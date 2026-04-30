---
name: receipt-ocr-sorter
description: "OCR領収書自動仕分けツール。画像(JPEG/PNG)/PDF/ZIP/動画(MP4/MOV)の領収書をOCRで読み取り、日付・金額・国・カード・用途を抽出して標準ファイル名にリネーム＆プロジェクト単位で仕分ける。Markdownサマリーレポート付き。D365 Expenseカテゴリマッピング・レシート添付連携対応。Use when: (1) 領収書の整理, (2) receipt sorting, (3) レシート仕分け, (4) 経費レシートをフォルダ整理, (5) OCRでリネーム, (6) D365経費カテゴリマッピング。Surya OCR + GPU(CUDA)対応。"
argument-hint: "仕分けたい領収書フォルダ、対象プロジェクト、必要な出力"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Receipt OCR Sorter

OCR（Surya）を使った領収書の自動仕分け・リネーム・集計ツール。

## When to Use

- **領収書を仕分けて**, **レシートを整理して**, **receipt sorting**
- フォルダ内の領収書画像をプロジェクト単位で自動整理したい
- 大量のレシート写真に日付・金額・用途でファイル名を付けたい
- 出張経費の領収書を一括でリネーム＆集計したい

## Core Workflow

1. 入力フォルダの画像 / PDF / ZIP / 動画を受け取る
2. OCR で日付・金額・国・カード・用途を抽出する
3. 品質補正をかけて標準ファイル名へ正規化する
4. プロジェクト単位で仕分ける
5. Markdown サマリーを出す

## Architecture

```
入力フォルダ（未仕分け/iCloud写真 等）
  │
  ├─ JPEG/PNG/PDF/ZIP → OCR → 抽出 → リネーム → PJフォルダへ移動
  ├─ MP4/MOV → ffmpeg → JPG → OCR → ...
  │
  ├─ カード不明 or テキスト不可 → 未分類フォルダ → 再仕分け可能
  │
  └─ 個人経費（D365対象外） → PJフォルダ/private/
```

> **`private/` フォルダ**: D365 に申請しない個人経費レシートを格納する。OCR後にユーザーが「個人経費」と判断した場合に移動する。

## Naming Convention

```
YYYY-MM-DD-国コード-金額[-カード]-分類.ext

例:
  2026-02-09-jpn-14320-amex-shinkansen.jpeg
  2026-02-11-us-272-amex-hotel.jpeg
  2026-02-12-us-190.38-meal.jpeg        ← カードなし
  2026-02-09-us-6.80-amex-meal-starbucks.jpeg
```

国コード一覧、分類一覧、D365 カテゴリ対応、添付手順は [references/d365-expense-guide.md](references/d365-expense-guide.md) を参照。

## CLI Usage

```powershell
# Dry-run（確認のみ、ファイル移動なし）
python receipt_sorter.py --project "202602_TechConnect_Seattle" --dry-run

# 本実行
python receipt_sorter.py --project "202602_TechConnect_Seattle" --input "未仕分け\iCloud写真"

# ログ指定
python receipt_sorter.py --project "202602_TechConnect_Seattle" --input "未仕分け\iCloud写真" --log "result.csv"
```

### Options

| オプション  | 説明                         | デフォルト                                            |
| ----------- | ---------------------------- | ----------------------------------------------------- |
| `--project` | 出力PJフォルダ名（必須）     | -                                                     |
| `--input`   | 入力フォルダ                 | `未仕分け/`                                           |
| `--dry-run` | ファイル移動せず結果のみ表示 | false                                                 |
| `--log`     | 結果CSVパス                  | `<PJフォルダ>/csv/<PJ名>_dryrun.csv` or `_result.csv` |

## Markdown Summary Output

本実行後、PJフォルダに `<PJ名>_summary.md` が自動生成される。

含む内容:

- プロジェクト合計（通貨混在・参考値）
- 国コード別合計テーブル
- 日付×国コード別合計テーブル
- 全明細テーブル（日付・国・金額・カード・分類・日本語概要・ファイル名）

## Setup

→ **[references/setup-guide.md](references/setup-guide.md)**

## Script Reference

→ **[references/receipt_sorter.py](references/receipt_sorter.py)**

## D365 Expense Integration

OCR 後のファイルを D365 Expense に添付する運用はこの skill の重要ユースケースだが、カテゴリ表と添付手順は本体から分離する。

- カテゴリ対応表
- 添付 / 差し替え手順
- 添付時の照合ルール
- ブラウザ操作の注意

詳細は [references/d365-expense-guide.md](references/d365-expense-guide.md) を参照。

## Known Limitations

- OCRの精度はSuryaモデルに依存（手書きや歪みが大きい領収書は誤読あり）
- 金額は最大候補を採用するが、複数明細のあるレシートでは個別明細は取れない
- **金額連結誤読**: OCRが改行をまたいで数字を結合し巨大整数を返すことがある（例: `14520` + `300` → `14520300`）。上限チェック（500万超は除外）で防御しているが、完全ではない
- 動画は中間フレーム1枚のみ抽出（最適フレーム選択は未実装）
- 日本語の漢字店名はスラッグ化時にASCII変換で落ちる（カタカナはローマ字化される）
- **Windows PIL ファイルロック**: `Image.open()` がハンドルを保持し `shutil.move()` が `WinError 32` で失敗する。`with` + `img.copy()` + リトライで対応済み

## Done Criteria

- OCR 抽出からリネームまで一貫して処理できる
- 標準ファイル名でプロジェクト単位に仕分けできる
- 未分類と private の扱いを説明できる
- Markdown サマリーが出力される
- D365 へ載せる場合は reference の照合ルールに従って添付できる
