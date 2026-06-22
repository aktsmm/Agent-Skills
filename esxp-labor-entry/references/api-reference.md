# API Reference

ESXP labor の主要 API は core と draft の 2 系統です。認証ヘッダーは **live CDP session の Network.requestWillBeSent** から毎回取り直します。保存済み token や cookie を再利用しません。

## Host And Paths

- Host: `https://professionalservices.microsoft.com`
- Core labor: `/lmt-coreapi/api/v1/labor`
- Draft labor: `/lmt-draftapi/api/v1/draftLabor`

## Authentication Pattern

1. Edge を `--remote-debugging-port=<port> --remote-allow-origins=*` で起動する
2. ESXP Week View に手動ログインする
3. `scripts/verify_esxp_profile.py` で Home / sign-in / wrong profile でないことを確認する
4. `scripts/labor_api_tools.py` が CDP Network イベントから次のヘッダーを捕捉する

Typical headers:

- `Authorization`
- `Cookie`
- `Ocp-Apim-Subscription-Key`
- そのほか submitter API request に付いてくる request headers

## Read Operations

### Fetch core records for a week

```text
GET {HOST}/lmt-coreapi/api/v1/labor/submitter/{alias}?StartDate=YYYY-MM-DD&EndDate=YYYY-MM-DD
```

### Fetch draft records for a week

```text
GET {HOST}/lmt-draftapi/api/v1/draftLabor/submitter/{alias}?StartDate=YYYY-MM-DD&EndDate=YYYY-MM-DD
```

Portable command:

```powershell
python scripts/labor_api_tools.py fetch-week --start-date 2026-06-15 --end-date 2026-06-21 --format table
```

## Write Operations

### Add dispatch labor to core

```text
POST {HOST}/lmt-coreapi/api/v1/labor
```

Key fields:

- `laborDate`: `YYYY-MM-DDT00:00:00`
- `laborHours`: `HH:MM`
- `laborTimeZoneId`: `87` in JST environments
- `laborCategoryId`: default dispatch category is usually `Delivery`
- `laborCategoryName`
- `submittedFor`, `submittedBy`: user alias
- `partner`: often `axis`
- `assignmentDetails.assignmentId`
- `assignmentDetails.assignmentName`
- `assignmentDetails.customerName`
- `assignmentDetails.productName`
- `actionDetails[]`: optional LateSubmission metadata

Example payload:

```json
{
  "laborDate": "2026-05-18T00:00:00",
  "laborHours": "04:00",
  "laborTimeZoneId": 87,
  "laborCategoryId": 865418,
  "laborCategoryName": "Delivery",
  "submittedFor": "alias",
  "submittedBy": "alias",
  "laborNotes": "Delivery work",
  "partner": "axis",
  "assignmentDetails": {
    "assignmentId": 5206766,
    "assignmentName": "RMOT2026021305200000",
    "customerName": "Customer",
    "productName": "Technical Update Briefing - Azure"
  },
  "actionDetails": [
    {
      "actionType": "LateSubmission",
      "reasonId": 333177,
      "comments": "Late submission after correction"
    }
  ]
}
```

### Add dispatch labor to draft

```text
POST {HOST}/lmt-draftapi/api/v1/draftLabor
```

Important: **draft POST body must be an array**.

```json
[
  {
    "laborDate": "2026-05-18T00:00:00",
    "laborHours": "04:00"
  }
]
```

`{"bulkDraftLabor": [...]}` のような wrapper は 400 になります。

### Add non-project labor

`add-nonproject` は通常 core API に POST します。Payload は assignmentDetails を持たず、category ベースです。

Example payload:

```json
{
  "laborDate": "2026-05-04T00:00:00",
  "laborHours": "08:00",
  "laborTimeZoneId": 87,
  "laborCategoryId": 982947,
  "laborCategoryName": "Out of office",
  "submittedFor": "alias",
  "submittedBy": "alias",
  "laborNotes": "Japanese Holiday",
  "partner": "nonproject",
  "actionDetails": [
    {
      "actionType": "LateSubmission",
      "reasonId": 333185,
      "comments": "Late submission after correction"
    }
  ]
}
```

## Delete Operations

### Delete one core labor record

```text
PATCH {HOST}/lmt-coreapi/api/v1/labor/{laborId}/delete?userAlias={alias}
```

### Delete one draft labor record

```text
PATCH {HOST}/lmt-draftapi/api/v1/draftLabor/{laborId}/delete?userAlias={alias}
```

## Dedupe Model

Logical duplicate key:

- date
- hours
- laborCategoryName or laborCategoryId
- partner
- assignmentId for dispatch

Run `fetch-week` before mutation and compare the logical key before re-sending.

## Known API Behaviors

- Draft records may disappear from the draft endpoint after submit and return 404 on empty state.
- Non-project records can be successfully created while `fetch-week` still shows 404 or no matching rows. In that case, trust Week View summary instead of core/draft listing for NP verification.
- `add-dispatch` can need a dedupe bypass when single-day GET returns 404 but week-level fetch works. That is why the helper supports `--skip-dedupe`.
