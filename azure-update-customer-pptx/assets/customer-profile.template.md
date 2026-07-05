# Customer Profile

Fill this file for each customer workspace. Do not store customer-specific values in skill references.

## Identity

| Field                    | Value                                           |
| ------------------------ | ----------------------------------------------- |
| Customer name            | `<customer>`                                    |
| System name              | `<system>`                                      |
| Output filename pattern  | `Customer-System_AzureUpdate_{year}{date}.pptx` |
| Template filename        | `azure-update-template.pptx`                    |
| Fiscal year for filename | `2026`                                          |

## Azure Environment

| Field         | Value                     |
| ------------- | ------------------------- |
| Tenant domain | `<tenant-domain>`         |
| Tenant id     | `<tenant-id>`             |
| Auth          | `az login -t <tenant-id>` |

The auth row is a reference value. Use the actual workspace authentication flow when it differs.

## Priority Keywords

SSOT: `.config/customer-keywords.json`.

- Fill services, SKUs, regions, and operational concerns that should bias updates toward Weekly.

## In-use SKU

| Bucket     | SKUs     |
| ---------- | -------- |
| In use     | `<fill>` |
| Monitor    | `<fill>` |
| Not in use | `<fill>` |

## Exclude Keywords

SSOT: `.config/exclude-keywords.json`.

- Fill services that are unused or should usually go to Appendix.

