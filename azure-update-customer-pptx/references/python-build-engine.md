# Python Build Engine

The Python engine is an opt-in build path for contract-v1 templates. COM remains the default.

## Boundary

- Select with `.config/config.json` `build.engine = "python"` or `Run-CustomerPptxPipeline.ps1 -Engine python`.
- A missing engine setting means `com`.
- Python never falls back to COM silently. Contract or dependency failures stop before the canonical PPTX is replaced.
- Python builds from the same `classification.json`, `region_info_reviewed.json`, and `notes.json` used by COM.
- Missing reviewed region evidence is fatal for Weekly items. Hidden Appendix items retain the neutral `リージョン情報要確認` state until reviewed; never convert missing evidence into a false Japan-unavailable claim.
- PDF export, rendering, and the canonical delivery verifier remain PowerPoint-backed phases.
- Python output is already enriched; the dispatcher skips COM Enrich to avoid duplicate tables, stamps, and notes.

## Template Contract

Python v1 supports templates conforming to `assets/template-contract.v1.json`. It resolves cover, summary,
UPDATE Points, body, and ending prototypes using the declared layout, text, and shape predicates. Arbitrary
customer templates are unsupported until they pass this contract.

The canonical verifier currently expects hidden Appendix topic count to equal `classification.appendix`;
Python therefore starts the Appendix section at the first hidden topic and does not add a separate divider.

## Runtime

The wrapper uses an existing workspace `.venv` and never installs packages. Create the environment explicitly:

```powershell
uv venv .venv --python 3.12
uv pip sync --python .venv\Scripts\python.exe scripts\python\requirements.lock
```

## Safety

1. Close only the exact canonical target before replacement.
2. Build to a unique local temporary OpenXML file.
3. Validate ZIP structure and semantic counts before copying to the date folder.
4. Keep a verified OpenXML source for later verification if organizational protection re-wraps the canonical file.
5. Use `-NoOpen` for parity and automation. Interactive review opens a local snapshot, never the canonical file.
6. A distribution gate must run immediately before delivery.

## Adoption Gate

COM and Python outputs are compared semantically, not byte-for-byte. Python remains opt-in until both engines
pass the same verifier for sections, ordering, hidden Appendix slides, notes, hyperlinks, region stamps,
UPDATE Points pagination, ending selection, placeholders, bounds, and representative renders.

## Harvested Lineage

The engine was harvested from dated workspace builders (0217/0414/0714/0818) that proved the speed and
OpenXML approach. Those builders, their Python verifiers, render/export sidecars, requirements, and validation
artifacts are legacy fixtures only. The portable runtime never imports a dated builder. Behavior is owned by
the current manifest, template, style, and validation contracts in this skill.
