---
name: ocr-super-surya
description: "GPU-optimized OCR using Surya. Use when: (1) Extracting text from images/screenshots, (2) Processing PDFs with embedded images, (3) Multi-language document OCR, (4) Layout analysis and table detection. Supports 90+ languages with 2x accuracy over Tesseract."
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# OCR Super Surya

GPU-optimized OCR using [Surya](https://github.com/datalab-to/surya).

## When to Use

- **OCR**, **extract text from image**, **text recognition**, **画像から文字**
- Extracting text from screenshots, photos, or scanned images
- Processing PDFs with embedded images
- Multi-language document OCR (90+ languages including Japanese)

## Features

| Feature       | Description                             |
| ------------- | --------------------------------------- |
| **Accuracy**  | 2x better than Tesseract (0.97 vs 0.88) |
| **GPU**       | PyTorch-based, CUDA optimized           |
| **Languages** | 90+ including CJK                       |
| **Layout**    | Document layout, table recognition      |

## Quick Start

### Installation

```bash
# 1. Check GPU
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# 2. Install (with CUDA if GPU available)
pip install surya-ocr

# If CUDA=False but you have GPU, reinstall PyTorch:
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Windows + uv 環境（OneDrive配下でのインストール）

OneDrive 配下のフォルダでは uv のハードリンクが失敗するため、以下の手順を使う：

```powershell
# キャッシュをOneDrive外に設定
$env:UV_CACHE_DIR = "C:\Temp\uv_cache"

# 仮想環境をOneDrive外に作成
uv venv C:\Users\<USERNAME>\ocr_env --python 3.12

# surya-ocrをインストール（link-mode=copy でハードリンクを回避）
uv pip install surya-ocr --python C:\Users\<USERNAME>\ocr_env\Scripts\python.exe --link-mode=copy

# transformers 5.x は非互換 → 4.x を強制
uv pip install "transformers<5.0" --python C:\Users\<USERNAME>\ocr_env\Scripts\python.exe --link-mode=copy
```

### Usage

```bash
# CLI
python scripts/ocr_helper.py image.png
python scripts/ocr_helper.py document.pdf -l ja en -o result.txt

# Or use surya directly
surya_ocr image.png --output_dir ./results
```

### Python API

```python
import sys, io
# Windows CP932エンコードエラー対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.foundation import FoundationPredictor

image = Image.open("document.png").convert("RGB")
found_pred = FoundationPredictor()
rec_pred = RecognitionPredictor(found_pred)  # v0.13+ : FoundationPredictor必須
det_pred = DetectionPredictor()

# v0.17.x以降: langs引数は廃止 → 渡さないこと
for page in rec_pred([image], det_predictor=det_pred):
    for line in page.text_lines:
        if line.text.strip():
            print(line.text)
```

> **API変更履歴 (v0.17.x)**:
> - `RecognitionPredictor(foundation_predictor)` - `FoundationPredictor` が必須引数に変更
> - `__call__()` から `langs` 引数が削除（自動検出に変更）

## GPU Configuration

| Variable                 | Default | Description           |
| ------------------------ | ------- | --------------------- |
| `RECOGNITION_BATCH_SIZE` | 512     | Reduce for lower VRAM |
| `DETECTOR_BATCH_SIZE`    | 36      | Reduce if OOM         |

```bash
export RECOGNITION_BATCH_SIZE=256
surya_ocr image.png
```

## Scripts

| Script                  | Description                               |
| ----------------------- | ----------------------------------------- |
| `scripts/ocr_helper.py` | Helper with OOM auto-retry, batch support |

## Troubleshooting

| エラー | 原因 | 対処 |
| ------ | ---- | ---- |
| `RecognitionPredictor.__init__() missing 1 required positional argument: 'foundation_predictor'` | v0.13+ でAPIが変更 | `found_pred = FoundationPredictor()` を作成して引数に渡す |
| `TypeError: __call__() got an unexpected keyword argument 'langs'` | v0.17.x で `langs` 引数廃止 | `langs` 引数を削除する |
| `AttributeError: 'SuryaDecoderConfig' object has no attribute 'pad_token_id'` | `transformers 5.x` との非互換 | `pip install "transformers<5.0"` でダウングレード |
| `failed to hardlink file ... OneDrive` (uv, os error 396) | OneDrive のハードリンク制限 | `--link-mode=copy` を付けてインストール＋`UV_CACHE_DIR` をOneDrive外に設定 |
| `UnicodeEncodeError: 'cp932' codec can't encode character` | Windows のCP932デフォルトエンコード | `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` を先頭に追加 |

## License Note

- **Surya**: GPL-3.0 (code), commercial license required for >$2M revenue
