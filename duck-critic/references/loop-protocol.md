# Loop Protocol

The producer-critic loop: the producer (you, the main agent) advances the work to a checkpoint, the critic (a different model) reviews it read-only, the producer reconciles and revises, and the loop repeats until a stop condition is met.

This is a **gated checkpoint loop**, not two agents running at the same wall-clock moment. The value comes from a different model inspecting the producer's current artifact at the right moment, not from simultaneous execution.

## Checkpoints

Consult the critic at high-leverage moments, the same ones the native Rubber Duck targets. Do not consult on every trivial edit.

- **After planning, before implementing**: the plan or design is drafted but no code is written yet.
- **Mid-implementation**: a risky or central piece of the implementation is in place and worth a check before building further on top of it.
- **After drafting tests**: the test strategy or test cases exist and you want to confirm they actually cover the requested behavior.
- **After repeated failures**: the same approach has failed two or more times and a second perspective is needed before retrying.
- **Before a hard-to-reverse decision**: architecture, deployment, schema, or security choices.
- **After executing a change to external or shared state**: a repository, service, or published document has already been touched. Deterministic gates confirm the artifact still passes, but they do not compare declared counts, status notes, and plan documents against what was actually produced, so this is where silent drift between the record and reality surfaces.

Small, obvious changes need zero consultations. Skipping the critic is a valid outcome — report it as `0 rounds`.

## What the Critic Cannot Catch

The critic's field of view is exactly the packet you send, so checkpoint choice decides what the second model can possibly find.

- A **diff-scoped** packet answers "is this change correct?". It cannot answer "what did we fail to detect?" — defects that were never raised as findings stay invisible, and stay invisible across repeated runs of the same gate.
- A packet that shows a safety mechanism **exists** cannot show that it **executes**. When the artifact's argument is "X gets checked at runtime", state the exact invocation in the packet and ask the critic to confirm X actually runs on the real path — caches, flags, early returns, and short-circuits routinely make present-in-source code never execute. This class survives an early PASS, so do not stop at round 1 for gate-severity or safety-critical changes.
- A **plan-scoped** packet is where a second model changes outcomes most, because scope, assumptions, and the rule design are still open.
- A finding built on a **calculated premise** is only as strong as the constant it started from. When the critic derives a blocking issue from a default value, a config setting, or an assumed dimension, measure that constant on the real artifact before revising.
- Measurements in the packet can go stale inside a single loop. Shared artifacts get rebuilt by other people, sessions, and jobs while you iterate, so stamp each measurement with when and where it came from, and re-take the ones a revision depends on before the next round.
- If the same class of defect keeps surviving reviews, the fix is upstream (producer instructions, detection checklist, deterministic gate), not more critic rounds.

## One Round

1. **Produce**: the producer advances the artifact to the next checkpoint.
2. **Critique**: send the critic packet to a read-only reviewer on a different model family. On round 2+, use the revision-round packet shape (prior findings + what changed).
3. **Reconcile**: classify findings with the reviewer rubric, de-duplicate, and reject low-signal notes explicitly. Later rounds tend to surface defects that predate the change under review. Record one as an out-of-scope deferred item, with the evidence that it predates the change, only when the current work neither builds on it nor makes it materially worse; otherwise it stays blocking.
4. **Revise**: the producer applies fixes for blocking findings itself, then evaluates the stop condition.

## Stop Conditions

Check these in order after each round:

1. **PASS** — the critic returns no blocking findings **and** has no non-blocking notes worth acting on. This is the primary stop condition. Stop here.
2. **PASS_WITH_NOTES** — no blocking findings remain, but the critic left non-blocking findings or suggestions. You may only stop here after the producer **explicitly** decides to accept and defer those notes. Record which notes were accepted and why they are safe to defer. Do not report a plain PASS when accepted notes remain.
   - Optionally, the producer may apply _cheap, low-risk_ notes (typos, wording, obvious omissions) in a **single pass** before stopping, and then report a plain PASS. Do **not** send that single-pass fix back for re-critique — applying cheap notes must not restart the loop.
   - Notes that need judgment or trade-offs (design preference, alternative approaches) are not auto-applied. The producer keeps deciding; defer and record them. Never let "fixing every note" hand control back to the critic.
3. **Max-rounds fail-safe** — if the loop reaches **3 rounds** without reaching PASS or an accepted PASS*WITH_NOTES, stop anyway and report the remaining blocking findings, \_unless the loop is converging* as defined below. This is only a guard against an endless revise/re-critique loop; it is not a target round count. Most loops should stop well before this.
4. **BLOCKED** — the critic could not evaluate at all: it never got the artifact, the harness could not select a model, or every dispatch came back unusable. Stop and report what is missing. This is not a PASS.

Each stop condition names a verdict, and the report uses that name: conditions 1 and 2 give `PASS` and `PASS_WITH_NOTES`, the max-rounds fail-safe with blocking findings still open gives `NEEDS_CHANGES`, and condition 4 gives `BLOCKED`. See [output format](./output-format.md) for the verdict definitions.

A loop is **converging** when both hold at the round that would otherwise trigger the fail-safe:

- the blocking count strictly decreased from the previous round, and
- every still-open blocking finding is new — surfaced by the producer's own last revision — rather than one that was already addressed and came back.

A converging loop may take one more round at a time, to a hard cap of **5 rounds**. Anything else is oscillation: a count that held steady or grew, or the same finding returning, stops at 3.

Record the blocking count for every round in the final report, so continuing past 3 is auditable rather than a matter of taste. The extension exists for the case where stopping would knowingly leave a blocking defect in the artifact; it is never a licence to keep polishing. When a fix for a blocking finding is itself capable of creating one — anything touching persistence, rollback, or partial-failure recovery — expect the next round to find it, and budget for that instead of treating the third round as the finish line.

### An Unusable Round Is Not a Round

A dispatch that comes back empty, truncated, off-topic, or lost inside the harness produced no blocking count. Silence is not `blocking: 0` — reading it that way removes the gate rather than passing it, and it looks identical to a clean review in the report.

Discard the dispatch, do not count it toward the fail-safe, and retry once. If the retry is also unusable, fall back per [model lanes](./model-lanes.md); if that fails too, stop the checkpoint as `BLOCKED`. Report how many dispatches were discarded, because a checkpoint that shows one clean round while three came back empty is not the same checkpoint.

The native Rubber Duck has no fixed round count — it consults by judgment at checkpoints. The max-rounds fail-safe exists only because this loop is driven explicitly and could otherwise oscillate. Prefer the result-based stop (PASS) over the count-based one.

Out-of-scope deferred items are not part of `PASS_WITH_NOTES`. They carry no verdict, so list them separately in the final report and keep the notes the producer accepted distinguishable from the defects this loop chose not to own.

## When the Loop Does Not Converge

If the round-3 check shows oscillation, or the hard cap is reached with blocking findings still open:

- Stop the loop. Do not silently keep iterating.
- Report the unresolved blocking findings, the per-round blocking counts, what was tried, and the producer's current best artifact.
- Surface the disagreement to the user with a concrete recommendation, rather than forcing a low-confidence change just to clear the critic.

A loop whose blocking count refuses to fall while new findings keep landing in the same risk class is telling you the design is unsound in that area, not that the critic is noisy. Say that in the report instead of reclassifying findings downward until a stop condition is reached.

## Multiple Lanes

At a single checkpoint you may run more than one critic lane in parallel (for example a security lane and an architecture lane). That parallelism is across critics within one round, not the producer and critic running at the same time. Merge their findings during reconcile before deciding the stop condition.
