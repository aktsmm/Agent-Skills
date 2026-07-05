# COM and XML Pitfalls

`repurpose-deck-from-reference` フローで踏みやすい既知の罠と回避策。

## 1. Negative dimension corruption

### 症状

`python-pptx` で `add_textbox(..., width=Emu(w), height=Emu(h))` に負の値が渡ると、保存は通るが PowerPoint COM `Presentations.Open` が失敗する（"ファイルを開けません。"）。GUI からはなぜか開ける。

### 原因

`add_card` 等のヘルパーで `body_h = h - 650000` のような計算をしていて、`h < 650000` のとき body_h が負数になる。

### 回避

```python
add_text(slide, left + 150000, top + 130000, w - 300000,
         max(200000, min(350000, h - 200000)), title, ...)
body_top = top + min(540000, h // 2)
body_h = max(150000, top + h - body_top - 100000)
add_text(slide, left + 150000, body_top, w - 300000, body_h, body, ...)
```

すべての width / height で `max(min_positive, ...)` クランプを入れる。

### 発見手順

スライド単位の bisection でしか発見できないことが多い。`partial_build.py STOP_AT_SLIDE_N` で N まで作って `com_test_copy.py` で確認、を繰り返す。

```python
import sys, re
src = open("rebuild_deck.py", encoding="utf-8").read()
marker = f"    # ============= SLIDE {int(sys.argv[1])}:"
idx = src.find(marker)
inject = '    pres.save(PATH); print("saved partial"); return\n'
exec(src[:idx] + inject + src[idx:], {"__name__": "__main__"})
```

## 2. COM Export cache

### 症状

`rebuild_deck.py` で内容を更新して save した直後、`Presentations.Open(SAME_PATH)` → `Slides.Item(N).Export(...)` で出てくる PNG が古い内容のまま。`python-pptx` で読むと最新内容が見えるのに COM だけ古い。

### 原因

PowerPoint / OneDrive / Office cache が同じパスに対する以前の content snapshot を保持している。

### 回避

```python
import shutil, pythoncom, win32com.client
src = r"<original>.pptx"
dst = r"<original-dir>\__exp.pptx"  # 新しい名前
shutil.copy(src, dst)
pythoncom.CoInitialize()
app = win32com.client.DispatchEx("PowerPoint.Application")
pres = app.Presentations.Open(dst, WithWindow=False)
# ... export ...
pres.Close(); app.Quit()
os.unlink(dst)
```

毎回 GUID 付き / `__exp.pptx` 等で別名コピー。

## 3. OneDrive lock + FileCoAuth

### 症状

`python-pptx` の `Presentation(path)` で `PackageNotFoundError: Package not found at '...'` が起きる。pptx は disk 上にあるのに。

### 原因

OneDrive の `FileCoAuth.exe` が同期中にファイルをロックしている。

### 回避

```powershell
Get-Process POWERPNT, FileCoAuth -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.Id -Force }
Start-Sleep 5
```

それでも駄目なら OneDrive 同期一時停止。

## 4. XML escape in section names

### 症状

`p14:sectionLst` を `presentation.xml` に直接挿入したあと、PowerPoint COM Open が失敗。`python-pptx` では開ける。

### 原因

section 名に `&` を含むと XML 不正。例: `D. Customize & Collaborate`。

### 回避

```python
("D. Customize &amp; Collaborate", [11, 12]),  # &amp; にエスケープ
```

XML を組み立てる前に名前を escape する。

## 5. Hidden slide page numbering

### 症状

INTERNAL 用 hidden slide があるとき、ページ番号を「visible only」でカウントすると、hidden を挟んだ後の slide の表示番号がプレゼン時の見た目とズレる。

### 回避

ページ番号は **hidden を含めた絶対インデックス** で振る。プレゼン時に hidden は飛ばされるが、それは PowerPoint 側の責務。

```python
for idx, slide in enumerate(slides, start=1):
    if idx == 1:  # title - no page num
        continue
    set_page_number(slide, idx)
```

## 6. Layout-inherited background

### 症状

スライドの layout を「白紙」に変えたのに、レンダリングすると古いテンプレの背景色（青や写真）が残る。

### 原因

slide 自体に `<p:bg>` が独自に設定されており、layout 変更だけでは消えない。

### 回避

```python
import zipfile, shutil, re
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if (item.filename.startswith("ppt/slides/slide") and
            item.filename.endswith(".xml") and item.filename not in skip_files):
            data = re.sub(r"<p:bg>.*?</p:bg>", "", data.decode(), flags=re.S).encode()
        zout.writestr(item, data)
```
