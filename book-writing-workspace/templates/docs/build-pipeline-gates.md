# Build Pipeline Gates

Use these invariants when a writing workspace converts source files or renders final artifacts. Keep tool names, package versions, and commands in project-local documentation.

## Gate Sequence

| Stage | Verify before work starts | Stop when |
| --- | --- | --- |
| Source validation | Required runtime modules are declared and importable | A dependency is missing |
| Conversion | The converter can normalize source metadata that conflicts with target formatting | A fixture changes its expected output |
| Rendering | The required runtime responds through its CLI or API | The runtime is installed but not ready |
| Artifact review | The generated artifact contains the expected labels and layout | Build success is the only evidence |

Run each gate immediately before its dependent stage. A converter does not need renderer-only dependencies, but a renderer must validate every dependency it will use.

## Metadata Normalization

When the target formatter automatically assigns labels, normalize only recognized source-side labels at the converter boundary. Preserve ordinary captions unchanged.

- Match known manual label formats explicitly; do not strip broad leading text.
- Add fixtures for every accepted format, an unnumbered caption, and a caption containing only the manual label.
- If removing a label leaves no caption, use a documented fallback or fail validation. Do not silently change the policy.
- Verify the generated intermediate output contains one label source only before rendering.

## Runtime Readiness

Installation or a visible GUI process is not proof that a build runtime is ready. Use the runtime's CLI or health endpoint and fail before conversion or rendering begins when it does not respond.

Error output should identify the missing layer: dependency declaration, importable module, command-line tool, runtime service, or final artifact quality.

## Done Criteria

- [ ] Dependencies are declared by pipeline stage.
- [ ] Each entry point runs its prerequisite gate before expensive work.
- [ ] Converter fixtures cover metadata normalization and fallback behavior.
- [ ] Final artifact checks inspect generated content, not only command exit status.