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

Small, obvious changes need zero consultations. Skipping the critic is a valid outcome — report it as `0 rounds`.

## One Round

1. **Produce**: the producer advances the artifact to the next checkpoint.
2. **Critique**: send the critic packet to a read-only reviewer on a different model family. On round 2+, use the revision-round packet shape (prior findings + what changed).
3. **Reconcile**: classify findings with the reviewer rubric, de-duplicate, and reject low-signal notes explicitly.
4. **Revise**: the producer applies fixes for blocking findings itself, then evaluates the stop condition.

## Stop Conditions

Check these in order after each round:

1. **PASS** — the critic returns no blocking findings **and** has no non-blocking notes worth acting on. This is the primary stop condition. Stop here.
2. **PASS_WITH_NOTES** — no blocking findings remain, but the critic left non-blocking findings or suggestions. You may only stop here after the producer **explicitly** decides to accept and defer those notes. Record which notes were accepted and why they are safe to defer. Do not report a plain PASS when accepted notes remain.
   - Optionally, the producer may apply _cheap, low-risk_ notes (typos, wording, obvious omissions) in a **single pass** before stopping, and then report a plain PASS. Do **not** send that single-pass fix back for re-critique — applying cheap notes must not restart the loop.
   - Notes that need judgment or trade-offs (design preference, alternative approaches) are not auto-applied. The producer keeps deciding; defer and record them. Never let "fixing every note" hand control back to the critic.
3. **Max-rounds fail-safe** — if the loop reaches **3 rounds** without reaching PASS or an accepted PASS_WITH_NOTES, stop anyway and report the remaining blocking findings. This is only a guard against an endless revise/re-critique loop; it is not a target round count. Most loops should stop well before this.

The native Rubber Duck has no fixed round count — it consults by judgment at checkpoints. The max-rounds fail-safe exists only because this loop is driven explicitly and could otherwise oscillate. Prefer the result-based stop (PASS) over the count-based one.

## When the Loop Does Not Converge

If round 3 still has blocking findings, or the critic keeps raising new blocking issues each round:

- Stop the loop. Do not silently keep iterating.
- Report the unresolved blocking findings, what was tried, and the producer's current best artifact.
- Surface the disagreement to the user with a concrete recommendation, rather than forcing a low-confidence change just to clear the critic.

## Multiple Lanes

At a single checkpoint you may run more than one critic lane in parallel (for example a security lane and an architecture lane). That parallelism is across critics within one round, not the producer and critic running at the same time. Merge their findings during reconcile before deciding the stop condition.
