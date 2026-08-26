# Asset embedding

Everything an artifact displays lives inside the file. There is no second request at open time.

## Routes in

| Source                      | How                                                                               |
| --------------------------- | --------------------------------------------------------------------------------- |
| Local file                  | `embed_assets.py path/to.png`                                                     |
| Remote URL                  | `embed_assets.py https://... --allow-network` — fetched at build time and inlined |
| Diagram or chart drawn here | inline SVG, subset in `artifact-grammar.md` section 3                             |
| SVG from another tool       | import it, then confirm it is inside the subset                                   |

A remote URL is never left as an `<img src>`. The constraint forbids it, so the only way a URL can work is by being downloaded and inlined. A failed fetch stops the build; it is not skipped, because an artifact missing one image still looks finished.

## The shape

```html
<img src="data:image/png;base64,..." alt="構成図" data-asset-ref="a1" />
```

```json
{
  "schemaVersion": 1,
  "assets": [
    {
      "id": "a1",
      "mime": "image/png",
      "alt": "構成図",
      "w": 1200,
      "h": 630,
      "sha256": "..."
    }
  ]
}
```

The payload sits once, in the `img`. The model entry is a record of it, and the verifier checks the two agree on mime, hash and alt text — an id that matches while the bytes do not is exactly the drift worth catching.

Every `img` needs `data-asset-ref`. An image outside the model is rejected, which is what stops an unvetted one from slipping in.

## Metadata

Stripping is standard library, so it works anywhere. Rebuilds happen against an **allowlist** of chunks, not a list of bad ones — that is what closes gaps like JPEG APP13/IPTC or PNG `tIME` that a denylist keeps missing.

| Format | Kept                                                                  |
| ------ | --------------------------------------------------------------------- |
| PNG    | `IHDR` `PLTE` `IDAT` `IEND` `tRNS` `gAMA` `cHRM` `sRGB` `bKGD` `pHYs` |
| JPEG   | SOI, SOF0/1/2, DHT, DQT, SOS, DRI, EOI, APP0 when it is JFIF          |

EXIF orientation is applied to the pixels before the segment is dropped, so a phone photo does not end up sideways.

WebP is not handled by the standard library path. Convert it to PNG or JPEG first.

## Screenshots

A text scan cannot read a tenant name rendered inside a PNG. Nothing in this skill can. So:

1. Look at the image.
2. Mask what should not ship — `mask_image.py --rect x,y,w,h`. Solid fill is the default; a blur can leave short strings legible.
3. Only then run `embed_assets.py --sanitized`.

`--sanitized` is an assertion you are making, not a check the tool performed. If the image changes, make it again.

## Size

Base64 adds about 33%. Defaults in `budget.json`:

| Scope      | Warn   | Fail  |
| ---------- | ------ | ----- |
| One image  | 400 KB | 2 MB  |
| Whole file | 3 MB   | 12 MB |

Over the limit the build stops and asks. It does not silently recompress, because quietly degrading someone's screenshot is worse than telling them.

To shrink: `--max-width 1600` (needs Pillow), crop to the part that matters, or move the image out of the artifact entirely.

## Resolution

A poster exported at `--scale 2` renders the canvas at twice its pixel size. An image displayed 600px wide therefore wants 1200 real pixels. `embed_assets.py` reports the true dimensions so this is arithmetic rather than guesswork.

## What is not embedded

Original paths and fetch URLs stay out of the distributed file. Keep them in your own notes alongside the asset id if you need to re-fetch later. Signed URLs and query tokens must never be written anywhere.

If an image is third-party, put the visible credit and licence in the artifact where a reader can see it — not in a comment.
