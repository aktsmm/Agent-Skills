# Implementation Patterns

PowerPoint Automation の本体 SKILL から切り出した、実装寄りのレシピ集。

## Technical Content Verification

Azure / Microsoft 系の技術内容をスライドへ追加するときは、生成より先に一次情報確認を行う。

Pricing, billing, deadline, supportability, and regional availability claims are high-risk: verify them against official/current sources, and use `要確認` rather than inventing or over-compressing when the source does not explicitly support the claim.

### Standard Flow

```text
[Content Request] -> [Researcher] -> [Reviewer] -> [PPTX Update]
```

### Required Steps

1. `microsoft_docs_search` / `microsoft_docs_fetch` で一次情報を取る
2. 内容をレビューしてから content.json を更新する
3. 生成前に PowerPoint が対象ファイルを開いていないことを確認する
4. 複数 JSON / manifest を使う生成では、最終 deck に採用した slide set と manifest の件数・ID が一致することを確認する

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

## Tool Selection: python-pptx (create) vs COM (edit)

pptx を扱う 2 系統のツールを、フェーズで明確に使い分ける。混ぜると版番爆発とユーザー手修正の上書きが発生する。

| Phase                                                                                                 | Tool                       | 理由                                                                                              |
| ----------------------------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------- |
| **ゼロから新規作成 / 大量 slide 一括生成**                                                            | python-pptx (build script) | 20-30 slide 一括、レイアウト / SECTIONS / refurl 定型パターンをコード管理できる                   |
| **既存 pptx の微修正 (agenda 直し / textbox 差し替え / 非表示 flag / ノート追記 / セクション再配置)** | PowerPoint COM (pywin32)   | 版番増えない、ユーザー手修正と両立、開いてる状態で編集可、非表示 / セクション / ノートの API 網羅 |

### Rationale

- python-pptx で「既存 pptx を読んで一部書き換えて保存」をするとフォントサイズ・placeholder 継承・run rPr の gotcha が発動して意図しない見た目劣化が起きやすい
- COM は Windows 限定・並列不可・起動 3-5 秒の overhead があるが、微修正では十分速い
- 「build_deck.py で全 slide 再生成 → 手修正が消える」というアンチパターンを防げる

### File Lifecycle (SSOT を守る)

1. **生成段階**: build script の OUTPUT は `..._v01.pptx`〜`..._vNN.pptx` の版番付きで、build のたびに新規保存
2. **顧客提示 or 会議で使った瞬間**: 版番付きファイルを **無版番の canonical name** (例: `..._overview.pptx`) にリネームして SSOT 化
3. **同時に build script の OUTPUT を `..._draft.pptx` サフィックスに変更** して SSOT の上書き衝突を防ぐ
4. **build script + 素材フォルダ (画像等)** は `archive/` 配下に退避。ゼロ作り直しになったときのみ復活
5. **以降の微修正は SSOT を COM で直接編集**。SSOT はディスク上に 1 個だけ、版番増えない

### COM 編集のミニ helper 例

再利用可能な helper module を 1 個持つと、微修正のたびに ad hoc script を書かずに済む。

```python
def open_ssot(pptx_path):
    """既に開いてれば掴む、なければ open (WithWindow=True)"""

def find_textbox_by_content(slide, contains):
    """テキスト部分一致で shape 特定 (idx 番号に依存しない)"""

def replace_textbox_text(shape, new_text, preserve_font=True):
    """フォント維持で本文差し替え"""

def set_slide_hidden(slide, hidden=True):
    """会議で見せなかった slide の非表示化"""
```

