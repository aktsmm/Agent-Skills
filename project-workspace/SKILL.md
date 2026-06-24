---
name: project-workspace
description: "Create and manage topic-specific project workspace folders for validation, investigation, PoC, comparison, or workstream projects. Use when creating/opening a project workspace, validation folder, topic-specific work folder, or cost comparison workspace. Triggers on project workspace, プロジェクトワークスペース, 検証フォルダ, PoC ワークスペース, トピック別作業フォルダ."
argument-hint: "作成したいプロジェクト名や検証テーマ"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Project Workspace Skill

Use this skill when the user asks to create, open, prepare, or organize a project/workspace folder for a validation, investigation, PoC, topic-specific workstream, comparison, or similar Clawpilot project.

## Default location

- Use the user's configured Clawpilot project root as the default root for project-specific folders.
- In local installs, this root is commonly a dedicated non-OneDrive project workspace. Treat the concrete local path as environment-specific configuration, not portable skill content.
- Do not create new project folders under the chat/workspace document folder unless the user explicitly asks for that location.
- Use Windows-style paths with backslashes.

## Folder naming

- Prefer concise kebab-case English folder names, for example:
  - `azure-monitor-workspace-validation`
  - `joule-validation`
  - `customer-meeting-prep`
- If the user provides a Japanese or informal topic name, convert it to a clear English folder slug.
- If a folder already exists, reuse it instead of creating a duplicate. If the requested name is ambiguous or would collide with an unrelated folder, ask before proceeding.

## Creation flow

1. Determine the intended project topic and folder slug.
2. Create the folder under the configured Clawpilot project root.
3. Default to creating a lightweight project package, not just an empty folder, when the request is for validation, investigation, PoC, comparison, customer explanation, screenshot collection, or when the user asks for viewpoints/criteria.
4. If the user explicitly asks for only a folder, create the folder only and report the path.
5. For large moves, renames, or destructive cleanup, follow dry-run -> confirmation -> execution.

## Default project package

When creating a validation, investigation, PoC, or comparison workspace, create these artifacts by default unless the user asks otherwise:

```text
README.md
validation-plan.md
notes\findings.md
screenshots\README.md
screenshots\01-source-or-baseline
screenshots\02-validation
screenshots\03-customer-story
exports
```

Adapt folder names to the topic when obvious. For example, a two-product comparison can use product-specific screenshot folders plus a comparison/customer-story folder.

If the user mentions cost, pricing, TCO, FinOps, billing, or comparing the cost of multiple options, also create `cost-comparison.md` with assumptions, measured usage, unit prices, formulas, screenshots/evidence, and final comparison notes.

## Validation plan quality bar

`validation-plan.md` should be useful immediately, even before the user provides detailed requirements. Include:

- Purpose and expected output.
- Key questions or hypotheses to validate.
- Scope and explicit non-goals.
- Environment and prerequisites to prepare.
- Step-by-step validation scenarios.
- Evidence plan, including screenshot targets and naming convention.
- Comparison or decision criteria when there are multiple options.
- Customer value story: what benefit the customer should understand from the validation.
- Actual measurement scenarios for claims that require evidence. Do not stop at conceptual comparison when the user asks to "actually compare", "verify", "measure", or "cost compare".
- Risks, caveats, and open questions.
- Official references for Microsoft/Azure topics.

For Microsoft/Azure topics, verify important product facts with official Microsoft Learn, Azure pricing, or other Microsoft official sources before writing them into the artifact, and include source URLs.

## Cost comparison plans

When the task includes cost comparison, the plan must define how cost will be measured or estimated, not only list pricing pages. Include:

- The comparable workload or scenario.
- What data each option actually stores or processes. If the services are not same-data alternatives, state that explicitly.
- Usage drivers and units for each option, such as GB ingested, GB retained, metric samples, time series, queries, exports, or add-on services.
- Baseline unit prices from official pricing sources or Azure Retail Prices API, with region, currency, and retrieval date.
- Test runs that separate baseline, high-volume, and high-cardinality or high-retention cases where relevant.
- Formulas for converting measured usage into daily/monthly estimates.
- Evidence to collect, such as Cost Management screenshots, usage queries, pricing calculator/API output, and portal screenshots.
- A note that actual billing can lag and should be reconciled with Cost Management after charges are reflected.

For Azure Monitor workspace versus Log Analytics workspace specifically, do not frame the comparison as putting identical data into both. Use the same monitored workload, send logs to Log Analytics workspace and Prometheus metrics to Azure Monitor workspace, then compare the actual cost drivers: log ingestion/retention for Log Analytics workspace versus metric samples/cardinality/query behavior for Azure Monitor workspace.

## Reporting

- Report the final path first.
- Mention if an existing folder was reused.
- Keep the response concise in Japanese.

## Guardrails

- Do not move or delete existing files unless explicitly requested or needed to fix a mistaken placement made in the current task.
- Do not store secrets or credentials in project files.
- Do not store user-machine-specific absolute paths in this private repo skill; keep those in local configuration or local installed skill copies.
- For Microsoft/Azure validation plans, verify important facts with official Microsoft Learn/Azure pricing information and include source URLs in artifacts when applicable.
