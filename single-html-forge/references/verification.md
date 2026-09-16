# Verification

`verify_html.py` covers what is decidable. This page covers what is not.

## Running the gate

```
python scripts/verify_html.py artifact.html --tier2
```

`0` PASS, `1` FAIL, `2` UNVERIFIED. Only `0` means it can go out.

Read that exit code from the command itself. In PowerShell, an early-terminating pipeline consumer can leave `$LASTEXITCODE` stale or unset instead of reflecting the native command — `... | Select-Object -First 3` does this and a `FAIL` reads as `0`. Measured: `-First` loses the status, `-Last` keeps it. Run the verifier bare, read the status immediately, and filter saved output afterward.

Tier 1 is standard library and always runs. Tier 2 needs Playwright; without it the result is `UNVERIFIED`, never `PASS`. Reporting an artifact as finished on Tier 1 alone is the failure mode this exit code exists to prevent.

To prove the gate still bites after changing it:

```
python scripts/test_verify.py
```

Negative fixtures must fail, positive ones must pass. A suite where everything passes proves nothing.

Assert `MODEL`/`URL` reports for malformed JSON types and links, not merely a failing process. A traceback is not the verifier's failure contract. The export contract tests also check unsupported option combinations, source/output collisions and byte-for-byte preservation after rendering or replacement failure. Verify that new test methods are actually discovered: nesting a `test_*` function inside another function silently removes it from the suite; an AST guard rejects that form.

Run `python scripts/test_browser.py` when changing runtime navigation or visibility-dependent checks. It requires Playwright and Chromium and tests real page transitions, not only generated markup.

## Error codes

| Code                                 | Meaning                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------ |
| `CANONICAL`                          | syntax a browser and a parser could read differently                     |
| `ENCODING`                           | BOM, bad UTF-8, control character                                        |
| `ELEMENT` / `ATTR`                   | outside the HTML allowlist                                               |
| `SVG_ELEMENT` / `SVG_URL` / `SVG_NS` | outside the SVG subset                                                   |
| `PINNED`                             | a `script` or `style` that is not one of the four known regions          |
| `TAMPERED`                           | pinned content does not match its approved hash                          |
| `UNSUPPORTED_VERSION`                | declared version is not in the registry — an old artifact, not an attack |
| `THEME`                              | a custom property or value outside the token grammar                     |
| `MODEL`                              | manifest missing, unparseable, or wrong schemaVersion                    |
| `ASSET`                              | manifest and images disagree                                             |
| `MIME`                               | declared type does not match the bytes                                   |
| `METADATA`                           | a chunk outside the allowlist survived                                   |
| `IMG` / `URL`                        | a resource or link that is not permitted                                 |
| `BUDGET`                             | over the size limit                                                      |
| `TIER2`                              | something only visible in a browser                                      |

After editing fixed CSS/runtime, bump the version before running `build_skeletons.py`; reusing an existing version with a changed hash is rejected. Do not overwrite old registry entries to silence `TAMPERED`.

## What Tier 2 does

Blocks network egress, builds an independent ordered list of every slide/step, follows the actual keyboard path and checks each resulting state. It waits for fonts/images, then checks decoded images, SVG viewBox, expected step visibility, element boundaries, overflow and console errors. Step decks must be finalized before delivery so complete print pages are present. `DERIVED` indicates invalid steps or stale/mismatched derived output; `INPUT` indicates an invalid numeric control.

SVG viewBox validity is checked even while hidden. Dimensions are checked in the visible state, excluding intentionally hidden steps and static print markup. Expected visible step groups must have nonzero size. Keep the complete walk: a diagram hidden now must be inspected when its stage is reached. For SVG use the hidden attribute, not a JavaScript expando named hidden.

For a deliverable deck, Tier 2 also enters print media and checks each printed page for nonzero dimensions, media visibility and content outside its boundary. PDF export calls that same print check immediately before rendering, without publishing any output on failure. Tests inject print-only overflow and verify actual browser resolution of copied SVG names and internal links. The check restores the screen viewport and does not change the selected slide/step. Draft finalization preflight skips print checks until the static pages have been generated; the final candidate never skips them.

The print generator's exact-text self-comparison only proves deterministic generation. It does not prove that references resolve to the intended elements or that text fits: keep the independent browser link/name assertions, geometry failure fixture and PDF checks instead of relying on generator-against-itself tests alone.

Player regression: run `python -B -m unittest discover -s scripts -p "test_*.py"`. This includes pending audio resume/mute, volume zero, failed fullscreen, focus restoration, sidebar/display changes, replacement-stage printing, thumbnail generation and actual PNG export. Optional `SHF_SCREENSHOTS` records desktop/mobile captures from the browser tests. Sound API success is not an assessment of pleasantness; listen before choosing a tone for a live presentation.

## What no check can tell you

**Secrets inside an image.** A tenant name in a screenshot is pixels. Look at every screenshot before embedding, and again in the finished file.

**Whether the content is true.** Verification says the file is well-formed, not that the claims hold.

**Whether it reads well.** See `anti-slop.md`.

**Whether the colours work in the room.** A projector washes out low contrast that looks fine on a laptop.

## By eye, before shipping

- Open the file directly from disk, not through a server. That is how the recipient will open it.
- Deck: arrow through every slide, press `S`, confirm the notes match.
- Grouped outline: compare chapter membership with the source, expand/collapse with mouse and keyboard, jump between chapters, cross a boundary with next/previous, and confirm exactly one current-page marker. Tier 2 alone does not prove chapter membership or cross-format information parity.
- Doc: scroll from top to bottom and watch the sidebar highlight follow. Click a citation and confirm it lands.
- Poster: export the PNG and look at the PNG, not the HTML.
- Narrow the window to about 800px on a doc.
- Print preview if it will be printed.
- Search the file for any customer, tenant, or project name that should not be there.

## Release checks

Run these when the skill itself changes, not on every artifact.

- Copy the skill folder outside the workspace and run `test_verify.py` there. It must pass, which is what proves the skill is portable.
- Grep the folder for absolute paths and for names of other skills. Neither should appear as a required step.
- Confirm Pillow-less and Playwright-less paths still stop loudly rather than passing.
