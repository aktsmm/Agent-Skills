# Screenshot Capture

Rules for producing product screenshots that survive monochrome print, a rights review, and a re-capture two revisions later. Crop width, aspect, and grayscale checks against the built page are in [figure sizing](review-pdf-tips.md); the release-time inspection is [Release Readiness Review](release-readiness-review.md) Gate 5.

## Decide what earns a screenshot

Prefer a real screen wherever one exists. A reader recognises the product from it and recalls the operation; a book of diagrams alone reads like it was written away from the product. A few per chapter is a workable target.

The exception is a screen that carries no more information than the prose already does. A list of file names does not beat the table explaining what each file is for. Structure and relationships stay diagrams.

Confirm the element exists in the surface you can actually capture, before building an environment for it. A product often ships different feature sets to its desktop and web clients. Check that the client is fully signed in first: a half-authenticated session renders the surrounding interface while silently omitting the very menu entries you came to photograph, which reads as "the feature is gone" rather than "sign-in is incomplete". When the only surface that shows it differs from the one the chapter's other captures came from, the figures will not sit together on the page, and prose is the cheaper answer.

A policy of "no screenshots" is worth revisiting rather than defending. The usual argument for it is that interfaces change, but that risk is cheaper than the teaching value it costs, and it is disclosed once in the front matter instead of paid for in every chapter.

Do not substitute a diagram that imitates the product's chrome — header bars, sidebars, tab strips. A redrawn interface carries the same trademark exposure as a capture with none of its evidence.

## Choose the environment by who appears in it

Capture only from accounts and projects you can account for: the vendor's own repositories, a well-known public project run by an organisation, or a neutral scratch project you created. Never a third party's personal account or profile.

Then split by whether people appear on the screen.

- Screens without people — dependency lists, release assets, marketplace listings — come from a populated public project. A scratch project shows two rows and loses the point of the figure
- Screens with people — activity summaries, contributor lists, issues, pull requests — come from your own scratch project

Third parties leak in through contributor lists, watcher and star lists, mention targets, and author columns. Check the frame for those before pressing capture.

Attribute a capture of someone else's project directly under the figure. Your own scratch project needs no attribution line.

## Crop the account area, not the whole header

Capturing while signed in is fine, and your own name and avatar may appear. What must not appear is a third party's name, avatar, or address, plus notification counts, billing or plan indicators, experimental feature flags, search history, extension icons, and the tab strip.

Cutting the entire top band to achieve that costs the reader the breadcrumb that says which screen this is. Hide the account side of the header instead, with a rule that preserves layout rather than removing the element, so the breadcrumb stays where it was.

Make a hide selector that matches nothing **fail the capture**. Generated class names rotate, and a silently unapplied rule is discovered by a reader, not by you. Where framing cannot exclude a third party, blur or fill the region and record what was altered.

Resize before you frame. A side panel captured at its default width can clip the descriptions beside each entry, which is often the detail the figure was taken to show. Widen it first, then choose the crop.

Public owner names that a signed-out visitor would also see are fine. Private organisation names, customer names, and anything visible only under a specific contract are not.

Signed-in and signed-out states render different controls, so capture in the state the prose describes.

## Size the capture to the printed width

Printed width is fixed, so the printed text size inside a screenshot is set by how many CSS pixels were packed into it: density = CSS pixel width / printed width in millimetres.

- Derive the CSS width from the capture path rather than assuming it. A browser page capture at a device pixel ratio of 2 has half the CSS width of its image file, while a capture taken through the operating system's window compositor often carries none of that scaling, leaving the window width as the CSS width. Display scaling and the capture API both move this, so measure it once per path and reuse the measurement
- Density is a diagnostic, not a target. Check grayscale legibility at the measured printed width before changing it. A screen whose own type is large survives a high density, and widening the window can add line wraps that make the figure taller instead of clearer
- Lowering density can break a figure. When the point is a fine distinction such as a filled versus an empty checkbox, a wider capture erases it in grayscale. Verify in black and white after any change, and record that the magnification is load-bearing
- For two figures meant to be read as a pair, match effective density rather than zoom. Browser zoom is stored per origin, so a target whose domain changes on every launch cannot reproduce it. Set the window width instead

## Record the capture

Keep a record file beside each image holding the URL, capture date, three lines of steps, crop region, theme, interface language, device pixel ratio, and authentication state. Without it the next edition cannot reproduce the frame.

Records drift from images every time a capture is redone. After a re-capture, reconcile the recorded viewport, crop, and any edit coordinates against the actual image dimensions, and read every line that contains a number — figures buried in prose go stale separately from the ones in tables.

Match the theme to the screenshots already in the book, and force it explicitly rather than relying on a default. Web-hosted editors in particular follow the account's appearance setting, which follows the operating system, so a light capture appears in a dark book without anyone changing anything.

Images supplied by a co-author or an outside contributor have no reproducible procedure. Note them as known exceptions with a count instead of inventing steps to satisfy a checker.

## Do not regenerate over a real capture

Before overwriting anything under the image folder, check the file's history. Batch regeneration run for visual consistency is how a contributor's real screenshot becomes a mock.

When a figure is missing or a path is broken, regenerate exactly the affected file. To find out when an image was swapped, look up the first commit that introduced the current blob rather than reading the file's own log.
