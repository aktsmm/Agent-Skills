# Battle-Tested Patterns

These are the operational lessons to preserve when turning the factory into a mobile app workspace, Steam game workspace, SaaS lab, content machine, or internal improvement loop.

## 1. Queue, Not Fixed Phase Pipeline

Use a queue of small tasks instead of a rigid linear phase plan.

- Good: add the next `discover`, `research`, `review`, or `build` task when evidence calls for it.
- Bad: force every idea through every stage even after a kill signal appears.

Why: a factory should move attention to the current bottleneck, not worship a diagram.

## 2. Artifact-Only Workers

Workers should write one evidence artifact and avoid shared state mutation.

- Worker output: `artifacts/<task-id>.md` or equivalent.
- State update: orchestrator/reducer imports the artifact and updates queue, logs, and ledgers.

Why: multiple agents editing the same JSON, database row, or tracker creates race conditions, partial writes, and hard-to-debug corruption.

## 3. Single-Writer Reducer

Have exactly one component update shared state.

The reducer should:

- detect completed artifacts
- parse structured data blocks
- move tasks to done/failed/skipped
- update ledgers and summaries
- record parse failures without losing the artifact

If parsing fails, keep the task open and retry after the artifact is fixed.

## 4. One Pulse, One Task

Limit each worker run to one task.

Why: this prevents runaway loops, keeps costs bounded, and makes outputs auditable. If a task wants to do five things, split it into five tasks.

## 5. Pain-First Scouting

Start from raw unmet need, not from technology or what would be fun to build.

Mix sources every discovery pass:

- user reviews and low-star complaints
- Reddit / forums / community threads
- X or social posts with real frustration
- support questions and Q&A sites
- competitor changelogs, issue trackers, and feature requests
- store pages, tags, wishlists, and review themes for games/apps

Avoid source monoculture. If all evidence comes from builders talking to builders, the factory may optimize for interesting implementation instead of painful demand.

## 6. Search and Fetch Are Different

Treat keyword search as discovery and page fetch as evidence reading.

- Search finds candidate sources.
- Fetch/read extracts claims, numbers, quotes, constraints, and contradictions.

Do not let search snippets become final evidence for market, legal, or platform decisions.

## 7. Review Gates Are Separate Thinking Modes

Keep these gates conceptually separate, even when one person runs them:

- Need: is the pain real and repeated?
- Distribution: can first users be reached?
- Scope: can the riskiest assumption be tested with one small artifact?
- UX/fun: is the first experience clear or compelling?
- Technical: can it be built and maintained cheaply enough?
- Platform/legal: do store rules, TOS, privacy, copyright, or claims block it?
- Outcome: what metric decides hot, stale, or rejected?

Why: builders are biased toward building; scouts are biased toward novelty; critics are biased toward rejection. Separate gates keep those biases useful.

## 8. Blockers Accumulate Before Interrupting Humans

Workers should not stop the whole loop for one login, paid API, publish action, or account question.

Default order:

1. Try a free or local substitute.
2. If no substitute exists, write a `## blocker` section in the artifact.
3. Let the orchestrator aggregate similar blockers.
4. Ask the human only when the same blocker repeats or blocks a high-value path.

A practical threshold is three similar blockers, but tune it by domain risk.

## 9. Notification Compression

High-frequency worker loops should not notify on every run.

Report periodically with:

- queue health
- promising opportunities
- stale or rejected items
- repeated blockers
- next-cycle focus

Why: too much notification trains humans to ignore the system.

## 10. Metrics Need Provenance

Every metric must say whether it is observed, estimated, or assumed.

Examples:

- observed: installs, wishlists, paid purchases, replies, playtest completion
- estimated: review-count proxy, traffic estimate, price-band inference
- assumed: expected conversion, estimated build effort, hypothetical retention

Never blend these into one score without preserving provenance.

## 11. Feedback Updates the Next Search

The learning output should change future discovery and evaluation.

Track:

- categories that produced good signals
- categories to avoid
- scout source quality
- critic calibration: what it approved that failed, and what it rejected too early
- build friction: tech stacks or asset scopes that repeatedly overrun
- distribution patterns that actually reached users

If learning does not alter the next queue, it is just a report.

## 12. Build the Smallest Artifact That Tests the Riskiest Assumption

For a mobile app, this might be a clickable prototype, permission-risk test, store listing draft, or local MVP.

For a Steam game, this might be a 10-minute loop, one mechanic prototype, capsule/copy test, playtest build, or trailer script.

Stop building when the artifact can answer the current question. Do not build a full product to test whether the pain exists.

## 13. Degraded Operation Beats False Failure

If a preferred tool, memory search, or external source fails, switch to a lower-tech path before marking the task failed.

Examples:

- read existing artifacts directly
- use local grep/search over ledgers
- use public pages instead of logged-in dashboards
- record an evidence gap instead of inventing a metric

Only fail when the task cannot produce a useful artifact under the constraints.

## 14. Domain-Specific Translation

Keep the core loop stable, but translate evidence and metrics by domain.

| Domain      | Demand Evidence                                                       | Small Artifact                                         | Outcome Signal                                        |
| ----------- | --------------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------- |
| Mobile apps | app review complaints, repeated tasks, permission-sensitive workflows | prototype, local MVP, store copy                       | installs, waitlist, retention proxy, review sentiment |
| Steam games | review themes, tag gaps, streamer pain, modding demand                | vertical slice, trailer script, capsule/copy, playtest | wishlists, playtest completion, creator interest      |
| SaaS/tools  | forum complaints, spreadsheet workarounds, issue trackers             | CLI, web MVP, landing page                             | signups, replies, paid pilots, usage                  |
| Content     | search demand, Q&A repetition, paid info gaps                         | article, outline, landing page, sample lesson          | reads, saves, purchases, replies                      |

The mistake to avoid is copying the same metrics across domains.
