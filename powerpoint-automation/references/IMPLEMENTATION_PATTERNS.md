# Implementation Patterns

PowerPoint Automation の本体 SKILL から切り出した、実装寄りのレシピ集。

## Technical Content Verification

Azure / Microsoft 系の技術内容をスライドへ追加するときは、生成より先に一次情報確認を行う。

### Standard Flow

```text
[Content Request] -> [Researcher] -> [Reviewer] -> [PPTX Update]
```

### Required Steps

1. `microsoft_docs_search` / `microsoft_docs_fetch` で一次情報を取る
2. 内容をレビューしてから content.json を更新する
3. 生成前に PowerPoint が対象ファイルを開いていないことを確認する

### Forbidden

- 技術内容を未検証で足す
- 「簡単な追加だから」とレビューを飛ばす
- 開いている PPTX に対してそのまま生成する

## Shape-based Architecture Diagrams

アーキテクチャ図は ASCII art ではなく PowerPoint shapes で組む。

### Design Rules

- `Cm()` ベースで配置する
- Azure / on-prem / cross-connect は色で分ける
- ラベルは図形の内側に置く
- ゾーン間は最低 1.5cm ほど空ける

### Anti-patterns

- ASCII art を textbox に入れる
- 図形同士が重なる
- ラベルが外に出る
- 絶対値だけで配置して再利用できない

## Hyperlink Batch Processing

URL を含むランや appendix の参考 URL は、生成後に一括で linkify する。

### Basic Pattern

```python
import re

url_pattern = re.compile(r'(https?://[^\s\)）]+)')
for slide in prs.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                for url in url_pattern.findall(run.text):
                    if not (run.hyperlink and run.hyperlink.address):
                        run.hyperlink.address = url.rstrip('/')
```

### When `run.hyperlink.address` Fails

既存 PPTX のレイアウト変更後などで通常 API が効かない場合は、XML の `a:hlinkClick` を直接追加する。

## Font Theme Token Resolution

python-pptx が `+mn-ea` や `+mj-lt` の theme token を解決しない場合は、保存後に ZIP レベルで XML を置換する。

### Rule

- `prs.save()` の**後**に行う
- `+mn-ea`, `+mj-ea` は和文フォントへ
- `+mn-lt`, `+mj-lt` は欧文フォントへ

## Section and Layout Management

python-pptx は section API や安全な layout swap を持たない。必要なら XML / ZIP を直接扱う。

### Section Update

- `ppt/presentation.xml` の extension に section 情報が入る
- 既存 section XML は削除してから入れ直す
- 変更確認は PowerPoint を再オープンして行う

### Safe Layout Change

推奨は **add -> move -> hide -> cleanup**。

1. 新しい layout で末尾に slide を追加
2. 必要な title を入れる
3. XML で新 slide を旧位置へ移動
4. 旧 slide を hidden にして空にする
5. 別 pass で hidden slide を削除する

### Forbidden

- `rel._target = new_layout.part` を ZIP dedup なしで使う
- `drop_rel()` だけで slide deletion を済ませる
- index 変動を無視して hidden 化する
- 空 placeholder を残したままレイアウトだけ変える

## Ghost Placeholder Elimination

`Title and Content` や `Section Title` を既存 PPTX に追加すると、空 placeholder が見えてしまうことがある。

### Safe Rule

- 新規 slide は `Blank` レイアウトを優先する
- title placeholder は実タイトルを入れる
- 空 body placeholder は削除する

## Post-processing and File Lock

`create_from_template.py` は `footer_url` を処理しない。URL は post-processing で入れる。

For open PowerPoint files or direct COM edits, use [instructions/com-automation.instructions.md](instructions/com-automation.instructions.md) as the detailed rule source.

### Items Requiring Post-processing

- `footer_url`
- bullets 内 URL
- appendix の reference URL

### Save With Different Name

PowerPoint が開いているファイルは同名保存で `PermissionError` になりやすい。保存先は別名にする。

## 16:9 Centering

`Presentation()` 既定の placeholder は 4:3 基準。後から 16:9 にしても placeholder 位置は自動で中央化されない。

### Recommended Pattern

- `Blank` レイアウトを使う
- slide width を基準に textbox を手動配置する
- 既存 16:9 テンプレートがあるならそちらを優先する