Ad hoc の `_update_agenda.py` を毎回書くのはあり (1 回で捨てる想定)。3 回以上パターンが出たら helper module に昇格。

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
- For COM builds that copy a template to a temporary PPTX, use a unique GUID/timestamp filename per run. A fixed working filename can be reopened from stale Office state and append a second body-slide set. Before copying the validated build to its canonical path, count `ppt/slides/slide*.xml` in the ZIP and require the expected count.
- Rendered QA artifacts such as PDF, PNG contact sheets, and temporary scripts are transient. Delete them before handoff unless the user explicitly asks to keep evidence.
- When COM hangs while setting hyperlink `ActionSettings`, keep visible URLs in the deck and apply hyperlinks in a separate small post-processing pass.

## Reusable Slide Master Authoring

When the user asks to create or fix a reusable PowerPoint template, the deliverable is a template surface, not just good-looking sample slides.

### Master-first Rules

1. Put reusable cover, body, and ending design elements on `SlideMaster.CustomLayouts`.
2. Keep editable text as PowerPoint placeholders or text shapes: customer name, system name, title, subtitle, date, speaker, contact, and next step.
3. Set the default Japanese font on the master/layout to `BIZ UDPゴシック` (and set `Name`, `NameAscii`, `NameFarEast`, `NameComplexScript` together when using COM). Do not rely on per-slide font repair loops as the normal path.
4. Put reusable logos, icons, bands, accents, and infographic elements on the layout. Use official or approved assets when available, but keep them reusable at layout level instead of pasting them onto every sample slide.
5. Treat sample slides as previews only. They should contain the minimum editable placeholders or data-bearing objects, not repeated background art.
6. Name custom layouts by purpose, for example `Project Cover`, `Project Content`, `Project Body`, `Project Ending`.
7. If automation needs to identify cover/body/ending slides after master cleanup, detect by `Slide.CustomLayout.Name` first. Use legacy slide-level shape names only as fallback.

### Build Script Rules

- Generate new body slides with `Slides.AddSlide(index, customLayout)` using the intended body layout.
- Do not depend on duplicating a hidden sample slide when the layout itself is the reusable surface.
- If a template keeps sample shapes only as selectable examples (for example region stamp variants), document the exception and delete/replace them during generation.
- After moving design art from slides to layouts, update any scripts that previously detected cover/ending slides by slide-level design shapes.

### Validation Gate

Use COM inspection before handoff:

- `SlideMaster.CustomLayouts` includes selectable cover/content/body/ending layouts.
- Cover and ending sample slides have no direct background art shapes; the art is on their custom layouts.
- Master/layout text placeholders use the intended default fonts, including `BIZ UDPゴシック` for Japanese decks.
- Body slides can be created from the body layout without copying a hidden sample slide.
- A generated deck passes the normal build/enrich/verify path.
- Temporary validation decks, rendered images, and helper scripts are removed after validation.

### Visual Verification Loop (build → PNG → view → fix)

python-pptx で組んだ pptx は、フォント幅による改行位置 / shape 重なり / 余白バランス / Master 装飾との衝突 が実際に開くまで分からない。build 後は必ず PowerPoint COM で PNG エクスポートして目視する。

Loop:

1. `python build_deck.py` で pptx 出力
2. pywin32 経由で `Presentation.Export("<out_dir>", "PNG")` を呼び、各 slide を PNG 化 (会議想定なら 1600x900 以上)
3. AI (view_image tool) または人間で全枚数を目視。判定観点は下記
4. 問題があれば build script を修正し 1 に戻る

**目視判定観点** (毎回全てチェック):

- 本文フォント ≥14pt (会議画面共有想定)
- refurl / footer と本文の間隔 ≥0.15in、重なりゼロ
- 空 textbox は残さない、**ただし Master/Layout 装飾は残す** (common.instructions.md 参照)
- Title 折り返しで 2 行以上にならない
- 色付きバンド内テキストは背景色とコントラスト十分
- Appendix 埋め込み画像は 800px 幅以上で読める

**効率化のコツ**:

