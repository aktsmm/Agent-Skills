# Release Readiness Record

Create one copy of this record for each release candidate. Keep reusable workflow rules outside this file.

## Candidate

| Field                                            | Value                   |
| ------------------------------------------------ | ----------------------- |
| Title                                            | {{BOOK_TITLE}}          |
| Candidate ID                                     | YYYY-MM-DD-release-name |
| Source revision                                  | TODO                    |
| Manuscript SSOT path / identifier                | TODO                    |
| Candidate fingerprint                            | TODO                    |
| Proof revision / identifier                      | NOT_APPLICABLE          |
| Proof artifact path / identifier                 | NOT_APPLICABLE          |
| Accepted baseline                                | TODO                    |
| Change window                                    | TODO                    |
| Required deliverables                            | TODO                    |
| Reviewer                                         | TODO                    |
| Release approver                                 | TODO                    |
| Exception approver                               | TODO                    |
| Tie-break authority                              | TODO                    |
| Authorship / originality basis                   | TODO                    |
| Publication rights / contributor agreements      | TODO                    |
| Unattributed reused content search / disposition | TODO                    |

## Enabled Modules

Use `ENABLED` or `NOT_APPLICABLE`. Every row requires a reason, decision owner, and evidence; blank dispositions block Gate 0.

| Module                            | Disposition              | Reason / acceptance standard | Decision owner | Evidence |
| --------------------------------- | ------------------------ | ---------------------------- | -------------- | -------- |
| Figures / screenshots             | ENABLED / NOT_APPLICABLE |                              |                |          |
| Citations / external links        | ENABLED / NOT_APPLICABLE |                              |                |          |
| Exercises / answer keys           | ENABLED / NOT_APPLICABLE |                              |                |          |
| Glossary / index                  | ENABLED / NOT_APPLICABLE |                              |                |          |
| Runnable code / procedures        | ENABLED / NOT_APPLICABLE |                              |                |          |
| Companion files                   | ENABLED / NOT_APPLICABLE |                              |                |          |
| Localization                      | ENABLED / NOT_APPLICABLE |                              |                |          |
| AI-generated / third-party assets | ENABLED / NOT_APPLICABLE |                              |                |          |
| Preview / promotional materials   | ENABLED / NOT_APPLICABLE |                              |                |          |
| Accessibility                     | ENABLED / NOT_APPLICABLE | Standard / scope:            |                |          |
| Privacy / consent                 | ENABLED / NOT_APPLICABLE |                              |                |          |
| Contractual approvals             | ENABLED / NOT_APPLICABLE |                              |                |          |
| Disclaimers / regulated content   | ENABLED / NOT_APPLICABLE |                              |                |          |
| Trade / territory restrictions    | ENABLED / NOT_APPLICABLE |                              |                |          |
| Print / fixed PDF                 | ENABLED / NOT_APPLICABLE |                              |                |          |
| Reflowable EPUB                   | ENABLED / NOT_APPLICABLE |                              |                |          |
| Web                               | ENABLED / NOT_APPLICABLE |                              |                |          |
| Download package                  | ENABLED / NOT_APPLICABLE |                              |                |          |
| Retailer / distributor submission | ENABLED / NOT_APPLICABLE |                              |                |          |
| Release communication             | ENABLED / NOT_APPLICABLE |                              |                |          |
| Backup / recovery                 | ENABLED / NOT_APPLICABLE |                              |                |          |
| Errata / support                  | ENABLED / NOT_APPLICABLE |                              |                |          |
| Revision / withdrawal             | ENABLED / NOT_APPLICABLE |                              |                |          |

## Gate Results

Use `PASS`, `FAIL`, `BLOCKED`, `PASS_WITH_EXCEPTIONS`, or `NOT_APPLICABLE`.

| Gate                                      | Status | Method / command | Scope / artifact | Evidence | Owner / next condition |
| ----------------------------------------- | ------ | ---------------- | ---------------- | -------- | ---------------------- |
| 0. Scope and evidence                     |        |                  |                  |          |                        |
| 1. Inventory preflight                    |        |                  |                  |          |                        |
| 2. Deterministic source checks            |        |                  |                  |          |                        |
| 3. References and links                   |        |                  |                  |          |                        |
| 4. Content and reader journey             |        |                  |                  |          |                        |
| 5. Figures, screenshots, and rights       |        |                  |                  |          |                        |
| 6. Editorial and proof closure            |        |                  |                  |          |                        |
| 7. Build, artifact, and channel review    |        |                  |                  |          |                        |
| 8. Independent sign-off and manifest lock |        |                  |                  |          |                        |

## Review Lanes

| Lane ID | Scope / expected count | Candidate / source fingerprint | Executor / model | Reviewed count | Result artifact | Status / owner |
| ------- | ---------------------- | ------------------------------ | ---------------- | -------------: | --------------- | -------------- |

## Worker Result Acceptance

Allowed lane status values are `COMPLETED`, `BLOCKED`, or `FAILED`.

