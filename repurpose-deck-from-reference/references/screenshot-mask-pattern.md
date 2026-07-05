# Screenshot Mask Pattern

実機 UI を `PrintWindow` で取得し、PII を mask して挿入するフロー。

## Capture (PrintWindow)

`SetForegroundWindow` は Win11 で「アクセス拒否」になりがちなので、`PrintWindow` で focus 不要キャプチャ。

```python
import ctypes, win32gui, win32ui
from PIL import Image

def shoot(hwnd, out):
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    w, h = r - l, b - t
    hDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hDC)
    saveDC = mfcDC.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(bmp)
    ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0x2)  # PW_RENDERFULLCONTENT
    info = bmp.GetInfo()
    bits = bmp.GetBitmapBits(True)
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bits, "raw", "BGRX", 0, 1)
    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC(); mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hDC)
    img.save(out)
```

## Click + Capture (auto-navigation)

```python
def click(rel_x, rel_y):
    abs_x = WIN_L + rel_x
    abs_y = WIN_T + rel_y
    ctypes.windll.user32.SetForegroundWindow(HWND)
    ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(1.5)
```

sidebar 座標を事前に観察して定数化。pop-up 系（Search 等）は click 効かない場合あり、keyboard shortcut で代用。

## Mask (PII removal)

3 層構造で safe に隠す:

1. **Cover rect**（黒塗り）— 確実に元情報を消す
2. **Gaussian blur**（ぼかし）— 元の色味は残しつつ判読不可に
3. **Overlay label**（白文字説明）— 何が masked かを観客に伝える

```python
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def cover(draw, x1, y1, x2, y2, fill=(0x21, 0x26, 0x2D)):
    draw.rectangle([x1, y1, x2, y2], fill=fill)

def blur_region(img, x1, y1, x2, y2, r=10):
    region = img.crop((x1, y1, x2, y2)).filter(ImageFilter.GaussianBlur(r))
    img.paste(region, (x1, y1))

def label(draw, x, y, text, fill=(0xC9, 0xD1, 0xD9), size=12, bold=False):
    # IMPORTANT: use a Japanese-capable font (Segoe UI does NOT render Japanese)
    font = ImageFont.truetype("YuGothB.ttc" if bold else "YuGothR.ttc", size)
    draw.text((x, y), text, fill=fill, font=font)
```

### What to mask (always)

- Personal project / repository name (`aktsmm/<repo>`)
- Issue titles, issue numbers, PR titles
- Conversation body (free-text content)
- Sidebar session names (chat history shows topics)
- Username and avatar (bottom-left)
- Right panel issue detail (most sensitive)

### What is safe to keep visible

- Sidebar structure (Home / My work / Automations / Search / Sessions)
- Composer UI controls (Mode dropdown, Model dropdown, Reasoning effort)
- Official template names (Issue triage / Changelog draft etc.)
- Built-in skill names (docx / excalidraw / expense-report)
- Action buttons (Run / Open / Ready to merge / Fix / Review)

## Insert into PPTX

drop shadow + picture + caption をひとセットで:

```python
def add_screenshot(slide, png, left, top, w, h, caption):
    shadow = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Emu(left + 30000), Emu(top + 30000),
                                    Emu(w), Emu(h))
    shadow.fill.solid(); shadow.fill.fore_color.rgb = RGBColor(0xD0, 0xD7, 0xDE)
    shadow.line.fill.background()
    slide.shapes.add_picture(png, Emu(left), Emu(top), Emu(w), Emu(h))
    # caption above screenshot
    add_text(slide, left, top - 220000, w, 180000, caption, size=9, color=GREY)
```

幅は元画像のアスペクト比を保つ: `shot_h = int(shot_w * src_h / src_w)`.

## Done Criteria

- 全 mask 領域で個人情報（名前・リポ・issue タイトル・本文）が完全に判読不可
- 観客が「何がマスクされているか」を 1 行ラベルで理解できる
- 構造（UI panes / buttons / dropdowns）は十分に見える
- Caption に「個人情報マスク」と明記
