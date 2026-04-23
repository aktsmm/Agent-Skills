# Skill Bloat Review

Checklist for deciding whether a SKILL is growing by useful depth or by append-only accumulation.

## Review Order

Use this order every time:

1. Delete
2. Merge
3. Move to references
4. Add only what is still missing

## Triage Buckets

### Delete Candidates

- Stale guidance tied to old tool names or workflows
- Repeated best practices already stated elsewhere in the same SKILL
- Session-specific notes that are not reusable
- Long examples that do not change behavior

### Merge Candidates

- Two sections expressing the same rule with different wording
- Separate tables that should be one decision table
- Repeated warnings that belong under one principle
- Multiple mini-checklists that can become one review gate

### Move Candidates

- Sections longer than roughly 40-50 lines
- Large examples, schemas, command catalogs, or recipes
- Long external link lists
- Variant-specific guidance that not every invocation needs

### Add Candidates

- Missing trigger guidance that affects discoverability
- A new decision point users repeatedly get wrong
- A reusable rule that cannot fit cleanly into existing sections
- A reference file that reduces main-file token cost

## Bloat Signals

- New sections are appended without rewriting old ones
- The same concept appears in three or more places
- Main SKILL reads like a knowledge dump instead of an operating guide
- References exist, but detail still stays inline in SKILL.md
- Line count grows while the core workflow becomes harder to find

## Keep vs Move

| Keep in SKILL.md                  | Move to references/     |
| --------------------------------- | ----------------------- |
| What the skill is for             | Deep recipes            |
| Trigger conditions                | Large tables            |
| Core workflow                     | Implementation variants |
| Misuse-prevention decision points | Long examples           |
| Minimal review gates              | Link collections        |

## Decision Questions

- Can this replace an old sentence instead of adding a new paragraph?
- Is this needed on every invocation, or only sometimes?
- Does this teach the operating shape of the skill, or just document background detail?
- If this were removed from the main file, would the skill still route and operate correctly?

## Done Criteria

- Main SKILL still exposes the routing surface clearly
- Core workflow is visible without scrolling through recipes
- Duplicate rules are merged into one place
- Deep detail is loaded on demand via references
- New additions were made only after delete/merge/move was considered
