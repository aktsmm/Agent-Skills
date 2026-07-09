# Customer Material Lifecycle

Use these optional folders when customer-shared diagrams, decks, tables, or schedules accumulate.

```text
_received/                       <- customer originals only
  overall-architecture/
  mtg-YYYY-MM-DD-name/
_working/                        <- internal edited, annotated, or draft copies
  overall-architecture/
  mtg-YYYY-MM-DD-name/
_provided/                       <- customer-safe send-out or projection copies
  overall-architecture/
  mtg-YYYY-MM-DD-name/
```

- Never edit files in `_received/` in place.
- Use `overall-architecture/` for material relevant across meetings; use `mtg-YYYY-MM-DD-name/` only for meeting-scoped material.
- Store meeting screenshots with stable names and an `attachments.md` manifest.
- When files appear at workspace root, inspect all candidate documents, images, diagrams, and archives before classifying them.
- Rename received originals with a stable date prefix; leave only unclassified items in `_received/incoming/`.
- Check file signatures as well as extensions. A `.pptx` with an OLE signature must be handled as legacy Office content.
- Review every PDF page and deck slide before updating summaries.
- Use `scripts/Test-ReceivedMaterialPlacement.ps1` for a read-only root audit.
