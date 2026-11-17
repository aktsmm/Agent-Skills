# Reading Responses (read-only)

Use to read the results of a form you own: counts, averages, distributions and free-text themes. Everything here is read-only: no editing, no test submissions.

## Pick the source in this order

1. **The Forms aggregate view** (owner account, `analysis=true`) for headline counts and per-question summaries.
2. **The raw responses API from the page session** when the form is shared across audiences, needs filtering, or free text must be grouped.
3. **A synced results workbook** only after checking it is current. A local OneDrive copy can be a stale snapshot (compare its row count and last-write time with the response count on the aggregate view). A sensitivity-labelled workbook starts with the bytes `D0 CF`; open it read-only with Excel COM from the interpreter that has `pywin32`, dump the rows to a temporary file, close without saving, quit Excel, and delete the dump after use.

## Open the owner view

- A short response URL redirects to the response page; its `id=` query value is the form id.
- Open `https://forms.cloud.microsoft/Pages/DesignPageV2.aspx?origin=NeoPortalPage&subpage=design&id=<id>&analysis=true` in an owned Edge window (own port, throwaway profile). If the owner account is signed in through the Windows-connected account it opens without a prompt; otherwise stop and ask the user to finish sign-in.
- `document.body.innerText` of that page gives every question with counts or averages. Multi-select answers are counted per option.

## Raw rows from the page session

Run in the page context (Playwright `evaluate`). Take `<tenant>` and `<user>` from the `formapi` requests in the page's network log.

```js
const base = "/formapi/api/<tenant>/users/<user>/forms('<id>')";
const form = await (await fetch(base + "?$expand=questions($expand=choices)", {credentials: "include"})).json();
const list = (await (await fetch(base + "/responses?$top=200", {credentials: "include"})).json()).value;
// answers is a JSON string: [{questionId, answer1}]; multi-select answer1 is itself a JSON-encoded array
```

- Map answers by `questionId`. The API's question order is not the editor's order.
- Fields on each response include the submit date. Do not return names or emails to the model or to disk; the aggregate needs neither.

## Filtering and aggregating

1. List the distinct values of the organisation field with counts first (organisations are not personal data) and decide the match rules; spellings vary ("Company", "Company Holdings", an abbreviation).
2. Filter by organisation and submit date. Exclude test submissions (obvious dummy organisations or "test" in free text).
3. Compute counts, averages and distributions in the page or a script, not by hand; cross-check the total against the aggregate view.
4. Report aggregates and paraphrased themes. Do not quote individual answers or attribute them. State the respondent count and note when it is small.

## Cleanup

Stop the owned Edge window and delete its profile, delete your own browser-tool logs and any temporary dump or script, and make sure no Excel process is left behind.
