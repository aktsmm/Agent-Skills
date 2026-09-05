---
name: ocr-super-surya
description: "GPU-optimized OCR using Surya. Use when extracting text from images/screenshots, recovering image-only content in PDFs or slides, or inspecting multilingual document layouts. Preserve source locations and report recognition gaps separately from verified text."
argument-hint: "OCR したい画像・PDF、対象言語、欲しい出力"
user-invocable: true
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

## Extraction and Verification

1. Confirm the input scope and a non-public output location for sensitive material; preserve source files and do not bypass document protection. Text redaction does not anonymize retained images or authorize redistribution.
2. Extract native PDF/slide text first, including slide notes where present. A nonempty text layer can still omit screenshots, diagrams, or image-only pages; inventory those gaps before selecting OCR targets.
3. Record source-relative path, source hash, page/slide number, and image hash. Deduplicate identical images without dropping their source locations; distinguish pending, recognized, no-text, and failed outcomes.
4. Run a small sample and compare it with the original image before scaling. Reuse predictors within a batch and checkpoint each completed item so interruption does not require starting over.
5. Keep raw OCR separate from corrected notes. Flag low or missing confidence and inspect multi-column order, code symbols, and tables; high confidence is not proof of correctness, and no-text is not proof of an empty image.
6. Report extracted documents, processed OCR targets, unrecognized targets, and manually reviewed scope separately. Verify saved files and hashes; a saved hash alone proves neither source freshness nor semantic accuracy. Recheck the source hash when claiming the same source version.

## Quick Start

### Installation

Check the selected interpreter and existing dedicated environments before installing or declaring a PDF/OCR dependency unavailable. Set `OcrPython` to the resolved environment's interpreter; do not assume the active workspace environment has the same packages.

```powershell
& $OcrPython -c "import importlib.util,json; print(json.dumps({name: importlib.util.find_spec(name) is not None for name in ['surya','torch','pypdf','pypdfium2']}))"
```

After imports succeed, check package versions and `torch.cuda.is_available()` with that same interpreter. GPU unavailability alone is not a reason to uninstall a working environment. If dependencies are missing, use an isolated environment; stop repeated equivalent TLS failures instead of disabling certificate validation.

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
>
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

| エラー                                                                                           | 原因                                | 対処                                                                              |
| ------------------------------------------------------------------------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------- |
| `RecognitionPredictor.__init__() missing 1 required positional argument: 'foundation_predictor'` | v0.13+ でAPIが変更                  | `found_pred = FoundationPredictor()` を作成して引数に渡す                         |
| `TypeError: __call__() got an unexpected keyword argument 'langs'`                               | v0.17.x で `langs` 引数廃止         | `langs` 引数を削除する                                                            |
| `AttributeError: 'SuryaDecoderConfig' object has no attribute 'pad_token_id'`                    | `transformers 5.x` との非互換       | `pip install "transformers<5.0"` でダウングレード                                 |
| `failed to hardlink file ... OneDrive` (uv, os error 396)                                        | OneDrive のハードリンク制限         | `--link-mode=copy` を付けてインストール＋`UV_CACHE_DIR` をOneDrive外に設定        |
| `UnicodeEncodeError: 'cp932' codec can't encode character`                                       | Windows のCP932デフォルトエンコード | `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` を先頭に追加 |
| `PdfDocument` does not support the context manager protocol | Installed pypdfium2 API differs | Use explicit `try/finally` cleanup and close bitmap, page, and document after copying the rendered image; verify against the installed version. |

## License Note

- **Surya**: GPL-3.0 (code), commercial license required for >$2M revenue
