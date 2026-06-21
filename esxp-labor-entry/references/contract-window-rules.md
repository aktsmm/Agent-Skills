# Contract Window Rules

The most common planning mistake is using **delivery date** as if it were the labor-entry window. It is not.

## Core Principle

A dispatch matters only if you log at least some labor **inside its valid contract window**.

## Where To Read The Window

Use **Support Delivery > Request Details**.

Request details URL shape:

```text
https://esxp.microsoft.com/#/supportdelivery/requestdetails/<ID>
```

Both RMOT and ROSS requests can be opened with this route.

## RMOT Interpretation

For RMOT / single dispatch work:

- `Request Start Date` / `Request End Date` on the page are the real entry window
- delivery may happen on only some of those days
- labor can be distributed across multiple days or weeks **as long as it stays inside that window**

## ROSS / EDE Interpretation

For ROSS or EDE-type work there are often **two date layers**:

- `Request Start Date` / `Request End Date`: actual delivery activity window
- `Agreement Start Date` / `Agreement End Date`: broader umbrella contract period

Do **not** look only at the agreement year and conclude labor can be entered anytime. The practical planning anchor is still the request-level delivery/work window.

## Planning Heuristics

- if the request window closes this week, log the required hours this week
- if the window remains open next week, splitting is allowed
- if a dispatch has a nominal budget like `1 Day = 8h` or `3 Day = 24h`, treat that as the primary envelope
- avoid exceeding nominal budget except for a tiny operational tolerance you have already validated in your environment

## Late Entry Heuristic

A durable rule extracted from practice:

- labor does not have to be entered on the exact delivery day
- a usable operating rule is: finish entry by about **window end + roughly 2 months**

Treat this as an operational heuristic, not a product guarantee. Re-validate in your own org if the policy matters.

## Monthly FIX Buckets

Do not defer everything just because the window is open.

Usually these remain in the current month:

- monthly EDE allocations
- hours already explicitly received for the current month
- same-month dispatches that are treated as fixed internal commitments

Only defer work with real window slack.

## What To Store In Your Own Ledger

At minimum keep:

- assignment ID
- RMOT / ROSS / SCOP ID
- request end date
- nominal budget
- hours already logged
- whether this is a monthly fixed bucket or a movable bucket
