# Release Readiness Review

Use this workflow after writing and developmental review are complete, before a book is sent to a publisher, printer, store, or distribution channel. It applies to print, PDF, EPUB, and web editions. Project-local commands and product-specific rules stay in the target repository.

## Release Candidate Contract

Do not review a moving target. Start by recording one release candidate with:

- source revision or immutable snapshot
- manuscript source of truth
- proof or typeset revision, when different from current source
- required output formats and filenames
- change window since the last accepted candidate
- open editorial comments, accepted exceptions, owners, and deadline

Local preview output and publisher-typeset output are different artifacts. Record both when they exist, and never infer publisher page counts or layout from the local build.

At Gate 0, enable only the modules the book needs:

- content modules: figures, citations and permissions, exercises and answer keys, glossary, index, runnable code or procedures, companion files, localization, AI-generated or third-party assets, preview and promotional materials
- compliance modules: accessibility, privacy and consent, contractual approvals, regulated-content disclaimers, trade or territory restrictions
- channel modules: print, fixed-layout PDF, reflowable EPUB, web, downloadable package, retailer or distributor submission
- lifecycle modules: release communication, backup and recovery, errata and support, revision or withdrawal

Checks for a disabled or absent module are `NOT_APPLICABLE`, not failures.

Every module disposition, including `NOT_APPLICABLE`, must record the reason, decision owner, and evidence. Do not use module selection to bypass an unknown requirement. Authorship, originality, and the right to publish the manuscript are baseline checks and cannot be disabled as modules.

## Gate Sequence

Run gates in order. A failure blocks dependent gates. If a fix changes source, assets, metadata, conversion, or styles, invalidate and rerun every affected downstream gate.

## Execution Architecture

The main agent remains the release orchestrator. It freezes the candidate, chooses review lanes, owns the evidence record, verifies findings, applies edits, reconciles conflicts, and makes the release recommendation. Do not delegate the whole release decision to one worker.

Use the lowest-cost reliable executor for each task:

| Work                                                                                                          | Executor                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Inventory, extraction, counts, URL GET checks, validators, builds, timestamps, and hashes                     | Deterministic scripts or tools                                                                                              |
| Link meaning, factual grounding, chapter flow, answer/explanation agreement, and bounded proof classification | Read-only reviewer or fact-check subagent with a narrow scope                                                               |
| Screenshot privacy, crop, grayscale, printed-size legibility, and final rendered-page judgment                | Main agent or human reviewer using the actual image; a subagent may prepare the inventory but not replace visual inspection |
| Cross-chapter reconciliation and release decision                                                             | Main orchestrator                                                                                                           |
| Final challenge to the plan and evidence                                                                      | Independent read-only critic at Gate 8                                                                                      |

Parallelize only independent lanes. Partition broad review by chapter, claim set, URL batch, annotation batch, or output format, and give each item one primary owner. Reviewer workers are read-only by default; the main orchestrator applies accepted changes and reruns affected gates.

## Context and Grounding Rules

1. Give each reviewer a compact packet containing the frozen revision, exact scope, authoritative files or URLs, change window, review criteria, required output schema, and stop condition. Do not send the full conversation or unrelated repository history.
2. Retrieve source just in time. For long manuscripts, review bounded chapters or claim groups and return only the decision, key evidence, unresolved questions, and next action. Store large raw results outside the main context and return their relative path when auditability requires them.
3. Keep current state in the candidate evidence record. After compaction, handoff, or a new session, re-read that record and the authoritative source. Conversation summaries and model memory are navigation aids, not release evidence.
4. Require every factual finding to identify the source location or official URL, the supporting excerpt or section, the retrieval date, and one status: `VERIFIED`, `CONFLICT`, or `UNVERIFIED`.
5. Treat model output as a lead, never as evidence. The main orchestrator opens the cited source and confirms the finding before accepting it. If authoritative sources conflict or cannot be retrieved, do not infer the answer; record `CONFLICT` or `UNVERIFIED` and block or escalate according to priority.
6. Separate detection from adjudication: deterministic checks detect known defects, bounded reviewers judge meaning, and the independent critic challenges the assembled evidence. A critic cannot prove that an unrun check passed.
7. Use a different model family for the independent critic when the host and project policy allow it. Record the reviewer, model or route, scope, and verdict. Context isolation reduces context rot but is not a security boundary; tool and data permissions still need separate controls.
8. Exclude known historical prompt or instruction snapshots, obsolete generated copies, and dedicated incident archives from automatic Copilot context with `.copilotignore` or the host equivalent. Exclude only directories whose contents are not current SSOT or current release evidence; do not broadly hide active source, proofs, or candidate records.