- view_image は並列で複数枚同時に見る (1 turn で 3-5 枚)。ただし 20 枚上限に注意
- 「Explore」系サブエージェントに view_image + 監査ファイル書き出しを丸投げすると、audit ファイル書き出しに失敗する事例あり。**メインで view_image する方が確実**
- 「画像が入ってない」と判定する前に、その slide の `shape_type` を数えるスクリプトで確認 (見た目 vs 構造の乖離を防ぐ)
- 修正ループは build_deck.py への最小差分 + 全 slide 再スクショで行う。1 slide だけ差し替えるより早い
- 出力ファイル名は `_v01.pptx` `_v02.pptx` のように版番付けし、export dir も `v01-screenshots/` `v02-screenshots/` にすると diff が取りやすい
- **PowerPoint 開きっぱなしでロック衝突**: user が開いたままにする前提なら、次版は必ずファイル名を bump (v07→v08) して新規保存。同名保存は permission denied で build 失敗しがち
- **解析時のロック回避**: 開かれた pptx を python-pptx で読むと `Permission denied`。`Copy-Item -Force` で `_analyze.pptx` を作って解析し、終わったら削除するのがロックフリー
- **空 placeholder の検出は 1 行スクリプト**で: `[sh for sh in s.shapes if sh.is_placeholder and sh.has_text_frame and not sh.text_frame.text.strip()]` を全 slide で 0 になるまで詰める。view_image より速く確実
- **shape 差分 diff**: v01 と v02 で `[(sh.name, sh.left, sh.top) for sh in s.shapes]` を比較すると、何が消えた/追加されたかが構造レベルで分かる。目視ミスの二重チェックに有効
- **build script / 素材フォルダ は intermediate ではなく infrastructure**。cleanup 時に `_v0N_analyze.pptx` / スクショフォルダ / analyze スクリプトは消してよいが、`build_deck.py` と `appendix-images/` (または同等の素材フォルダ) は再ビルドに必須なので削除対象から除外する。user から「中間生成物を消して」指示が来ても、これらは infrastructure として保護する
- **PowerPoint COM の PNG export は `slide.Export(path, "PNG", W, H)` を優先**。`Presentation.Export(dir, "PNG", W, H)` は環境によって出力ファイル形式が想定と異なる (Slide1.PNG などにならず失敗するケース)。特定 slide だけ抽出するときも、prs.Slides(idx).Export(path, "PNG", 1600, 900) の per-slide 呼び出しの方が安定
- **レンダー鮮度と構造を先に確定**: render directory は各buildで新規作成または空にしてから使う。古いPNGを再利用すると、修正前の見た目で判断してしまう。PNG export前に ZIP内の `ppt/slides/slide*.xml` 数を期待枚数と比較し、重複/欠落を止める
- **builder リストの重複検出**: `builders = [s01, s02, ..., sNN]` のような slide builder 関数の list で、同じ関数が 2 回登場すると slide が重複生成される。build 直前に `assert len(set(builders)) == len(builders)` する。手動編集で関数追加した後に重複しやすい (symptom: 想定より 1 slide 多い、参考リンクが 2 枚並ぶ 等)
- **refurl / footer と本文の衝突を機械的に検出**: RefURL box の top を定数化 (例: `REFURL_TOP = Inches(6.15)`) し、各 slide の add_body_textbox() 呼び出し引数で `top + height <= REFURL_TOP - Inches(0.15)` を assert する。python-pptx は auto shrink しないので、本文が 6.15in を超えると refurl と物理的に重なる。symptom は開いた時に「参考 URL の上に本文が被る / 本文の中に URL が食い込む」
- **PowerPoint COM crash 後の pptx は `viewProps.xml` に `lastView="sldMasterView"` が残る** → 次に開いた時にスライドマスター表示で開く。`viewProps.xml` 全体を既定XMLで置き換えると、既存の notes / grid / namespace 情報を壊し、PowerPoint の修復ダイアログを出すことがある。既存XMLを保持し、`lastView` 属性だけを `sldView` に変更する:

  ```python
  import re

  def force_normal_view(prs):
      for rel in prs.part.rels.values():
          if not rel.reltype.endswith("viewProps"):
              continue
          original = rel.target_part.blob.decode("utf-8")
          updated, count = re.subn(
              r'lastView="[^"]*"', 'lastView="sldView"', original, count=1
          )
          if count == 0:
              updated = re.sub(
                  r'(<p:viewPr\b)', r'\1 lastView="sldView"', original, count=1
              )
          rel.target_part._blob = updated.encode("utf-8")
          return
  ```

  `viewProps` part が無ければ追加せず、そのままにする。更新後は ZIP として読めること、`lastView="sldView"` が残ること、PowerPoint が修復なしで read-only open できることを確認してから handoff する。COM で表示状態を保存しても、テンプレートやクラッシュ由来の view state を確実に直せない場合がある。

