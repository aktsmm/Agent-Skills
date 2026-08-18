# Python Engine Lineage Inventory

The portable engine harvests proven behavior from dated workspace assets without importing them at runtime.

| Legacy asset class               | Decision                                                                                              | Portable owner                                                       |
| -------------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `build_all.py` / `build_pptx.py` | Harvest slide primitives, notes, hidden slides, local-temp OpenXML writes; retire dated import chains | `scripts/python/build_customer_pptx.py`                              |
| Python `verify_pptx.py`          | Harvest OpenXML structural observations only; it is not an independent release verdict                | `scripts/Verify-Pptx.ps1` + `scripts/Invoke-PptxVerify.ps1`          |
| `Render-Pptx.ps1` / visual QA    | Keep as evidence pattern; render unique local snapshots and preserve canonical hash                   | canonical visual review rules                                        |
| `Export-Pdf.ps1`                 | Harvest local-copy export and unencrypted-PDF checks                                                  | `scripts/Export-PptxToPdf.ps1` + `scripts/Test-PptxDistribution.ps1` |
| dated requirements files         | Replace with exact portable pins                                                                      | `scripts/python/requirements.lock`                                   |
| dated validation artifacts       | Use only as external regression evidence; never package customer data                                 | synthetic tests + external acceptance run                            |

## Migration Rules

- No portable script imports a dated workspace builder.
- Customer names, tenant/subscription IDs, local absolute paths, and dated folder constants are forbidden.
- `classification.json` order is the build-order SSOT; renderers do not silently reorder it.
- Python structural checks feed the canonical verifier and parity report; they never declare delivery success alone.
