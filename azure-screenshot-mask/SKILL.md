---
name: azure-screenshot-mask
description: "Mosaic environment-sensitive areas (tenant name, user avatar, subscription name / ID, resource group, internal hostnames) on Azure Portal screenshots before publishing to blogs, Qiita, Medium, slides, or demos. Use when sanitizing screenshots, masking env info, or preparing portal captures for public sharing. Keywords: Azure Portal, screenshot, mask, mosaic, sanitize, tenant, subscription, public publishing, blur, redact."
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

- **右上のテナント表示** (組織名、user の頭文字アバター)
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

   - 本文に `<顧客名>-sub` のような subscription 名や顧客固有名が出ていたら削除する
   - 「環境固有情報はスクリーンショット上でマスクしています」のような 1 行を入れておくと、読者が画像のモザイクを誤読しない

## Script

CLI は [scripts/mosaic-azure-screenshots.py](scripts/mosaic-azure-screenshots.py) を使う。引数、依存関係、OCR fallback、赤枠注釈は [Advanced Azure Screenshot Masking](references/advanced-masking.md) を必要時に読む。

## OCR Fallback

静的な `--region` が外れる場合だけOCRで確認済み文字列のbboxを取得し、対象boxをマスクする。実装例は [Advanced Azure Screenshot Masking](references/advanced-masking.md) を参照する。

## OCR-guided Highlight（赤枠注釈）

before / after比較では、確認済みbboxへ赤枠を付ける。マスク用途と混同せず、1画像2〜3箇所に絞る。実装例は [Advanced Azure Screenshot Masking](references/advanced-masking.md) を参照する。

## Tips

- viewportを揃え、代表画像で決めた座標を再利用しても全画像を目視する。
- 単発の塗りつぶしで済む場合は通常の画像注釈ツールを使う。詳細は [Advanced Azure Screenshot Masking](references/advanced-masking.md) を参照する。

## Related Skills

- `humanize-writing`: 本文のサニタイズや AI 感の除去。同じ「公開前の最終チェック」フローで一緒に走らせると効率がよい
- `packet-capture-analysis`: pcap の中身を画像化する際の env-sensitive 領域マスクは別 skill。本スキルは Azure Portal キャプチャに特化
