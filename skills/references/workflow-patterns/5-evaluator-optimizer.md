# Pattern 5: Evaluator-Optimizer

**Generate → Evaluate → Improve loop**

> Back to [overview.md](overview.md)

## Diagram

```mermaid
graph TD
    A[Input] --> B[Generator]
    B --> C[Output v1]
    C --> D[Evaluator]
    D -->|Not Good| E[Feedback]
    E --> B
    D -->|Good| F[Final Output]
```

## Characteristics

| Aspect        | Description                                 |
| ------------- | ------------------------------------------- |
| **Structure** | Generator + evaluator + feedback loop       |
| **Benefits**  | Improves until quality criteria are met     |
| **Use Cases** | Translation, code review, text proofreading |

## When to Use

- Clear quality criteria exist
- Iterative improvement increases quality
- Want to mimic human feedback

## Implementation Example

```
Generator: Generate translation
    ↓
Evaluator:
  - Is the nuance accurate?
  - Is the grammar correct?
  - Does it reflect the original intent?
    ↓
  ├─ OK → Complete
  └─ NG → Regenerate with feedback
```
