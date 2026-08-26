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

`TAMPERED` after editing `assets/css/` or `assets/runtime/` just means the registry is stale. Re-run `build_skeletons.py`.

## What Tier 2 does

Blocks all network egress, walks every slide, waits for fonts and images to finish — by event, not by timer, because a timed sample lets a slow image escape inspection — then checks for zero-size images, SVG without a viewBox, overflow, and console errors.

## What no check can tell you

**Secrets inside an image.** A tenant name in a screenshot is pixels. Look at every screenshot before embedding, and again in the finished file.

**Whether the content is true.** Verification says the file is well-formed, not that the claims hold.

**Whether it reads well.** See `anti-slop.md`.

**Whether the colours work in the room.** A projector washes out low contrast that looks fine on a laptop.

## By eye, before shipping

- Open the file directly from disk, not through a server. That is how the recipient will open it.
- Deck: arrow through every slide, press `S`, confirm the notes match.
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
