# Rubber-Duck Review

Use this when the user has an intuition but the factory frame is not yet sharp.

## Question Ladder

Ask only the questions that change the next action.

1. Who exactly has the pain?
2. What do they do today instead?
3. What repeated complaint, workaround, bad review, or spending proves the pain?
4. What is the smallest artifact that can test the riskiest assumption?
5. What would make this idea not worth doing?
6. What platform, legal, privacy, or cost boundary can block it?
7. What metric would make the next cycle obvious?

## Review Frames

| Frame        | What to catch                                                   |
| ------------ | --------------------------------------------------------------- |
| Audience     | Too broad, unreachable, or imaginary user                       |
| Pain         | Nice-to-have disguised as urgent need                           |
| Substitute   | Existing tool already solves it well enough                     |
| Distribution | No believable way to reach first users                          |
| Scope        | MVP still too large for one cycle                               |
| Risk         | Store policy, TOS, privacy, copyright, safety, or payment issue |
| Metric       | Outcome cannot be measured without guessing                     |

## Response Shape

Return the review in this shape:

```markdown
## Sharpest Version

<one sentence opportunity statement>

## Assumptions to Test

- <assumption> -> <how to test>

## Kill Risks

- <risk> -> <early signal>

## First Queue Slice

- discover: <task>
- research: <task>
- build/design: <task>
- review/track: <task>
```

## Opportunity Statement Pattern

```text
For <specific audience> who struggle with <repeated pain>, create <small artifact> that helps them <measurable outcome>, validated by <metric>.
```

## Bias Checks

- If the idea starts from technology, force one pass from user pain.
- If the idea starts from money, force one pass from distribution.
- If the idea starts from a cool mechanic, force one pass from retention or replay value.
- If the idea starts from automation, force one pass from policy and trust risk.