| Lane ID | Status valid | Target match | Count match | Evidence fresh | Artifact verified | Cleanup verified | Required fields missing / invalid | Accepted / reason |
| ------- | ------------ | ------------ | ----------- | -------------- | ----------------- | ---------------- | --------------------------------- | ----------------- |

When a result is rejected, record every missing or invalid required field by name; do not write only `schema mismatch` or `failed`.

## Lane Findings Index

| Lane ID | Finding ID | Priority | Source location | Evidence reference | Status | Owner / resolution |
| ------- | ---------- | -------- | --------------- | ------------------ | ------ | ------------------ |

Use `VERIFIED`, `CONFLICT`, or `UNVERIFIED` for Status. A result artifact supplements this index; it does not replace the required finding-level evidence.

## Retry and Escalation

| Lane ID | Attempt count | Recoverable reason | Hard-gate reason | Escalated at | Last valid state / artifact |
| ------- | ------------: | ------------------ | ---------------- | ------------ | --------------------------- |

## High-Risk Changes

| Change ID | Before / after | Authoritative source / owner | Rejected alternatives | Blast-radius result | Invalidated gates | Independent review / verdict |
| --------- | -------------- | ---------------------------- | --------------------- | ------------------- | ----------------- | ---------------------------- |

## Grounding and Conflicts

Use `VERIFIED`, `CONFLICT`, or `UNVERIFIED`. Model output alone is not evidence.

| Claim / finding ID | Status | Source location / final URL | Supporting excerpt / section | Retrieved at | Verified by | Resolution / owner |
| ------------------ | ------ | --------------------------- | ---------------------------- | ------------ | ----------- | ------------------ |

## Link Inventory

Use `claim` for a link that supports a factual statement or answer, and `navigation` for a reader path that needs no evidence excerpt.

| Source location | Kind | Displayed URL | Final URL | Locale | Retrieved at | Result | Claim ID | Evidence excerpt / section | Owner / status |
| --------------- | ---- | ------------- | --------- | ------ | ------------ | ------ | -------- | -------------------------- | -------------- |

## Rights and Approvals

| Item / location | Asset or claim type | Permission / consent basis | Attribution / restriction | Approver / evidence | Status |
| --------------- | ------------------- | -------------------------- | ------------------------- | ------------------- | ------ |

## Compatibility and Accessibility

| Channel / target | Standard or environment | Validator / review method | Result | Exceptions / owner |
| ---------------- | ----------------------- | ------------------------- | ------ | ------------------ |

## Delivery and Security

| Item / channel                                               | Check | Result / receipt | Owner | Follow-up trigger |
| ------------------------------------------------------------ | ----- | ---------------- | ----- | ----------------- |
| Dependency / vulnerability scan                              |       |                  |       |                   |
| Malware / package integrity scan                             |       |                  |       |                   |
| Authentication / authorization                               |       |                  |       |                   |
| Credential handling / rotation                               |       |                  |       |                   |
| Transport security / network destinations                    |       |                  |       |                   |
| Data collection / retention / deletion / third-party sharing |       |                  |       |                   |
| Legal deposit / registration                                 |       |                  |       |                   |
| Production / fulfillment handoff                             |       |                  |       |                   |
| Channel-final purchase / download / access                   |       |                  |       |                   |
| Product description / preview / promotion / announcement     |       |                  |       |                   |

If a channel-final transaction test is omitted, record the reason, decision owner, alternative evidence, and reopen condition in the final row. Do not leave it blank or mark it passed without reader-facing evidence.

## Post-Release Readiness

| Path                          | Owner | Trigger | Procedure / evidence | Status |
| ----------------------------- | ----- | ------- | -------------------- | ------ |
| Reproduce build               |       |         |                      |        |
| Restore candidate             |       |         |                      |        |
| Release communication         |       |         |                      |        |
| Errata / accessibility report |       |         |                      |        |
| Corrected edition             |       |         |                      |        |
| Suspend / withdraw            |       |         |                      |        |
| Security / privacy incident   |       |         |                      |        |

## Exceptions

| ID  | Priority | Decision | Approver | Expiry / reopen condition | Evidence |
| --- | -------- | -------- | -------- | ------------------------- | -------- |

## Release Manifest

| Field                                     | Value          |
| ----------------------------------------- | -------------- |
| Source revision                           | TODO           |
| Proof revision / identifier               | NOT_APPLICABLE |
| Enabled modules snapshot                  | TODO           |
| Build command / configuration fingerprint | TODO           |
| Tool versions                             | TODO           |
| Staged or upload-ready package            | TODO           |
| Package hash                              | TODO           |
| Manifest comparison                       | PASS / FAIL    |

| Deliverable | Size | Hash | Built from source revision | Verified |
| ----------- | ---: | ---- | -------------------------- | -------- |

## Decision

- Verdict: `RELEASE` / `DO_NOT_RELEASE`
- Decided by:
- Decided at:
- Remaining risks:
- Invalidated gates after the last fix: None / TODO
