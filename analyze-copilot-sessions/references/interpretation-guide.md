# Interpretation Guide

## Single Session Analysis

For one run, report the primary model and effort, participating agent roles,
AIU and time, LLM/tool errors, quality evidence, and missing-data warnings.
Describe observed concentration or failure signals without claiming they caused
the outcome. Do not produce winners, Pareto results, or model rankings.

## Session State

Classify the verified target run and latest request, not the mutable session
directory. Treat user, LLM, agent-response, tool, and child-subagent execution
as execution-bearing; ignore customization discovery and resolution events for
liveness.

- `ACTIVE`: execution-bearing events continue within the declared observation
  window, or direct evidence shows a target operation is still in flight.
- `COMPLETED`: the latest request has a correlated terminal response or external
  workflow completion artifact, with no unresolved in-flight operation.
- `STALLED`: the latest request lacks completion evidence and task-bearing
  progress beyond the observation window.
- `UNKNOWN`: target identity, request correlation, or terminal state cannot be
  established from available evidence.

Do not classify state from the active chat, directory recency, UI spinner, or
log modification time alone.

## Confidence

| Confidence | Conditions                                                                   |
| ---------- | ---------------------------------------------------------------------------- |
| `HIGH`     | Same non-empty workload fingerprint and compatible measurement scope         |
| `MEDIUM`   | Same task class and unit, compatible scope, but fingerprint differs          |
| `LOW`      | Different/missing task class, unit, scope, or insufficient workload metadata |

Quality evidence gaps and sample size below three are reported as additional
limitations. They do not silently change metric values.

## Winners

Keep winners separate:

- lowest AIU per unit
- fastest elapsed time per unit
- fastest active LLM time per unit
- strongest external quality evidence

Do not collapse these into a weighted overall winner unless the user supplies
weights before calculation.

## Pareto Frontier

The default frontier minimizes cost per unit and elapsed seconds per unit while
maximizing quality-evidence level. Only externally measured, passing runs are
eligible. A frontier can contain multiple runs because one may be cheaper while
another is faster.

## Group Statistics

Group by primary model and reasoning effort. Report:

- sample size
- median
- first and third quartiles
- IQR
- quality measured/pass counts

For one sample, quartiles equal the observed value. Treat it as a run result,
not a stable model baseline. Call out outliers rather than deleting them.

## Recommended Report

1. State the purpose-specific conclusion first; for one run, summarize usage and bottlenecks rather than a winner.
2. Show a compact table with model/effort, sample size, AIU/unit, time/unit, and quality level.
3. State comparability confidence and reasons.
4. Separate observed evidence from interpretation.
5. Name missing AIU or quality data explicitly.
6. For live sessions, label snapshot-derived cumulative values as lower bounds
   and state the snapshot time and missing-call count.
7. End with the recommended use case for each non-dominated configuration.

Never describe AIU as USD or another currency. Never infer accuracy from final
assistant wording, error rate, retry count, or fixes found without external
quality evidence.
