---
name: azure-screenshot-mask
description: "Mosaic environment-sensitive areas (tenant name, user avatar, subscription name / ID, resource group, internal hostnames) on Azure Portal screenshots before publishing to blogs, Qiita, Medium, slides, or demos. Use when sanitizing screenshots, masking env info, or preparing portal captures for public sharing. Keywords: Azure Portal, screenshot, mask, mosaic, sanitize, tenant, subscription, hinokuni, public publishing, blur, redact."
argument-hint: "対象スクリーンショット (PNG / フォルダ) と、追加でマスクしたい領域があれば領域名や座標"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Azure Screenshot Mask

Azure Portal のスクリーンショットに残る環境固有情報を、公開前にまとめてモザイクで消すための skill。

## When To Use

- Azure Portal のスクリーンショットをブログ、Qiita、Medium、note、社外スライド、デモ動画に載せる前
- 同じテナントや顧客環境で連続して撮ったキャプチャを、一気にサニタイズしたいとき
- 「本文では伏せたのに画像内に名前が残っていた」を防ぎたいとき

## Core Principles

- **本文を伏せても画像内に残れば公開情報になる**。画像を別レビューで必ず目視する
- **右上のテナント表示はほぼ常に対象**。viewport 1912 px の Azure Portal なら右端 `(W-320, 0, W, 44)` のストリップで覆える
- **本文中の subscription 名 / ID / RG 名は座標が画面ごとに違う**。事前に値の有無を見て、必要な領域だけ追加で渡す
- **モザイクは元データを破壊する**。再撮りや再生成に備えて `.bak.png` を残せる手段を用意する
- **資源名そのものもマスク対象になりうる**。ラボ用に作った短命リソース名でも、ユニークな文字列は特定可能。本文で明示していても、画像内では先頭数文字だけ残してマスクするのが安全

## What To Mask (Checklist)

公開前に最低限見るリスト。残っていればモザイクをかけるか撮り直す。

- **右上のテナント表示** (`HINOKUNI (...)` など organization 名、user の頭文字アバター)
- **サブスクリプション名** (例: `*-sub`、顧客名入りの命名)
- **サブスクリプション ID** (GUID。Portal の "リソース ID" や "サブスクリプション ID" 欄に出る)
- **テナント ID** (GUID。Entra ID 関連画面で見える)
- **リソースグループ名** (内部コードや顧客プロジェクト名を含む場合)
- **個人ユーザーの UPN / メールアドレス**
- **内部ホスト名 / FQDN / Private IP / Public IP**
- **アカウント表示の onmicrosoft ドメイン**
- **リソース名**（Storage Account 名、task 名、assignment 名など）ユニークな文字列は先頭数文字だけ残してマスクする

逆に、汎用の lab 用に作った storage account 名や resource 名でも、ユニークな文字列は特定可能なのでマスク推奨。

## Default Workflow

1. **対象画像を 1 フォルダにまとめる**

   - 記事に貼る画像を `images/<platform>/<article>/` 配下に集約しておく
   - 同じ Portal 解像度 (viewport 幅) で揃っていると、領域指定を使い回せる

2. **右上テナント帯だけでよいか確認する**

   - フォルダ内の代表 1 枚を開き、右上の組織表示・アバターだけが env-sensitive か確認する
   - 本文側に subscription 名 / ID / RG 名が見えていれば、その行も対象にする

3. **モザイクをかける**

   ```powershell
   # フォルダ内の PNG 全部に対し、右上テナント帯だけ覆う
   python <skill-path>/scripts/mosaic-azure-screenshots.py images/qiita/<article>

   # 単一画像 + 追加領域（例: 概要画面のサブスクリプション名 / ID 行）
   python <skill-path>/scripts/mosaic-azure-screenshots.py images/qiita/<article>/overview.png `
     --region 450,277,740,304 `
     --region 450,308,920,335

   # 元画像を保険として残したい
   python <skill-path>/scripts/mosaic-azure-screenshots.py images/qiita/<article> --backup
   ```

