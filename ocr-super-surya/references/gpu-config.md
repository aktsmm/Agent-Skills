# GPU Configuration

## Environment Variables

| Variable                 | Default | Description           |
| ------------------------ | ------- | --------------------- |
| `RECOGNITION_BATCH_SIZE` | 512     | Reduce for lower VRAM |
| `DETECTOR_BATCH_SIZE`    | 36      | Reduce if OOM         |

## Example Configuration

```bash
export RECOGNITION_BATCH_SIZE=256
export DETECTOR_BATCH_SIZE=18
surya_ocr image.png
```

## Troubleshooting

| Issue               | Solution                    |
| ------------------- | --------------------------- |
| CUDA=False with GPU | Reinstall PyTorch with CUDA |
| OOM Error           | Reduce batch sizes          |
| CPU Fallback        | Auto-detected (slower)      |

## CUDA Reinstall

```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
