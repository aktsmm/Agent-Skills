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
- Stop building when the artifact already tests the riskiest assumption.
- Stop expanding roles when one role would be idle for multiple cycles.