## Section Headers (Slide Sorter Groups)

python-pptx は Slide Sorter 用の Section (章) 追加 API を持たない。Section 分けが必要な deck は、build 後に PowerPoint COM 経由で `Presentation.SectionProperties.AddBeforeSlide(idx, name)` を呼ぶ。build script 内で完結させ、build 完了 → COM open → Section 付与 → Save → Close をワンパスで実行する。

Section 定義は `SECTIONS = [(slide_idx, name), ...]` の SSOT 定数にまとめる。スライド構成変更時はここだけ書き換える。

```python
def apply_sections_via_com(pptx_path, sections):
    import win32com.client
    app = win32com.client.Dispatch("PowerPoint.Application")
    prs = None
    for p in app.Presentations:
        if p.FullName.lower() == str(pptx_path).lower():
            prs = p
            break
    if prs is None:
        prs = app.Presentations.Open(str(pptx_path), WithWindow=True)
    sp = prs.SectionProperties
    while sp.Count > 0:
        sp.Delete(1, False)  # False = keep slides
    for idx, name in sections:
        sp.AddBeforeSlide(idx, name)
    try:
        prs.Windows(1).ViewType = 9  # ppViewNormal
        prs.Windows(1).View.GotoSlide(1)
    except Exception:
        pass
    prs.Save()
```

Notes:

- 既に PowerPoint で開かれている pptx なら Presentations コレクションから掴む。掴めれば Save だけで反映され、COM open のオーバーヘッドが不要
- `Delete(index, keepSlides=False)` の 2 番目は必ず False。True にするとスライドごと消える (Gotcha: pywin32 の VARIANT_BOOL では第 2 引数の型ミスで挙動が変わることがある)
- Section 付与後に ViewType を Normal に戻さないと、直後の view state が Slide Sorter で保存されてしまう
- `p.FullName` アクセスで `pywintypes.com_error: (-2147352567, 'この操作を実行するアクセス許可がありません')` / `オートメーションからは実行できません` が返る場合、**他 pptx が保護ビュー / 変更中 / OneDrive 同期中**が原因。Presentations コレクション反復で 1 つでも FullName 取得失敗すると try/except で skip して次に進む。全 slide が section 付与できなかった場合は build 後の次回 build で解消する (idempotent なので毎回上書きで OK)。build script 自体は成功扱いにする (pptx は生成できているので main flow は破綻させない)

## Layout Choice: Section Header vs Title and Content

Custom templates often ship a **Section Header** layout with a large centered decorative title (or watermark-like inherited text) placed over the body area. This layout is designed for chapter divider slides (title only, no body content). If you use it for a slide that also contains body text or reference URL boxes, the layout's centered decoration overlaps every self-added textbox.

Rule:

- **Section Header layout**: 章の区切り slide のみ (タイトルだけで本文なし)
- **Title and Content layout**: 本文 / URL / チャート / 表 が入る全 slide

Symptom: 生成した slide を PowerPoint で開くと、本文のテキストボックスとレイアウトの装飾テキスト (「Section」等の大字) が重なって読めない。fix は該当 slide の layout を Section Header → Title and Content に変えるだけ。

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
