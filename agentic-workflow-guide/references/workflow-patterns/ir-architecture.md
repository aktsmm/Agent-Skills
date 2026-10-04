# IR Architecture (Intermediate Representation)

**Advanced pattern for transformation tasks with deterministic output**

> Back to [overview.md](overview.md)

Use for document generation, code transformation, report generation, and template filling where the same input must give the same output. Not for creative writing, exploratory analysis, or adaptive conversation.

```
Input → Generate IR → Validate IR → Transform → Render → Output
                          └─ invalid → reject / fix (no auto-completion)
```

## Stage Responsibilities

| Stage         | Role                                   | Creativity            | VS Code implementation                      |
| ------------- | -------------------------------------- | --------------------- | ------------------------------------------- |
| **Generate**  | Create IR from input                   | High (interpretation) | LLM agent; writes IR to a file              |
| **Validate**  | Verify IR completeness and correctness | None (rule-based)     | Script / schema check, not an LLM judgement |
| **Transform** | Convert IR to output format            | None (mechanical)     | Script or template engine                   |
| **Render**    | Format final output                    | Low (formatting only) | Script; LLM only for prose polish           |

Keeping Validate and Transform deterministic is what makes failures inspectable: same IR → same output, and a bad result is traced to either the IR or the transformer.

## IR Specification Guidelines

1. **Define allowed structure** - JSON, YAML, or structured Markdown
2. **Strict schema** - All required fields must be present
3. **No inference** - Missing data = error, not auto-completion
4. **Version control** - IR schema should be versioned

## Current State In Append-Only Documents

When one document contains both current state and history, do not search the entire body for status keywords.

1. Define explicit start and end boundaries for the current-state region.
2. Parse only that region with an exact header/schema.
3. Reject missing columns, wrong cell counts, and duplicate logical keys.
4. Exclude the history region by construction, not with a growing list of old statuses.

This prevents an old `pending` record from being revived as current work.

## Example IR Schema

```json
{
  "document": {
    "title": "string (required)",
    "sections": [
      {
        "heading": "string (required)",
        "content": "string (required)",
        "subsections": ["array (optional)"]
      }
    ],
    "metadata": {
      "author": "string",
      "version": "string",
      "created": "ISO8601 date"
    }
  }
}
```

Test each stage independently: fixtures of IR → expected output for Transform, invalid IR → rejection for Validate.
