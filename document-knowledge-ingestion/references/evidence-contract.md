# Evidence Contract

All paths in the ledger are POSIX-style relative paths. Artifact paths resolve under the directory containing the ledger; source-relative paths resolve only under explicitly supplied root aliases. No credentials, local absolute paths, or protected source excerpts belong in this package.

## Ledger Fields

| Field                        | Contract                                                                                                                                         |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `version`                    | Integer `1`                                                                                                                                      |
| `sources`                    | Nonempty list of unique `{id}` aliases; resolve locations at runtime                                                                             |
| `documents[].id`             | Unique stable ID, not a display title                                                                                                            |
| `source_id`, `relative_path` | Approved root alias and relative original location                                                                                               |
| `role`                       | `original`, `derived`, or `auxiliary`; retain version/translation distinctions in notes                                                          |
| `status`                     | `pending`, `extracted`, `empty`, `blocked`, or `excluded`                                                                                        |
| `reason`                     | Nonempty explanation for every state except `extracted`                                                                                          |
| `source_sha256`              | Exact source hash when readable; required for `extracted`                                                                                        |
| `extraction`                 | For `extracted`: `{path, sha256}` pointing to nonempty saved UTF-8 text                                                                          |
| `units`                      | For `extracted`: `{kind: line\|page\|slide, count: positive integer}` from the original, not the converted wrapper                               |
| `reading`                    | For `extracted`: `{status: unread\|partial\|full, ranges: [[first,last],...]}` using inclusive, 1-based original units                           |
| `notes`                      | List of `{path, sources: [document-id,...]}`; UTF-8 Markdown artifacts                                                                           |
| `ocr`                        | List of `{document_id, unit, status, review}` with `status` = `pending`, `recognized`, `no-text`, or `failed`; `review` = `machine` or `checked` |
| `ocr[].result`               | Required for `recognized`: nonempty UTF-8 `{path, sha256}`                                                                                       |
| `ocr[].reason`               | Required for every status except `recognized`; explain unresolved or no-text outcomes                                                            |

Optional per-document metadata includes version date, reader/version, sensitivity, OCR image hashes, and relationships to other records. Optional note metadata can list topic coverage and unresolved claims. The validator does not interpret extra fields, so critical checks must not depend on them.

## Coverage Rules

- Read ranges must be sorted, non-overlapping, within the measured unit count. `full` must cover every unit without gaps; `partial` needs some but not all units; `unread` has no ranges.
- A declared unit is not a certificate of comprehension. Keep a human-readable section table naming the body, examples, appendices, or media omitted. A read request extending beyond EOF does not prove the requested number of lines existed.
- For slide reading, include available notes within each slide's reading scope and state absent/unread images separately. PDF pages do not automatically map to slide numbers.
- Notes may cite only extracted documents with nonempty declared reading coverage. Mention blocked/excluded documents in a limitations list instead of using them as substantive evidence.
- Local Markdown links in notes must resolve inside the library. Cite original locations as alias, relative path, and units; do not make broken machine-local links. External links are retained as references but not fetched by the verifier.
- `no-text` remains ambiguous until reviewed. Strict completion requires `checked` for both recognized and no-text OCR outcomes. Reporting fully processed machine OCR is still allowed without claiming manually checked results.

## Verification Meaning

Default verification checks populated structure, allowed states, path confinement, saved text/hashes, read-range consistency, cited source existence, and note links. An empty template must fail. It reports partial work but does not reject honest blockers solely for being blockers.

`--source-root alias=path` compares recorded source hashes with current files for that alias. Missing hashes or omitted aliases are reported as unchecked; mismatches are failures. The program does not scan undisclosed roots or discover omitted documents.

`--require-complete` requires every non-excluded document to be extracted, fully read, and cited; every declared OCR item resolved and manually checked; all source aliases supplied; and current source hashes verified for included documents. It applies only to the declared scope, not every file on a disk.

Mechanical PASS does not prove semantic accuracy, discovery completeness, OCR quality, publication permission, or freshness of external product specifications. The validator checks reading ranges in the ledger, not prose claims or range annotations inside notes; compare each sampled claim and its cited units with the original and ledger separately. Perform those reviews and name actual checked examples.

## Selection and Refresh

Keep original sources read-only. Exclude dependency/build trees and unrelated sensitive files before copying content, but inspect plausible topic misses beyond keyword matches. Record unsupported formats instead of dropping them.

Deduplicate exact bytes with hashes while retaining source/version mappings. Count originals, generated exports, and summaries separately; notes based on the same underlying work are not independent evidence.

On refresh, compare source versions before overwriting any generated copy. A changed source invalidates prior full-reading claims until affected notes and ranges are reviewed. Preserve human edits; never delete the library with a blanket cleanup.

If interrupted, persist current artifacts and states after each batch. Resume from those states, not from remembered totals. Protect evidence supplied to reviewers from temporary-file cleanup.
