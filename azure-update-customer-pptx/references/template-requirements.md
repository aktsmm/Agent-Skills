# Template Requirements

- Design the customer template in PowerPoint first. Automation should inspect and enforce the contract; it should not be the primary design tool for a blank customer template.
- Store the runtime template in workspace `template/`.
- Set `.config/config.json` `template.folder` and `template.fileName` to the runtime template.
- Neutral templates may use placeholders such as `{{CUSTOMER}}`, `{{SYSTEM}}`, and `{{DATE}}`.
- The template must support the configured slide size and expected section order.
- Customer branding belongs in the workspace template, not in skill references.
- Maintenance scripts such as refine/cleanup helpers are repair tools. Do not make them part of the normal build path unless a verifier has identified a concrete failure.

## Ending variants

The customer template should include three formal Ending variants paired with the cover variants:

- `Azure Update Cover - Indigo Amber` -> `Indigo Amber` ending
- `Azure Update Cover - Azure Blue` -> `Azure Blue` ending
- `Azure Update Cover - Teal Fresh` -> `Teal Fresh` ending

Ending slides are simple closure slides. Required generated/sample text is `以上` and `Azure アップデート情報`. Do not leave blank placeholders, `Next Steps`, `TBD`, or generic action prompts.

Required ending shape names:

- `Ending-Title`
- `Ending-Subtitle`
- `Ending-Accent*` for visual-only accents

Only the ending paired with the visible cover should be visible in the generated deck; non-selected ending variants must be hidden.

See [template-lifecycle.md](template-lifecycle.md) for the design -> contract -> generation boundary.
