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

## Template-Based Slide Editing Order

既存 PPTX をテンプレートとして使うときは、構造編集と内容編集を混ぜない。

### Recommended Flow

1. `thumbnail.py` でレイアウトの見た目を確認する
2. `markitdown` などで placeholder / 残存テキストを確認する
3. content section ごとに slide layout を割り当てる
4. slide の削除、複製、並び替えなどの構造変更を先に完了する
5. その後で slide XML のテキストや画像を差し替える
6. `clean.py` / pack / render QA の順に確認する

### Layout Mapping Rules

- title + bullet の単調な繰り返しを避け、2 column、image + text、quote、section divider、stat callout などを混ぜる
- template slot と source item 数が合わない場合は、余った text box だけを空にせず、対応する image / shape / text の group 全体を削除する
- 1 つの textbox に複数の論点を連結せず、論点ごとに paragraph を分ける
- 構造変更後の slide XML 編集は、対象 slide が独立していれば並列化してよい

### Anti-patterns

- slide の追加・削除・移動と text replacement を同じ pass で混ぜる
- template の 4 枠に対して source が 3 件なのに 4 枠目の文字だけを消す
- numbered steps や複数 section を 1 paragraph に詰め込む
- `thumbnail.py` の overview だけで visual QA を完了扱いにする

### Rebuild Discipline

- Before rebuilding a deck, pick one canonical output filename. Do not keep producing `backup`, `clean`, `formatted`, `final`, and PDF variants in parallel.
- Keep source content in a separate Markdown/JSON draft until the story is stable. Then generate one working PPTX and iterate on that file only.
- If a template-derived output becomes visually corrupt, create one new template-based working copy and retire the failed variant. Do not stack more fixes on multiple partially failed decks.
- Rendered QA artifacts such as PDF, PNG contact sheets, and temporary scripts are transient. Delete them before handoff unless the user explicitly asks to keep evidence.
- When COM hangs while setting hyperlink `ActionSettings`, keep visible URLs in the deck and apply hyperlinks in a separate small post-processing pass.

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

### COM Section Rebuild (Build End)

スライド挿入順や hidden 化で位置が動く生成系は、静的 section 定義より **Build 末尾での動的再構築**が安定する。`SectionProperties.Delete()` で全削除後、`AddBeforeSlide($pos, $name)` を順番に呼ぶ。`$pos` はシェイプ名（例: 表紙群を判定する独自 `CoverPanel` のような名前付き shape）で動的検出し、固定値を避ける。

### Slow Master Cleanup on OneDrive

`SlideMaster.CustomLayouts.Delete()` を一括 (10 件以上) 実行すると、OneDrive 上では `Presentations.Open()` 後の応答が数分以上停止する。対策は次のスロー削除パターン:

1. 1 件削除 → 0.5 秒 Sleep
2. 5 件ごとに `$pres.Save()`
3. 一度に削除する件数は引数で制限可能にする (例: `-MaxRemove 5`)
4. 削除前にテンプレ事前バックアップ (`backup-yyyyMMdd-HHmmss/`) 必須

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

`.gitattributes` の `*.pptx binary` が遅れて入ると、既に add 済みの PPTX が壊れることがある。拡張子が `.pptx` でも実体が古い OLE 形式のこともある。

### Symptoms

- UTF-8 replacement char (`EF BF BD`) が混入する
- PowerPoint repair dialog が出る
- First bytes are `D0 CF 11 E0` instead of ZIP magic `50 4B`; `python-pptx` reports `PackageNotFoundError`.
- File opens in PowerPoint but cannot be read as a ZIP package; this usually means the extension is `.pptx` but the body is legacy OLE/binary.

### Recovery

- python-pptx で空テンプレートを再生成する
- For OLE-format templates, keep the source file untouched and use PowerPoint COM `SaveAs(..., 24)` to create a temporary normalized `.pptx` copy.
- Do not trust `SaveCopyAs` for normalization; it can preserve the legacy/OLE body. After conversion, verify the output starts with `PK` and passes `zipfile.ZipFile(path).testzip()` before treating it as a real `.pptx`.
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

### Per-shape Font Loop on OneDrive (Forbidden)

OneDrive 上で生成済みスライドのシェイプを per-shape ループして `Font.NameFarEast` / `Font.Name` を設定すると、フェーズ途中で数分以上応答しなくなる (OneDrive 同期との競合)。

- 推奨: フォント設定は **テンプレ側 (`SlideMaster.CustomLayouts` のプレースホルダ)** で 1 回適用し、生成スライド側の per-shape ループは行わない
- どうしても per-shape 設定が必要なら、OneDrive 同期を一時停止してから実行
- `AutoSize=2` (`ppAutoSizeTextToFitShape`) を本文 placeholder に設定すれば、フォント縮小は自動化される。per-shape のフォントサイズ走査ループは不要になることが多い

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

## PptxGenJS Hardening

PptxGenJS は無効な option でも silent failure や破損ファイルになりやすい。生成スクリプトでは次を守る。