## Template Corruption Recovery

`.gitattributes` の `*.pptx binary` が遅れて入ると、既に add 済みの PPTX が壊れることがある。

### Symptoms

- UTF-8 replacement char (`EF BF BD`) が混入する
- PowerPoint repair dialog が出る

### Recovery

- python-pptx で空テンプレートを再生成する
- `.gitattributes` を先に整えてから再管理する

## Video Embedding

python-pptx は MP4 埋め込みを公式にはサポートしないが、ZIP 直接操作で埋め込みは可能。

### Required Pieces

1. slide XML に `a:videoFile` と `p14:media` を追加
2. slide rels に video / poster image を追加
3. `[Content_Types].xml` に `video/mp4` を追加
4. `ppt/media/` に MP4 と poster image を入れる

### Rule

- 単純な slide 生成と混ぜず、専用 pass で扱う
- 埋め込み後は PowerPoint 実機で必ず再生確認する

## Image Insertion via COM

COM `Shapes.AddPicture` で外部画像をスライドに配置する。

### Basic Pattern (PowerShell)

```powershell
$pic = $slide.Shapes.AddPicture(
    $filePath,
    0,    # LinkToFile = false
    -1,   # SaveWithDocument = true
    $left, $top, $width, $height
)
$pic.Name = 'SlideImage'
$pic.LockAspectRatio = -1
```

### Aspect Ratio and Centering

挿入後に target area の中央へ配置する:

```powershell
$scaleW = $targetW / $pic.Width
$scaleH = $targetH / $pic.Height
$scale = [math]::Min($scaleW, $scaleH)
if ($scale -lt 1.0) { $pic.Width *= $scale; $pic.Height *= $scale }
$pic.Left = $targetL + ($targetW - $pic.Width) / 2
$pic.Top  = $targetT + ($targetH - $pic.Height) / 2
```

### SVG Support

- Office 365 / Office 2021+ は SVG を `AddPicture` で直接挿入可能。
- 挿入後のサイズは SVG の viewBox に依存するため、必ず明示的に幅・高さを指定する。
- 古い Office では EMF 変換が必要。

### Rules

- 画像名は `SlideImage` で統一し、再実行時に既存を削除してから挿入する。
- 画像と本文テキストが重ならないよう、画像挿入後に body 幅を狭める（callout 有りスライドと同じ 465 pt 前後）。
- 画像元が公式ドキュメントの場合、RefURL で出典 URL を付ける。

## Font-Fit Pattern

利用可能な高さ内で最大フォントサイズを選ぶ。

### Algorithm

```powershell
$sizes = @(24, 22, 20, 18)
foreach ($size in $sizes) {
    for ($i = 1; $i -le $paraCount; $i++) {
        $body.TextFrame.TextRange.Paragraphs($i).Font.Size = $size
    }
    if ($body.TextFrame.TextRange.BoundHeight -le $availableHeight) {
        break
    }
}
```

### Rules

- `BoundHeight` は PowerPoint が内部で再計算する値。assignment 直後に読める。
- 日本語テキストは同じ pt でも行送りが広い。候補サイズに余裕を見る。
- 16 pt 未満まで落ちたら「テキスト量削減 or スライド分割」を優先する。

## Manual Bullet Normalization

既存 deck がオートビュレットと手動記号を混在させている場合の統一手順。

### Pattern

```powershell
# 全行を「・ 」prefix で rebuild し auto-bullet を OFF にする
$lines = @('item1', 'item2', 'item3')
$bulleted = $lines | ForEach-Object { '・ ' + $_ }
$body.TextFrame.TextRange.Text = $bulleted -join [char]13

$pc = $body.TextFrame.TextRange.Paragraphs().Count
for ($i = 1; $i -le $pc; $i++) {
    $body.TextFrame.TextRange.Paragraphs($i).ParagraphFormat.Bullet.Type = 0
}
```

### Rules

- per-paragraph `.Text` 代入でなく、TextRange 全体を 1 shot で書き換える（index ずれ防止）。
- `Bullet.Type = 0` で自動ビュレットを無効化してから手動記号に揃える。
- 既存テキストから rebuild する場合、先頭の `・` / `■` / `●` を strip してから新 prefix を付ける。
