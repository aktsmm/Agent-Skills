# Pattern 1: Prompt Chaining

**Sequential processing with validation at each step**

> Back to [overview.md](overview.md)

Use when the step order is fixed and each step's output is the next step's input.

## VS Code Implementation

- Human-driven chain: one custom agent per step, linked with `handoffs` (`send: false` keeps the user as the gate). See [handoffs-guide.md](../handoffs-guide.md).
- Autonomous chain: one agent body with numbered steps, each followed by a gate checked against a file or command result (tests, validator, schema), not the model's own claim.
- Pass state between steps through files (e.g. `tmp/step1-output.json`), not conversation memory; later steps and resumed sessions can then re-read it.

## Gate Rules

- Each gate names the artifact and the pass condition (`tests pass`, `schema valid`, `file exists and non-empty`).
- On FAIL: fix and re-run that step only; do not continue with a failed intermediate.
- An empty extraction must fail the gate, not pass a "no violations found" check downstream.
