# Pattern 2: Routing

**Classify input → Route to specialized handlers**

> Back to [overview.md](overview.md)

Use when inputs fall into clear categories that need different handling, and misclassification is cheap to detect.

## VS Code Implementation

```yaml
---
name: Support Router
description: Classify a request and delegate it to the matching specialist agent
tools: ["agent", "read", "search"]
agents: ["Tech Support", "Billing", "FAQ", "General Assistant"]
---
## Routing Rules

1. Technical keywords → Tech Support
2. Billing/payment keywords → Billing
3. FAQ match → FAQ
4. Otherwise or low confidence → General Assistant (default route)
```

- `agents` restricts which subagents the router may call; when it is set, `agent` must be in `tools`.
- Specialists that should only be reached through the router: set `user-invocable: false` (hidden from the picker). Do not use the deprecated `infer`.
- For user-chosen routing instead of model routing, offer `handoffs` buttons from the router.

## Default Route Rules

| Condition                     | Action                              |
| ----------------------------- | ----------------------------------- |
| Low confidence / unknown type | Default handler (General Assistant) |
| Ambiguous input               | Ask one clarifying question         |
| Out of scope                  | Decline or escalate                 |

- Log unclassified inputs; repeated patterns signal a missing specialist.
- The default route must not absorb work that a specialist exists for.
