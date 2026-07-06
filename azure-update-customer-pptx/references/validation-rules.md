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

Done means `Verify-Pptx.ps1` exits `0` and the quality review checks above pass or any exception is explicitly reported.
