# Template Lifecycle

Use this reference when starting from an empty workspace or changing the customer-facing PowerPoint design. The template is a design artifact first; scripts should protect it, not invent it.

## Phase 1: Human-Led Template Design

Create the customer-specific template in PowerPoint before regular automation.

Required design decisions:

- cover, summary, body topic, UPDATE Points, ending, and optional hidden cover variants
- slide size and typography
- customer branding and visual density
- placeholder text such as `{{CUSTOMER}}`, `{{SYSTEM}}`, `{{DATE}}`, `{{SPEAKER}}`
- UPDATE Points table columns and row capacity
- where source URLs, labels, notes, and region stamps should appear

During this phase, scripts may inspect or report structure. They should not auto-refine the visual design unless the user explicitly asks for a repair helper.

## Phase 2: Template Contract

After the user accepts the design, record what automation may rely on:

| Contract Item         | Examples                                                                   |
| --------------------- | -------------------------------------------------------------------------- |
| Required slides       | cover, summary, body sample, UPDATE Points, ending                         |
| Required layouts      | cover layout, body layout, table layout                                    |
| Required placeholders | `{{CUSTOMER}}`, `{{SYSTEM}}`, `{{DATE}}`, optional `{{SPEAKER}}`           |
| Table contract        | 5 columns: #, keyword, update, key point, region                           |
| Hidden policy         | hidden cover variants may remain; Appendix slides are hidden               |
| Stamp policy          | region stamps are added by script and must not be pre-baked on body slides |

If a contract item is missing, stop before content build and fix the template.

## Metadata Hygiene

Before checking a template into any repo (private or public), strip inherited metadata from the source PowerPoint. Inspect the `.pptx` as a zip and clean:

- `docProps/core.xml` — `creator`, `lastModifiedBy` (remove personal names that are not the owner)
- `docProps/app.xml` — `Company`, `TitlesOfParts` (may leak internal deck names)
- `docProps/custom.xml` — SharePoint columns, MSIP / MIP labels, tenant IDs, sensitivity marks

For any public-facing repo, at minimum rewrite `docProps/custom.xml` to an empty `<Properties/>` element and remove non-owner names and emails from `core.xml`. Do this once per template revision, not per generation. PowerPoint re-adds SharePoint / MIP metadata every time the file is opened from OneDrive or SharePoint, so treat the check-in copy as a separate artifact.

## Phase 3: Regular Generation

Once the template contract passes, regular runs should be boring:

1. Fetch and normalize Azure Updates into manifests.
2. Prepare classification and initial region data.
3. Build or re-apply the deck from the validated template.
4. Run Verify and quality review.

This is where deterministic scripts provide the most value.

### Source Layout Normalization

`Slides.InsertFromFile` preserves source slide masters and layouts. When multiple source decks use different body designs, do not ship mixed Weekly Topic layouts. Rebuild every Weekly Topic from one named customer body layout/prototype and manifest content, then reapply region stamps, dedicated official-reference shapes, and speaker notes. Run Verify and visual QA again, then regenerate any delivery PDF after the final PPTX mutation.

## Phase 4: Maintenance and Repair

Maintenance scripts are recovery tools, not the default route.

- Use refine/cleanup scripts only when a template is already known to be structurally wrong.
- Use fix scripts only for a failed gate or manifest correction.
- After any repair, rerun the same verifier that failed.

The goal is a stable template contract plus small deterministic repairs, not repeated full-template surgery.
