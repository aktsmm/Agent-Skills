# Advanced Azure Screenshot Masking

## Script Usage

The bundled `scripts/mosaic-azure-screenshots.py` uses Pillow to apply pixel mosaics.

| Argument                                | Purpose                                    |
| --------------------------------------- | ------------------------------------------ |
| `path`                                  | PNG file or directory                      |
| `--region L,T,R,B`                      | Additional region; repeatable              |
| `--topright-width`, `--topright-height` | Adjust the default tenant strip            |
| `--no-topright`                         | Disable the default top-right strip        |
| `--block`                               | Mosaic block size                          |
| `--backup`                              | Preserve `<name>.bak.png` before overwrite |

Install dependency with `pip install pillow` in the selected Python environment.

## OCR Fallback

When static coordinates miss text in a table or details pane, use OCR to obtain `text` and `bbox [x1, y1, x2, y2]`, select rows containing confirmed sensitive values, and mosaic the matching boxes with Pillow. Never place real tenant, subscription, customer, or resource identifiers in reusable examples.

```python
for line in page.text_lines:
    text = line.text.strip().lower()
    if any(pattern in text for pattern in mask_patterns):
        x1, y1, x2, y2 = [int(value) for value in line.bbox]
        region = image.crop((x1, y1, x2, y2))
        small = region.resize((max(1, (x2 - x1) // 8), max(1, (y2 - y1) // 8)), Image.NEAREST)
        image.paste(small.resize((x2 - x1, y2 - y1), Image.NEAREST), (x1, y1))
```

## OCR-Guided Highlight

For a public before/after explanation, use the confirmed OCR box with `ImageDraw.rectangle` to highlight rather than hide text. Limit highlights to two or three per image and connect them to the article text.

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(image)
draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
```

## Practical Tips

- Keep viewport dimensions stable before reusing regions.
- Determine coordinates on one representative image, then visually verify every image.
- Use a normal image annotation tool when only one or two images need a solid cover; the script is most useful for repeatable batches.
- Investigate IP ownership before deciding whether an IP address is safe to publish.
