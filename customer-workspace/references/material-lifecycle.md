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
- When the task includes a direct attachment path or link, attempt to import every accessible original into the matching `_received/` folder before relying only on a summary. Copy local originals without modification and record a content hash when practical.
- If a linked source needs authentication or cannot be transferred, make one controlled attempt through an available authenticated route. Do not repeat a persistent failure; record the filename, source system, unreviewed status, and restart condition in `attachments.md`. Do not store credentials, secret-bearing URLs, or absolute local paths in the manifest.
- When files appear at workspace root, inspect all candidate documents, images, diagrams, and archives before classifying them.
- Rename received originals with a stable date prefix; leave only unclassified items in `_received/incoming/`.
- Check file signatures as well as extensions. A `.pptx` with an OLE signature must be handled as legacy Office content.
- Review every PDF page and deck slide before updating summaries.
- If the shared PDF is hard to parse, read the source deck instead. An Office original opens as a ZIP with no extra dependency, and also yields speaker notes and in-meeting memo slides that the PDF flattens away.
- When neither the PDF nor a source original can be read, do not claim a full review. Record the unreviewed status in `attachments.md` and state where the summarized points actually came from (transcript, prior deck, etc.).
- To confirm what the customer actually received, check that `shared PDF pages = source slides - hidden slides`, then verify every internal-only marker sits on a hidden slide. Record the result in `attachments.md`.
- Use `scripts/Test-ReceivedMaterialPlacement.ps1` for a read-only root audit.
