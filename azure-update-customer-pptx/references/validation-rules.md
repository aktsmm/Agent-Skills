# Validation Rules

`scripts/Verify-Pptx.ps1` is the validation SSOT. Keep this document aligned with the script.

Current script gate checks:

1. P2 summary is numbered.
2. UPDATE Points table has valid region column values.
3. Weekly topic slides have region stamps.
4. Slides have speaker notes.
5. Section order is valid.
6. Weekly slide order follows label priority.
7. UPDATE Points appears after Weekly Topics.
8. UPDATE Points key points are not generic fallback text.
9. Notes match slide titles/content.
10. No unresolved template placeholders remain anywhere on slides, including hidden cover variants (`{{...}}`).
11. No duplicate honorifics appear anywhere on slides: `御中 御中`, `様 様`, or mixed suffix duplication caused by config/template overlap.
12. No customer-specific terms appear on visible slides outside cover/metadata: customer name, system name, tenant domain, subscription IDs, or GUID-like environment identifiers from `.config/customer-profile.md`.
13. Visible Weekly slides distinguish `Microsoft Learn` detail links from `Azure Updates` announcement links, and the labels hyperlink to `learnUrl` / `sourceUrl` respectively.
14. Ending variants are valid: exactly one visible formal Ending, matching cover/ending visual variant, non-selected variants hidden, no empty `Ending-Title`/`Ending-Subtitle`, and no generic scaffold text.
15. Appendix slides are hidden and the hidden Appendix slide count matches `classification.json` Appendix count.
16. Region review evidence is present when required: `region_info_reviewed.json` with `verified`, `source`, and `evidence` fields. In draft mode, missing reviewed evidence is a warning; in delivery mode, it is a failure.

Quality review checks that must also pass before final done:

17. P2 summary has clean formatting: numbered list is readable, bullet glyphs are not duplicated, and template bullet formatting does not add extra `■` marks.
18. Classification matches customer relevance: Weekly is for customer-relevant or explicitly requested items; Appendix is allowed for low-relevance items and must be hidden.
19. Speaker notes are customer-grounded and include full source trails for Microsoft Learn and Azure Updates.
20. Weekly items have Azure Updates `sourceUrl` and, where a first-party page exists, Microsoft Learn `learnUrl`.
21. For nontrivial or customer-delivery decks, a rubber-duck style read-only critic review has checked the deck path, manifests, Verify result, placeholders, bullets, reference affordance, customer grounding, visible-slide neutrality, formal Ending, Appendix visibility, and region review evidence.
22. Visible Weekly Topics use one approved customer body layout. If source imports preserve different masters, rebuild the Weekly slice from a named body prototype before delivery.
23. Visible references never point readers to speaker notes. Each Weekly Topic has a dedicated hyperlink shape whose label distinguishes Microsoft Learn detail from Azure Updates announcement; inspect the saved PPTX to prove the shape-level URL persisted.
24. Every visible Weekly region entry has `verified: true`, a first-party `source`, and concrete `evidence`. A fail-safe 日本リージョン未対応 result records the sources checked and why no explicit Japan availability was found.
25. When PDF is a delivery artifact, export it after the final PPTX mutation and verify its page count equals the final slide count.
26. When the delivery requirement is an unprotected PDF, export with `Export-PptxToPdf.ps1 -RequireUnencrypted`; it must not detect a PDF `/Encrypt` reference. If encryption is expected, record that the protection is intentional before delivery.
27. Validate the **saved PPTX**, not only `notes.json`: each topic note must include a presenter-ready summary, customer impact, recommended action, Azure Updates source, Microsoft Learn source where available, and region evidence for visible Weekly topics. Every visible slide has purpose or transition notes.
28. Export customer PDFs from a unique local copy. Before and after export, verify the canonical PPTX remains an OpenXML ZIP and has the same SHA-256 hash; do not reuse an open canonical presentation for PDF export.
29. Section membership is valid, not only section order. Gate check 5 passes even when a section is empty, so inspect the saved PPTX and confirm every declared section owns the expected slide range and no section holds zero slides. An empty Weekly section absorbed by the preceding summary section is the usual symptom after a Weekly rebuild.
30. Visible Weekly slide count matches the `classification.json` Weekly item count. A mismatch that is an exact duplication of the Weekly slice indicates a cloud-sync conflict merge, not a manifest error.
31. Visible Weekly body has `targetService`, `updateSummary`, `userValue`, and `displayImpact`; `updateSummary` is not a normalized title repeat, and `displayImpact` has no internal `【…】` token. The body fill ratio is 0.55-0.92.
32. Visible body and speaker notes do not repeat two or more substantive lines. Notes retain technical context, Q&A, and complete Learn / Azure Updates / region source trails.
33. Positive Japan East / West availability claims in visible body or notes agree with `region_info_reviewed.json`; ignore a claim only when the same sentence explicitly says the region is unsupported.
34. For multi-output hosts, retain one `verify_status.json.results` entry per output filename and aggregate a top-level pass state. Never let the last verified deck overwrite an earlier deck's result.
35. Render representative saved Weekly slides from a temporary local copy. Confirm long titles remain readable and do not overlap the status badge; do not treat a successful COM save as visual proof.
36. Every Weekly item has classification-authored `layoutMode=action|technical|change`, graphical Before / After, and a nonempty full-width left-aligned mode row with a 16pt heading and 13-15pt body. No `KeypointBand` remains. Representative saved renders cover each present mode and avoid decorative card overuse. Render validation must use a hash-verified local snapshot, not a same-named SharePoint/OneDrive presentation with a different slide count or empty representative note.
37. Visible references contain one primary Learn URL, zero to two distinct role-specific related Learn URLs, and the Azure Updates announcement URL. Verify every dedicated shape-level hyperlink, label, and manifest URL in the saved PPTX. The visible date stamp is the Azure Updates publication date; availability and retirement dates remain separate timeline facts.
38. For every new date folder, each classified item has `titleJa`; it is a concise Japanese display title without status wording, while raw `title` retains the fetched Azure Updates title for the same `id`. Confirm P2, Weekly slides, and UPDATE Points show `titleJa`, every displayed title resolves to exactly one classification item through raw `title` or `titleJa`, and the saved deck remains readable within two rendered title lines. Titles must be unique and not prefix-related after 12 normalized characters.

Done means `Verify-Pptx.ps1` exits `0` and the quality review checks above pass or any exception is explicitly reported.
