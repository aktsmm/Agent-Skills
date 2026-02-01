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
from PIL import Image
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.foundation import FoundationPredictor

image = Image.open("document.png")
foundation_predictor = FoundationPredictor()
recognition_predictor = RecognitionPredictor(foundation_predictor)
detection_predictor = DetectionPredictor()

predictions = recognition_predictor([image], det_predictor=detection_predictor)
for page in predictions:
    for line in page.text_lines:
        print(line.text)
```

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

## Done Criteria

- [ ] CUDA available (if GPU present)
- [ ] Text extracted from target image
- [ ] Output saved to specified file

## License

- **This skill**: CC BY-NC 4.0
- **Surya**: GPL-3.0 (code), commercial license for >$2M revenue