### Rules

- 色は 6 桁 hex のみを使い、`#` prefix や 8 桁 alpha 付き hex を使わない。透明度は `opacity` / `transparency` option で表す
- shadow や line などの option object は call ごとに新規作成する。PptxGenJS が object を mutate するため、同一 object を再利用しない
- 箇条書きは `bullet: true` と `breakLine: true` を使い、手動 bullet 文字を text に入れない
- bullets では `lineSpacing` より `paraSpaceAfter` を優先する
- 文字間隔は `charSpacing` を使う。`letterSpacing` は効かない
- shape や icon と text の左端を揃えるときは text box の `margin: 0` を明示する
- 角丸 card に矩形 accent bar を重ねると角が合わない。accent bar を使う card は `RECTANGLE` を優先する
- deck ごとに新しい `pptxgen()` instance を作る

### Review Focus

- double bullet、行間の過剰な広がり、accent bar の角ずれ、shadow の破損を生成後に見る
- chart は default のままにせず、series colors、grid line、data label、legend 表示を明示する

## Rendered Slide QA Loop

PPTX の最終確認は XML や text extraction だけで終えない。必ず実レンダー結果を見る。

### Content QA

- `markitdown` などでテキスト抽出し、欠落、誤字、順序、placeholder 残りを確認する
- template 利用時は `xxxx`, `lorem`, `ipsum`, `this page`, `this slide` などの placeholder 文字列を検索する

### Visual QA

- LibreOffice などで PDF 化し、`pdftoppm` などで slide image に変換して確認する
- Contact sheet は全体傾向の把握用に留める。編集した slide、表 slide、タイトル/本文を大きく動かした slide は必ず個別画像で読む
- 最初の render は問題がある前提で見る。問題が 0 件なら、overlap、overflow、edge cut-off、footer/source collision、低コントラスト、余白不足をもう一度探す
- 可能なら fresh-eye reviewer / subagent に画像を見せ、期待内容と照合させる
- 修正後は対象 slide だけでも再レンダーし、1 回以上 fix -> verify を回す

### Visual QA Checklist

- text が shape / image / footer と重なっていない
- 追加した card / callout の下に、元 title・bullet・table・source が残って透けたり重なったりしていない
- title wrap により装飾線やアイコン位置がずれていない
- margin が 0.5 inch 相当未満に詰まりすぎていない
- columns / repeated cards の位置と gap が揃っている
- low-contrast text / icons がない
- source citation や RefURL が本文と衝突していない
- placeholder や空 slot が残っていない

## Inline Label Body

ラベル + 値を別段落で出すと行数が倍になりオーバーフローしやすい。`対象：\n  Azure NetApp Files` のように 2 段で書くと 8 項目で 16 行使ってしまう。`対象：Azure NetApp Files` の 1 行に統合するだけで複数項目の本文は 7-8 行短縮できる。

### Rules

- `TextRange.Text` の 1 shot 代入で `"対象：${value}"` のように先頭にラベルを含めて書く
- ラベル文字列だけを `Characters($pos+1, $len)` で取り出して `Font.Bold = -1` + 色変更し、ラベルだけ強調する
- 値が長い時は値だけ折り返し、ラベルは行頭から始まる。`AutoSize=2` と組み合わせると枠内に確実に収まる

## Status Badge Overlay

本文スライド右上に状態 (GA / Preview / Retirement / Announcement / Update など) を示す独自バッジを置くパターン。

### Rules

- バッジは `AddShape(5, ...)` (msoShapeRoundedRectangle) で配置し、`Shape.Name = 'StatusBadge'` で識別
- 同名 shape を先に削除してから追加 (再実行耐性)
- バッジ追加後、タイトル shape の `Width` を **バッジ左端の手前まで自動縮小** する。これを忘れると長文タイトルがバッジに重なる
- 配色はテーマの accent カラー (`accent1` / `accent2`) に揃え、状態ごとに色相だけ変える
- フォントは Segoe UI 等の半角向けを使う (BIZ UDP は短文ラベルだと幅が広く崩れる)
- 右下のリージョン / 地域スタンプとの**情報重複**は許容する (本文は代替案・スタンプは一目情報の役割分担)

## Multi-variant Cover

表紙を 3 パターン用意し、本番表示は 1 つ・残りは末尾に非表示で同梱するパターン。デザインレビュー後に差し替えやすい。

### Rules

- 全パターンに共通の名前付き shape (例 `CoverPanel`) を必ず置き、Build / Verify 側がこれで表紙群を動的検出できるようにする
- 本番表示は先頭 1 枚、バリエは末尾 (`MoveTo($pres.Slides.Count)`) に退避し `SlideShowTransition.Hidden = -1`
- Section 再構築時は `CoverPanel` を持つ連続スライド範囲を `visibleCoverEnd` として検出し、サマリ / 本文開始位置を動的に決める
- バリエ表紙は専用 section として末尾に配置する
