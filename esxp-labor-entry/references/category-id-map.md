# Category And Reason Map

These values were confirmed in one JST-based ESXP environment. They are practical defaults, not universal guarantees. If the API returns `inactive`, discover a live value from your own environment before mutating data.

## Non-Project Category IDs

| Category                                | laborCategoryId | Notes                                 |
| --------------------------------------- | --------------: | ------------------------------------- |
| Out of office                           |          982947 | good default for holidays and absence |
| Unified Presales                        |          368713 | pre-sales work                        |
| General Admin , Meetings & Events       |         1013309 | admin / meetings                      |
| Mentor/Community/ Practice Contribution |          368709 | community / mentoring                 |

## Categories That Need Verification In Your Environment

- Training & Accreditation Taken
- Vacation

If one of these is missing, create or inspect a draft in your own environment and read `laborCategoryId` from the captured record.

## Dispatch Category Naming

Use `Delivery`, not `(ISD only) Delivery`.

`(ISD only) Delivery` is a classic footgun that leads to rejected or unusable input.

## Late Submission Reason IDs

Common confirmed IDs from the source environment:

- `333177`
- `333185`

Do not brute-force reason IDs. Reuse IDs from known-good records or UI-confirmed values.

## Action Details Pattern

When a late reason is needed, the payload uses this shape:

```json
[
  {
    "actionType": "LateSubmission",
    "reasonId": 333185,
    "comments": "Late submission after correction"
  }
]
```

## Time Zone

`laborTimeZoneId = 87` in the confirmed JST environment.

Keep it configurable if you copy these scripts into a non-JST tenant.