## Reviewer Return Contract

Every reviewer lane must return a structured result that the main orchestrator validates before advancing. The project may use JSON, YAML, or an equivalent machine-readable artifact, but it must contain:

- lane identifier and exact scope or range
- candidate revision and source fingerprint used for review
- status: `COMPLETED`, `BLOCKED`, or `FAILED`
- expected and reviewed item counts
- findings with priority, source location, and evidence reference
- `CONFLICT` and `UNVERIFIED` items
- produced artifact paths, when any
- cleanup status for processes and temporary files started by the worker

Reject a worker result when it is narration-only, targets a different candidate or scope, has missing or mismatched counts, cites missing or stale evidence, omits required fields, or leaves its own interactive/background work unresolved. A statement such as `review complete` or `all items passed` is not completion evidence.

The main orchestrator persists accepted worker results through the project-approved path, verifies referenced artifacts and source fingerprints, and only then updates the gate record. Workers do not directly overwrite the final release record unless an explicit project contract allows it.

Retry recoverable transport, schema, or current-artifact drift failures within a bounded project policy, with three attempts as the default ceiling. Do not retry through candidate mismatch, unavailable authoritative evidence, permission failure, rights uncertainty, secret exposure, or another hard gate; stop and escalate with the last valid state.

## High-Risk Change Contract

Treat a change as high risk when it can alter a factual conclusion, answer, legal or rights position, publication identity, reader-visible reference, proof/source mapping, or the rendering of many pages.

Each high-risk change must record:

- before and after values
- authoritative source or decision owner
- why rejected alternatives are wrong or unsafe
- blast-radius search across mirrored or related content
- affected artifacts and invalidated downstream gates
- focused read-only review by a different model family when available, or a named human reviewer when it is not

The focused critic receives only the touched diff, authoritative evidence, and affected references. Its verdict supplements deterministic validation and source verification; it cannot replace them. Do not advance while a high-risk change lacks evidence, blast-radius disposition, or required review.

### Gate 0: Freeze Scope and Evidence

1. Name the release candidate and its source revision.
2. Identify the authoritative manuscript, metadata, assets, generated outputs, and publisher proof. Record the manuscript SSOT path or identifier, proof artifact path or identifier, and a candidate fingerprint; Gate 0 passes only when the record and reviewed artifacts match them.
3. List changed chapters, images, questions, references, build code, and metadata since the accepted baseline.
4. Define P1/P2/P3 and who may accept a P2 exception.
5. Name the responsible reviewer, release approver, exception approver, and tie-break authority.
6. Confirm the authorship and originality basis, contributor agreements, ownership or publication rights, and absence or disposition of unattributed reused content.
7. Record each module's disposition, reason, decision owner, acceptance standard, and evidence source.
8. Create an evidence record before running checks.

Stop if the source revision, proof baseline, required formats, or decision owner is unknown.

Also stop when an enabled compliance or channel module has no named requirement owner, acceptance standard, or evidence source. A module may be `NOT_APPLICABLE`, but it may not be silently omitted.

### Gate 1: Inventory Preflight

- Confirm every expected chapter, front-matter item, back-matter item, image, table, question set, and output exists.
- Confirm required source, metadata, asset, build, validator, and packaging inputs exist before expensive work.
- Record the last accepted artifact and the expected outputs for each enabled channel.

### Gate 2: Deterministic Source Checks

Run the repository's structure, notation, spelling, question, cross-reference, image-reference, metadata, and build validators before subjective review.

Also search for:

