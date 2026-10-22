# Review Safeguards

## Host adaptation

- Resolve actual instruction precedence before choosing placement. Cross-repository guardrails belong to the requested host's personal instruction entry; repository rules belong to its applicable repository instruction chain. Do not create a profile or UI configuration without a request.
- Prefer a task skill for reusable work, reference files for background, and scripts or hooks for deterministic repetition. A role requires a real delegation need and host support.
- Translate tools and metadata against the target host's supported capabilities. Mark unsupported behavior and manual-only invocation losses explicitly; never claim an unavailable tool executed.

## Compression evidence

- Compare requirements, prohibitions, scope qualifiers, exceptions and modal strength (`may`, `should`, `must`). Permission must not become obligation; requirements must not weaken; authorization must not broaden.
- State applicability in the rule itself when headings alone could hide a routing, execution, verification or stop conflict.
- Compare representative normal, exception and stop decisions, not just retained keywords. Separate authorized behavior changes from compression.
- Keep implemented-but-unverified obligations pending until evidence establishes completion. Preserve prior text in existing history or an authorized review artifact; this does not authorize a commit.
- Character and line counts indicate context cost, not correctness. Material compression needs an independent old/new evidence review; if unavailable or prohibited, record `NOT_RUN`, retain unresolved obligations and do not claim verified equivalence.

## Trigger decisions

For a new or materially changed skill name or description, check these cases. For manual-only skills, natural-language cases must not imply automatic loading.

| # | Case | Expected |
| --- | --- | --- |
| 1 | Explicit invocation plus core task | Load and perform the requested workflow |
| 2 | Natural-language core task | Match only if implicit invocation is allowed |
| 3 | Adjacent context plus the core task | Same invocation policy; preserve scope |
| 4 | Nearby domain requiring another action | Do not activate |

Record the selected skill, whether instructions were read, route and result. Narrow an overbroad description and repeat all cases after a negative-control failure. Static YAML/link checks do not prove host routing; unexecuted host cases are `NOT_RUN`.

## Attribution

Safeguards adapted from aktsmm's customization review material (CC BY-NC-SA 4.0), with primitive-selection concepts credited there to Skill Creator+ (Apache-2.0) and trigger-evaluation design input from OpenAI's public Skill evaluation guidance. Existing owner license and attribution remain unchanged.
