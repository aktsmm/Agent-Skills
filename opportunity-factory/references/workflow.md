# Opportunity Factory Workflow

## Purpose

This reference turns a domain goal into a repeatable factory. The domain can be mobile apps, Steam games, SaaS, content, internal tools, research prototypes, or any other artifact stream.

## Factory Frame

Define these fields before running the loop:

| Field           | Meaning                  | Example                                                   |
| --------------- | ------------------------ | --------------------------------------------------------- |
| `domain`        | The territory to explore | `mobile apps for solo creators`                           |
| `artifactType`  | What gets produced       | `Android MVP`, `Steam demo`, `landing page`, `article`    |
| `audience`      | Who has the pain         | `indie game streamers`, `busy parents`, `small clinics`   |
| `successMetric` | What proves progress     | `wishlists`, `installs`, `paid downloads`, `time saved`   |
| `constraints`   | Hard boundaries          | `no paid APIs`, `no external publishing without approval` |

Keep the frame short. It is a steering constraint, not a strategy essay.

## Throughput KPI

A fixed output quota and a strict quality gate cannot both be hard constraints. One of them breaks, and it is the gate, because missing a visible number feels like failure while a quietly lowered bar does not.

Split the target:

- **attempt** — how many candidates the factory starts on. The workload dial.
- **publish** — how many cleared every gate. This is a **forecast, not a commitment**.

**Make the gate and the attempt budget hard; leave publish soft.** A hard publish floor recreates the exact pressure this section exists to remove: when the count is short, the only lever left is the bar. If a stakeholder needs a committed number, commit to attempt volume and gate pass rate, not to output.

Manage on **gate pass rate**. Raise the attempt target after the pass rate is stable, never before. When output is short, that deficit means candidate selection is weak, so the response is more discovery and differentiation work.

Per-lane or per-category quotas are **caps, not targets**. Their sum may exceed the attempt target on purpose, which leaves room to shift emphasis while still preventing one category from taking everything. State which meaning a number carries; a cap read as a target silently becomes a quota to fill.

## Generic Roles

| Role         | Responsibility                                                                      |
| ------------ | ----------------------------------------------------------------------------------- |
| Orchestrator | Keeps the queue filled, imports artifacts, summarizes blockers, chooses next focus  |
| Scout        | Finds raw pain, demand, trends, reviews, competitor gaps, and unsolved complaints   |
| Researcher   | Validates market, audience, existing substitutes, feasibility, and evidence quality |
| Critic       | Kills weak ideas, exposes false assumptions, and sets go/no-go conditions           |
| Designer     | Turns a validated opportunity into a small solution spec                            |
| Builder      | Creates the smallest useful artifact                                                |
| Reviewer     | Checks UX, technical quality, legal/TOS, store/platform risk, and launch readiness  |
| Tracker      | Measures outcomes and labels ideas as promising, stale, blocked, or invalidated     |

One person or agent can hold several roles. Keep the role names even in a small setup because they preserve the thinking boundaries.

## Queue Kinds

Use these generic task kinds:

| Kind       | Output                                                       |
| ---------- | ------------------------------------------------------------ |
| `discover` | candidate opportunities with evidence                        |
| `research` | evidence summary, risks, alternatives, confidence            |
| `evaluate` | decision, score, kill criteria, next condition               |
| `design`   | scope, user flow, mechanics, data model, acceptance criteria |
| `build`    | runnable artifact, prototype, draft, or packaged output      |
| `review`   | findings, required fixes, optional improvements              |
| `track`    | metrics, observed response, hot/stale decision               |
| `learn`    | pattern update and next-cycle direction                      |

## Artifact Contract

Every task should leave one artifact with these sections:

````markdown
# <task id> - <short title>

## summary

One paragraph with the result.

## evidence

- Source or observation
- Why it matters
- Confidence: high|medium|low

## decision

go|conditional|reject|blocked|needs-more-data

## next actions

- One or more executable next tasks

## structured data

```json
{}
```
````

For review tasks, add `## required fixes`. For blockers, add `## blocker` with the approval or missing dependency.

## Review Gates

Use only gates that change the decision. Suggested gates:

| Gate            | Questions                                                               |
| --------------- | ----------------------------------------------------------------------- |
| Need            | Is the pain real, repeated, and reachable?                              |
| Differentiation | Why would someone choose this over existing substitutes?                |
| Scope           | Can one small artifact test the core assumption?                        |
| UX              | Is the first-run path obvious and short?                                |
| Technical       | Can it be built and maintained with available tools?                    |
| Platform        | Are App Store, Google Play, Steam, marketplace, or social rules a risk? |
| Legal           | Any privacy, copyright, regulated activity, or misleading claim risk?   |
| Outcome         | What metric will decide hot, stale, or rejected?                        |

### Gate Placement

Which gate runs is only half the design. **When it runs decides how much work gets thrown away.**

- **Differentiation is a blocking gate placed before the expensive lanes**, not part of the final review. A factory that only checks differentiation at the end discovers "this is not better than the existing substitute" after paying for research and production.
- The boundary is **full evidence collection and build**, not all evidence. A **light probe is allowed and expected**: two or three pieces of evidence, enough to enumerate claims. Fully separating the gate from evidence creates a chicken-and-egg problem, because you cannot name what is distinctive about a candidate without touching it.
- Judge **per claim, not per topic**. An incumbent covering the subject does not cover every claim about it. Failure conditions, side effects, applicability limits, and operational judgement are frequently absent from official sources even when the topic is documented.
- Failing the gate means reject or re-angle, never proceed to the expensive lanes. Cap re-angle attempts so a doomed candidate cannot loop.

## Domain Examples

### Mobile App Factory

- `discover`: mine app reviews, Reddit, X, forums, and support communities for repeated complaints.
- `research`: verify existing apps, pricing, install volume, review sentiment, and retention hints.
- `evaluate`: reject ideas that need paid data, regulated advice, or impossible acquisition.
- `design`: one-screen core loop, onboarding, permissions, data storage, monetization hypothesis.
- `build`: clickable prototype, local MVP, store listing draft, or testable Android/iOS shell.
- `review`: privacy, permissions, battery/network cost, accessibility, app store policy.
- `track`: waitlist, install intent, test user feedback, retention proxy.

### Steam Game Factory

- `discover`: mine Steam reviews, subreddit complaints, streamer comments, modding communities, and genre trend gaps.
- `research`: compare tags, capsule art, median review counts, price bands, update cadence, and scope risk.
- `evaluate`: kill ideas that need huge content volume, expensive art, or multiplayer ops too early.
- `design`: core mechanic, 10-minute loop, art constraint, demo promise, wishlist hook.
- `build`: vertical slice, trailer script, Steam page copy, prototype, or playtest build.
- `review`: fun clarity, onboarding, performance, controller support, platform policy, asset licensing.
- `track`: wishlists, playtest completion, feedback themes, demo retention, creator interest.

## Stop Conditions

- Stop a loop when the next action needs human approval.
- Stop an opportunity when the core need is unproven after two independent evidence passes.
- Stop an opportunity when the differentiation gate fails and the re-angle cap is reached.
- Stop building when the artifact already tests the riskiest assumption.
- Stop expanding roles when one role would be idle for multiple cycles.
