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

## Coarseness Check and Rebuild

Block mosaics can hide more than the sensitive value. Before redoing a whole set, measure how much of each image body (below the header strip) differs from the raw capture, then redo only the outliers.

```python
diff = ImageChops.difference(raw, masked).convert("L").point(lambda v: 255 if v > 8 else 0)
body = diff.crop((0, 45, raw.width, raw.height))
changed_pct = sum(1 for v in body.getdata() if v) / (body.width * body.height) * 100
```

In one 429-image set only about 2% of the images changed more than 1% of the body, and most masking was the account strip; a full rebuild was not justified.

If a value-only rebuild is still wanted, there are two output styles. A dummy such as `user@contoso.com` or an all-zero GUID drawn over the value (sampled background colour) is one. The other, when a requester asks for readable answers, is a light-gray fill over only the value with a short label (for example the kind of value hidden); see [Labeled Gray Fill](#labeled-gray-fill-requester-style). Keep these rules:

- Match patterns against each OCR **line text with word boundaries joined**, not word by word: OCR splits one name into several words, and a per-word regex misses it. Run OCR at 1x/2x/3x and union the hits; the passes are slow for hundreds of images.
- Do not reveal text that was previously masked unless OCR read it cleanly and the remainder contains no hex runs, `@`, IPs or long mixed digit-letter names. A partial or garbled read is not evidence that it is safe.
- Never overwrite the reviewed delivery set with the rebuild until every output has been re-OCRed and visually reviewed. Keep the rebuild in a separate folder and report any pattern gap found (for example a name that stayed readable) as a stop.

## Labeled Gray Fill (requester style)

Use when a requester wants answers readable and only identifiers hidden. Confirm first what to hide and what to keep (typically subscription ID, tenant ID, signed-in account, public IP hidden; lab dummy names kept).

- Fill only the value with light gray and write a short label on it (for example the value kind). In an ARM ID replace only the subscription GUID and leave the rest visible, including a GUID that wraps onto a second line.
- Save beside the original with a suffix such as `_v2`; never overwrite the original or the reviewed delivery set.
- Run OCR in both Japanese and English (`en-US`) at 1x/2x/3x. Japanese OCR breaks GUIDs and splits names into words; English reads GUIDs better. Snap GUID boxes to the neighbouring `/` words and refine edges with template matching of the same text rows. Join words per line before regex matching.
- After rendering, zoom and check each filled box for leftover characters or clipped neighbours (a missing first character of `/resourceGroups` is common); patch by hand, then re-verify.
- Visual review is mandatory: give each reviewer 10–15 images at most, repeat until a round finds nothing, and report residual minor defects instead of calling the set perfect. The viewer may show a stale image for a rewritten file, so copy to a fresh name before viewing.
- Ask before hiding items the requester did not list (for example a personal alias inside a subscription name) and say so in the report.

## OCR-Guided Highlight

For a public before/after explanation, use the confirmed OCR box with `ImageDraw.rectangle` to highlight rather than hide text. Limit highlights to two or three per image and connect them to the article text.

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(image)
draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
```

## Practical Tips

- Script is most useful for repeatable batches; for one or two images a normal annotation tool is enough.
- Investigate IP ownership before deciding whether an IP address is safe to publish.
