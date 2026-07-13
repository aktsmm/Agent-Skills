# Session Log Template

Use this form for a new log. Remove optional sections that would be empty.

````markdown
---
type: coding|research|debug|design|discussion
exported_at: 2026-01-01T12:34:56
tools_used: [tool1, tool2]
outcome_status: success|partial|failed
---

# Session Title

## Summary

A one- or two-sentence summary.

## Timeline

### Phase 1 - Phase Name

- Work performed
- Modified: [relative/path/file.ext](relative/path/file.ext#L10)

## Key Learnings

- A discovery or reusable learning

## Commands & Code

```text
A reusable command or code excerpt
```

## References

- Page Title - https://example.com/article
- Related File - C:/work/other-repo/path/to/file.md

## Next Steps

- [ ] Unfinished follow-up
````

## Append Template

When a same-day, same-topic file already exists, keep its frontmatter and append this block:

```markdown
---

## Session Update - 2026-01-01T12:34:56

### Summary

A summary of the newly added work.

### Timeline

#### Phase N - Phase Name

- Work performed

### Key Learnings

- A new learning

### Commands & Code

### References

### Next Steps

- [ ] Unfinished follow-up
```

- Update the existing frontmatter `outcome_status` to reflect the latest overall state.
- Keep the actual append time in the `Session Update` heading.
- Add only URLs and related files newly used by this update.
