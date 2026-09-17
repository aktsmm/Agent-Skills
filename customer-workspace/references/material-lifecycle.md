# Customer Material Lifecycle

Use these optional folders unless the user specifies another destination. Preserve the same lifecycle boundaries in the chosen folder.

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

- Never edit stored originals in place, including those kept in a user-selected reference folder. Work on a separate copy for redaction or adaptation.
- Use `overall-architecture/` for material relevant across meetings; use `mtg-YYYY-MM-DD-name/` only for meeting-scoped material.
- Store meeting screenshots with stable names and an `attachments.md` manifest.
- When the task includes a customer-provided file, link, or pasted body, preserve every accessible original in the matching `_received/` folder before answering or relying on a summary. Copy local originals without modification and record a content hash when practical.
- Save a pasted body as a text file without changing its wording, symbols, or paragraph structure. Use the meeting-scoped folder when its date is known; otherwise use `_received/incoming/` until it can be classified.
- If a linked source needs authentication or cannot be transferred, make one controlled attempt through an available authenticated route. Do not repeat a persistent failure; record the filename, source system, unreviewed status, and restart condition in `attachments.md`. Do not store credentials, secret-bearing URLs, or absolute local paths in the manifest.
- When files appear at workspace root, inspect all candidate documents, images, diagrams, and archives before classifying them.
- Use a date/topic/version name for the workspace copy and retain the source file. A customer-neutral filename does not remove names in content, images or metadata; record which were actually sanitized. Do not adopt another engagement's configuration, progress or decisions as current facts.
- Check file signatures as well as extensions. A `.pptx` with an OLE signature must be handled as legacy Office content.
- Record transfer, integrity, and content-review states separately in `attachments.md`: retrieved, signature/hash checked, rendered pages reviewed, and original reviewed are not interchangeable. If only rendered page images are available, record their page count and provenance; summarize only those pages, keep the original as not retrieved, and assign no original-file hash.
- Review every PDF page and deck slide before updating summaries from that original.
- If the shared PDF is hard to parse, read the source deck instead. An Office original opens as a ZIP with no extra dependency, and also yields speaker notes and in-meeting memo slides that the PDF flattens away.
- When neither the PDF nor a source original can be read, do not claim a full review. Record the unreviewed status in `attachments.md` and state where the summarized points actually came from (transcript, prior deck, etc.).
- Verify the actual deliverable against its allowed page set; a hidden-slide flag alone does not prove PDF exclusion. For an editable deck, exclude restricted content from slides, notes, media and metadata, not merely the slideshow. Record the delivered file and verification scope in the manifest; NDA labels do not expand the source's sharing permission.
- Use `scripts/Test-ReceivedMaterialPlacement.ps1` for a read-only root audit.