- TODOs, placeholders, authoring notes, unresolved conflict markers, and temporary labels
- missing or duplicate headings, chapters, figures, tables, notes, and answer keys
- stale generated digests, indexes, glossaries, counts, and chapter maps
- secrets, personal data, internal URLs, local absolute paths, and unpublished customer information

Machine checks detect known patterns. They do not replace factual, semantic, or visual review.

For enabled runnable-code or procedure modules, execute every reader-facing command, code sample, exercise setup, and destructive or irreversible procedure in a supported environment or a documented equivalent. Record the environment fingerprint, prerequisites, expected result, and actual result. A sample that cannot be executed must be explicitly classified and justified; do not present an unverified sample as tested.

### Gate 3: References and Links

Extract all reader-visible URLs and citations. Review the complete set, not a sample.

For every destination:

1. Use GET to verify the final HTTP result. Do not classify a HEAD-only failure as a broken link.
2. Record redirects and confirm that the final page is still the intended source.
3. Prefer an official page in the reader's language when it exists. Verify the localized URL directly; do not create it by mechanical locale replacement alone.
4. Confirm that the page supports the nearby claim, answer, quotation, or procedure. HTTP 200 is not semantic validation.
5. Flag retired products, renamed features, volatile pricing or plan pages, and time-sensitive specifications for manual fact review.
6. Check fragment identifiers, visible link text, PDF line breaking, and clickability in each output format.

A critical link that is broken, points to the wrong claim, or silently redirects to unrelated content is P1. A valid but nonpreferred locale is normally P2.

Maintain a link inventory with the source location, displayed URL, final URL, locale, retrieval time, and status. For claim-bearing links, also record a claim identifier and the evidence excerpt or section that supports the claim. This keeps semantic validation auditable without requiring excerpts for navigation-only links.

For citations, quotations, excerpts, and reused tables or figures, record the source, the applicable permission basis (license, written permission, contractual right, or documented quotation exception), required attribution, and any scope or territory limit. URL reachability is not permission evidence.

### Gate 4: Content and Reader Journey

Review the full manuscript for release-wide invariants. Review 100% of the change window in detail, and risk-sample unchanged content using chapter boundaries, dense figures or tables, volatile facts, prior defects, and output-format boundaries.

- required topic and reader-outcome coverage
- agreement with the declared reader persona: assumed knowledge, chapter-level outcomes, difficulty progression, and boundaries for non-target readers
- factual accuracy and current product names
- chapter order, definitions, cross-chapter references, and duplicated explanations
- ambiguity and safety: missing conditions, environment-dependent instructions, double negatives, destructive operations without warnings, and wording likely to cause a harmful misapplication
- inclusive and respectful treatment of people, regions, cultures, identities, abilities, and experience levels; escalate legal, safety, or discrimination risk rather than guessing intent
- reputational and legal risk in statements about identifiable people or organizations, including defamation, false endorsement, and misleading claims about affiliation or approval
- localization consistency across prose, terminology, units, dates, keyboard labels, examples, screenshots, and user-interface language; translated editions also require completeness and semantic review by a reviewer qualified for the target locale
- discoverability of major concepts through canonical terms, abbreviations, aliases, former names, glossary entries, index terms, and search-visible wording
- agreement among body text, summaries, captions, tables, examples, questions, answers, and explanations
- front matter, acknowledgements, index, glossary, colophon, copyright, edition, author, publisher, ISBN, and dates
- required disclaimers, safety notices, update cut-off statements, and limitations for the book's subject and market
- consistency between source, generated digests, and every published format

For answer-bearing content, compare each answer with its explanation and source. Structural presence checks cannot detect a valid-looking but wrong answer label.

### Gate 5: Figures, Screenshots, and Rights

Inspect every new or changed visual, plus unchanged visuals selected by risk. Always include first and last chapters, chapter boundaries, dense tables, full-page figures, and output-format boundaries.

Check:

- text-to-visual agreement and correct placement
- crop, scale, resolution, grayscale contrast, legibility at printed size, and right-edge clipping
- captions, alt text, numbering, source files, and attribution
- third-party names, avatars, repository names, tenant data, tokens, email addresses, and other unintended disclosure
- trademark, logo, screenshot, font, stock asset, and code-sample permissions
- consent or contractual approval for identifiable people, customer or partner names, case studies, testimonials, and nonpublic environments
- provenance and permitted-use terms for AI-generated material, third-party code, datasets, templates, and externally supplied assets
- whether the prose still works if an optional visual is removed during typesetting