4. **目視で検証する**

   - 上記チェックリスト項目が読めなくなっているか、画像ビューアで確認する
   - 1 枚でも残っていれば、その画面だけ `--region` を足して再実行する

5. **記事側のテキストも合わせて整える**

   - 本文に `hinokuni-sub` のような subscription 名や顧客固有名が出ていたら削除する
   - 「環境固有情報はスクリーンショット上でマスクしています」のような 1 行を入れておくと、読者が画像のモザイクを誤読しない

## Script

このスキルには CLI スクリプト [scripts/mosaic-azure-screenshots.py](scripts/mosaic-azure-screenshots.py) を同梱している。Pillow ベースで pixel mosaic をかける。

主な引数:

| 引数 | 説明 |
| --- | --- |
| `path` | PNG ファイル、または PNG を含むディレクトリ |
| `--region L,T,R,B` | 追加でマスクする領域 (px 座標)。繰り返し指定可 |
| `--topright-width` / `--topright-height` | 右上テナント帯のサイズ調整 (既定 320 × 44) |
| `--no-topright` | 既定の右上ストリップを無効化 |
| `--block` | モザイクのブロックサイズ (既定 14 px) |
| `--backup` | `<name>.bak.png` を残してから上書きする |

依存: `Pillow`。`pip install pillow` で導入できる。

## OCR Fallback

`--region` 座標指定でテーブル行や詳細ペイン内のテキストに当たらない場合は、OCR（Surya）でテキスト bbox を取得してから Pillow で直接モザイクをかける。

手順:

1. `ocr-super-surya` skill で画像を OCR し、各テキスト行の `text` と `bbox [x1, y1, x2, y2]` を取得する
2. マスク対象のキーワード（例: `stmock`, `hinokuni`）を含む行をフィルタする
3. bbox の先頭数ピクセルを残し、残りを Pillow の resize (NEAREST) でピクセル化する

```python
MASK_PATTERNS = ["stmock", "hinokuni"]  # マスク対象キーワード
KEEP_PX = 30  # 先頭何 px を残すか

for line in page.text_lines:
    text = line.text.strip()
    if any(pat in text.lower() for pat in MASK_PATTERNS):
        x1, y1, x2, y2 = [int(v) for v in line.bbox]
        mask_x1 = x1 + KEEP_PX  # 先頭を残す
        region = img.crop((mask_x1, y1, x2, y2))
        block = 8
        small = region.resize((max(1, (x2-mask_x1)//block), max(1, (y2-y1)//block)), Image.NEAREST)
        img.paste(small.resize((x2-mask_x1, y2-y1), Image.NEAREST), (mask_x1, y1))
```

依存: `surya-ocr`, `Pillow`。`ocr-super-surya` skill の環境を使う。

## Tips

- **viewport を毎回 1912 px 前後に揃える**と、`--topright-*` を毎回触らずに済む
- **座標は 1 枚で決めて使い回す**。ある記事の overview 画面で `(450,277,740,304)` が subscription 行に当たれば、同じ Portal レイアウトの別キャプチャでも流用しやすい
- **モザイクの代わりに塗りつぶしで十分**な場合は、Snipping Tool / Snagit / Greenshot などの注釈機能を使い、本 skill のスクリプトは一括処理が必要な時だけに絞ってよい
- **Public IP の判別が必要**な場合は、`subscription` / `tenant` / `IP` を一気にマスクするより、IP は別途 RDAP で意味付けしてから判断する（公開可否は所有者で変わる）

## Related Skills

- `humanize-writing`: 本文のサニタイズや AI 感の除去。同じ「公開前の最終チェック」フローで一緒に走らせると効率がよい
- `packet-capture-analysis`: pcap の中身を画像化する際の env-sensitive 領域マスクは別 skill。本スキルは Azure Portal キャプチャに特化
