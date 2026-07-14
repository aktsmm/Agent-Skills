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

Done means `Verify-Pptx.ps1` exits `0` and the quality review checks above pass or any exception is explicitly reported.