Rights uncertainty and sensitive-data exposure are P1. Do not defer them as cosmetic issues.

### Gate 6: Editorial and Proof Closure

Treat annotated proofs as structured input.

1. Extract all annotations and record counts by file and annotation subtype.
2. Confirm with the editor which annotations require author action. A marker helps classification but does not prove completeness.
3. Resolve what each annotation points to from its page context or highlight rectangle.
4. Map PDF pages to printed folios and identify the typeset source revision with textual sentinels.
5. Record one decision and evidence trail per comment, including typesetter-applied edits that only ask for confirmation.
6. Reconcile the decision count with the extracted total and leave no unresolved P1/P2 without an owner and deadline.

Do not close an editorial thread until the accepted change is visible to the reviewer or the rejection includes its reason and source.

### Gate 7: Build, Artifact, and Channel Review

Run a full conversion and full build after source-side gates pass. Partial builds are diagnostic only. Inspect generated content, not only successful exit codes.

- verify the freshness chain from source through intermediate output, styles, configuration, metadata, cover, and final files
- record tool versions, commands, exit results, artifact timestamps, page counts, and hashes
- rasterize or otherwise scan every page for blanks, missing content, overflow, clipping, malformed glyphs, and conversion residue
- visually inspect representative and high-risk pages at actual output size
- verify table of contents, bookmarks, page numbers, running heads, chapter openers, footnotes, code blocks, tables, URLs, and colophon
- open every deliverable and compare print, ebook, EPUB, and web editions for required parity
- verify final filenames, cover, spine, back cover, embedded metadata, and packaging contents
- compare product descriptions, preview excerpts, sample pages, promotional copy, and public release announcements with the frozen candidate; verify factual claims, quoted material, rights, confidentiality, pricing or availability statements, and version-specific promises

Automated all-page scans and manual high-risk inspection are complementary. Representative screenshots alone cannot prove that no page is missing.

Apply the enabled channel modules:

| Channel                | Minimum checks                                                                                                                                                                                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Print / fixed PDF      | locked trim size, bleed and safe area, spine calculation basis, placed-image DPI, color space, transparency and overprint, complete font embedding and licensing, barcode scan, cover and colophon, edition and ISBN metadata, and physical proof approval when required |
| Accessible PDF         | tags, heading and table structure, reading order, language, alternate text association, keyboard navigation, and validation against the declared accessibility standard                                                                                                  |
| Reflowable EPUB        | EPUB structural validation, navigation document, landmarks, language metadata, reading order, alt text, reflow and zoom behavior, and accessibility validation against the declared standard                                                                             |
| Web                    | canonical and indexing settings, responsive reading order, accessibility, privacy or legal links when applicable                                                                                                                                                         |
| Download package       | manifest, filenames, checksums, licenses, companion-file references, absence of temporary or source-only files                                                                                                                                                           |
| Retailer / distributor | required product metadata, classification, price, currency, tax treatment, territories, rights, release date, format-to-identifier mapping, accessibility metadata or statement, and channel-specific package rules                                                      |

Validate deliverables on a declared compatibility matrix of readers, operating systems, devices, screen sizes, or print conditions. Validate file structure and integrity, not only whether the artifact opens. When a channel transforms the uploaded artifact, retrieve or preview the channel-final result and compare its content, metadata, pagination or reading order, and visible rendering with the approved manifest.

For runnable code, companion packages, downloadable files, connected services, or web features, verify dependencies and known vulnerabilities, scan distributed files for malware, and document authentication, authorization, credential handling and rotation, transport security, required privileges, network destinations, data collection, retention, deletion, and third-party sharing. Disclose or remove unexpected telemetry or data collection. Security and privacy findings that could harm a reader or expose data are P1.

Extend accessibility review to companion files, audio, video, and interactive content. Require captions, transcripts, descriptions, or an equivalent accessible alternative when the enabled accessibility standard calls for them.

