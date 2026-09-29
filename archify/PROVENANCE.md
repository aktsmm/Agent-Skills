# Provenance

This Skill is a derivative import of the Archify Agent Skill by tt-a1i.

- Source: https://github.com/tt-a1i/archify/tree/69cf672087289033af5138648d3875d3d73fc431/archify
- Upstream release: 3.0.1 (`skill-release.json`)
- Upstream commit: `69cf672087289033af5138648d3875d3d73fc431`
- Upstream license: MIT. `LICENSE` and `THIRD_PARTY_NOTICES.md` are retained verbatim.
- Upstream lineage: Archify declares itself based on Cocoon-AI/architecture-diagram-generator (MIT).

## Local changes

- Excluded `test/` (upstream development suite) and `examples/*.html` (rendered sample outputs). The runtime does not read them; `doctor`, `demo`, and `finalize` passed after the exclusion.
- `SKILL.md`: appended a routing boundary and Japanese triggers to `description`, and added the `Local adaptation notes` section.
- Added `PROVENANCE.md`, `skill-license.json`, and `.gitattributes` (`* -text -whitespace`), which keeps upstream LF bytes on Windows checkouts with `core.autocrlf=true` and exempts upstream generated files from `git diff --check`.

Every other file is byte-identical to the upstream commit above. Because `test/` is excluded, the `npm test` and build scripts in `package.json` are upstream development commands and do not run in this copy; use `doctor` and `finalize` instead.

## Re-import

1. Fetch the new upstream `archify/` folder at a pinned commit, for example with a sparse clone.
2. Replace every file except `PROVENANCE.md`, `skill-license.json`, and `.gitattributes`.
3. Re-apply the two `SKILL.md` changes, then remove `test/` and `examples/*.html`.
4. Run the Node probe from `SKILL.md`, `doctor`, and `finalize` on an upstream example with `ARCHIFY_UPDATE_CHECK_DISABLED=1`; all four gates must pass.
5. Update the commit and release above, refresh every `evidence` hash in `skill-license.json` (`LICENSE`, `THIRD_PARTY_NOTICES.md`), and rerun `quick_validate.py`.
