# Validation Rules

`scripts/Verify-Pptx.ps1` is the validation SSOT. Keep this document aligned with the script.

Current gate checks:

1. P2 summary is numbered.
2. UPDATE Points table has valid region column values.
3. Weekly topic slides have region stamps.
4. Slides have speaker notes.
5. Section order is valid.
6. Weekly slide order follows label priority.
7. UPDATE Points appears after Weekly Topics.
8. UPDATE Points key points are not generic fallback text.
9. Notes match slide titles/content.

Done means `Verify-Pptx.ps1` exits `0`.