For enabled print, retailer, distributor, or territory modules, confirm applicable legal deposit or registration duties, production handoff acceptance, manufacturing specifications, warehouse or fulfillment receipt, and return or replacement route. After delivery, retain the recipient's acceptance or rejection evidence and perform a channel-final transaction smoke test when practical, such as purchase, download, or access from the reader-facing surface. If the test is omitted, record the reason, decision owner, alternative evidence, and reopen condition; omission is not an implicit PASS.

### Gate 8: Independent Sign-Off and Manifest Lock

Give a compact evidence packet to an independent reviewer or critic. Include the frozen candidate, change window, gate results, accepted exceptions, known risks, and exact questions.

The critic checks the plan and evidence; it is not the detector of last resort. If the critic and producer disagree, use the tie-break authority named at Gate 0. Fix recurring misses in an upstream checklist or deterministic validator.

After approval, create and verify a release manifest containing the source revision, proof revision when applicable, enabled modules, build command or configuration fingerprint, tool versions, deliverable filenames, sizes, and hashes. Re-read the staged or upload-ready package and compare it with the manifest. Any mismatch invalidates approval and restarts the affected gates.

Before release, record how to reproduce the build, restore the approved candidate and evidence, notify stakeholders, receive errata or accessibility reports, issue a corrected edition, and suspend or withdraw a defective release. Include security and privacy incident response when digital files, credentials, personal data, or connected services are involved: notification, package replacement, credential rotation, escalation, and withdrawal triggers. Apply only the enabled lifecycle modules, but require an owner and trigger condition for each enabled path.

Release only when:

- P1 is zero
- P2 is zero or each remaining item has an owner-approved exception with an expiry or reopen condition
- all required formats were rebuilt from the frozen candidate after the last relevant fix
- editorial decisions and release communication match the evidence record

## Priority Model

| Priority | Meaning                          | Examples                                                                                                                                                                            |
| -------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P1       | Blocks release                   | factual error, wrong answer, missing page, broken build, rights uncertainty, secret or personal-data exposure, unresolved author decision, critical link with the wrong destination |
| P2       | Fix or obtain explicit exception | readability or layout defect, inconsistent metadata, stale screenshot, noncritical broken link, preferred-locale miss                                                               |
| P3       | Does not block this edition      | polish, optional visual, next-edition improvement                                                                                                                                   |

Do not use a percentage pass rate for P2. One unresolved P2 can affect a whole edition; require either resolution or a named exception.

### Deterministic gates sit outside this model

A gate a script decides — link reachability, structural validation, terminology sweeps, budget checks — is not a priority-ranked finding. It passes or it fails, and a failing one blocks regardless of how the priorities elsewhere are trending.

Reviewers and critics will argue for waiving one on cost or reader value. Answer with the rule the gate encodes and the measurement it produced rather than with a judgement call. If the rule itself is wrong, change the rule and re-run the gate; do not exempt a case from a rule you intend to keep.

## Reused Review Output Goes Stale

A stored review result is a statement about one revision, not a standing fact.

- Head every stored result with its run date and the candidate revision it examined
- Before citing an earlier result, check whether the files it covered moved since that revision. If they did, re-run it or narrow the citation to the part that did not move
- Overwrite in place when one lane re-runs against the same target, and keep cross-cutting reviews as separate dated documents so the older reading stays readable
- When a measurement later replaces the estimate a finding rested on, re-rank the finding and record both numbers with the method used. An estimate quietly overwritten regenerates the same finding next time
- Re-derive the overall verdict after any re-ranking. A held verdict left standing after its only blocking finding was withdrawn misleads everything downstream

## Evidence Record

For each gate, record:

- status: `PASS`, `FAIL`, `BLOCKED`, or `PASS_WITH_EXCEPTIONS`
- command or review method
- artifact or scope inspected
- measured result and evidence location
- finding owner and due condition
- exception approver, expiry, and reopen condition when applicable
- invalidated downstream gates after a fix

Keep release evidence separate from reusable rules. The workflow belongs here; candidate-specific results belong in the book repository.
