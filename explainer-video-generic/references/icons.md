# Logos and icons

Diagrams read better with the real logo or icon of the product/company than with a generic glyph. Use them to **identify** the subject, never to imply endorsement.

## Order of preference

1. **The user's own set** (brand kit, icon library, a `.pptx` of icons, a folder or zip of SVG/PNG).
   ```bash
   python "$S/scripts/icons.py" import  --src ./my-icons-or.zip --out "$W/icons"
   python "$S/scripts/icons.py" extract --pptx IconSet.pptx --out "$W/icons" --find Monitor,Alerts   # pptx icon sets
   ```
   Ask where the user keeps one, or search the project/downloads for `icons`, `brand`, `logo`.
2. **Official vendor assets**: the company's brand/press/media kit or its official icon set (for example the Azure architecture icons for Microsoft services, or the "brand assets" page of a company). Download with `fetch --url NAME=URL --license "<what the page says>"`.
3. **Simple Icons** (single-color brand glyphs, CC0 artwork; the trademarks still belong to their owners):
   ```bash
   python "$S/scripts/icons.py" fetch --out "$W/icons" --search nvidia                 # find the slug
   python "$S/scripts/icons.py" fetch --out "$W/icons" --simple nvidia,openai --color brand
   ```
   `--color brand` tints with the brand color from the Simple Icons data; a hex like `76B900` also works.
4. **Product-specific icons** not in any set: the icon the product's own page declares (`python "$S/scripts/icons.py" fetch --out "$W/icons" --page NAME=https://product.example.com/` reads its `<link rel="icon">`, SVG first), or the official GitHub organization's assets.
5. **Nothing found**: use the template's line icons `icon()` and say so in the report. Do not draw look-alike logos, and do not stand in a generic robot/agent glyph for a named product while a better source is untried.

Every fetched icon is recorded in `$W/icons/ATTRIBUTION.json` (name, file, source URL, license note, date). Keep it with the deliverables.

## Using them

```bash
python "$S/scripts/icons.py" sheet --dir "$W/icons" --out "$W/iconsheet.png"          # open and CHECK each icon
python "$S/scripts/icons.py" embed --html "$W/{slug}.html" --map nvidia="$W/icons/nvidia.svg" openai="$W/icons/openai.svg"
```

- `embed` stores data URIs in `VIDEO.images` (repeat calls merge). The HTML stays a single portable file and browser export keeps the images. SVGs that only have a `viewBox` get explicit width/height so the aspect ratio is preserved.
- Draw with `oi(ctx, 'nvidia', centerX, centerY, size)` or `img(ctx, 'nvidia', x, y, w, h)`.
- Single-color logos look best on a white/light rounded panel (`rbox`) with the product name written next to them.

## Rules

- **View the contact sheet before use.** Make sure no icon carries the wrong name, and do not stand in a parent or related product's icon for the labeled product.
- **Check that an SVG draws anything.** A file of a few KB can be an empty placeholder (valid XML, no path/circle/rect); `fetch` warns and `embed` refuses SVGs with no drawable shapes. Icon indexes and mirrors of portal assets are prone to this: render before trusting one.
- **Do not redraw, imitate, recolor (except the single-color brand tint), crop, flip or rotate** official marks; keep the aspect ratio. Follow the owner's brand guidelines (clear space, minimum size).
- **Do not call an icon "official" unless it came from the owner's own assets.** Report where each came from.
- Show the product name in text near the logo.
- For public distribution, confirm the owner's trademark/brand policy (many allow factual, nominative use in news and education; promotional or implied-endorsement use needs permission). When in doubt, use the name as text only and tell the user.
- Microsoft service icons: the Azure architecture icon terms allow use in architecture diagrams, training and documentation; get the sets from Microsoft Learn's "Azure architecture icons" page.
