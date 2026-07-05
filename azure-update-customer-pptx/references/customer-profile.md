# Customer Profile (fill per customer)

Abstract field guide. **Keep this file customer-neutral.** Put the actual values for one customer in
`assets/customer-profile.template.md` (copy + fill). Routing keywords live in
`.config/customer-keywords.json` (start from `assets/customer-keywords.template.json`) and
`.config/exclude-keywords.json`.

Source: consolidated from the repo's customer-keyword routing and customer Azure-access instructions.

## What a customer profile defines

Weekly slide routing: an update goes to **Weekly New Topics** if it matches a priority keyword and is
not excluded; otherwise it goes to **Appendix** (hidden). Default = Weekly; only an explicit exclude
match drops it to Appendix, after which AI makes the final call.

## Fields to fill

| Field                       | Meaning                                                                                                                                                                                                                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Customer name / system name | Used ONLY in output filename pattern + cover. Never in slide body text (use neutral "お客様").                                                                                                                                                                            |
| Priority keywords           | Services the customer uses. `Prepare-CustomerPptx.ps1` has built-in defaults; to override, place `.config/customer-keywords.json` (schema `priorityKeywords[keyword] = { Category, Priority }`, from `assets/customer-keywords.template.json`). Matching updates → Weekly. |
| Exclude keywords            | Services/areas the customer does NOT use → Appendix. Maintained in `.config/exclude-keywords.json`.                                                                                                                                                                        |
| In-use VM/AVS SKU list      | For the SKU-based retirement exception: VM/VMSS/AVS retirements go to Weekly only if the SKU is in use.                                                                                                                                                                   |
| Azure environment           | Tenant id, subscription ids, and how to verify region/SKU (e.g. `az` queries). Used by region review, not embedded in slides.                                                                                                                                             |

## Category SSOT (classification.json `category`)

Generic across customers. Do not add 廃止 as a category (it duplicates the 【廃止】 label).

| Category                     | Example services                                   |
| ---------------------------- | -------------------------------------------------- |
| インフラ基盤                 | VM, VMSS, ディスク, イメージ, SQL VM               |
| ネットワーク                 | VNet, ExpressRoute, Firewall, Load Balancer, NSG   |
| ストレージ                   | Storage Account, Azure NetApp Files, Blob          |
| バックアップ・災害復旧       | Recovery Services, Azure Backup, Site Recovery     |
| セキュリティ・ID             | Key Vault, Managed Identity, Defender              |
| 監視・運用                   | Azure Monitor, Log Analytics, Application Insights |
| ハイブリッド・マルチクラウド | Azure Arc                                          |
| アプリケーション基盤         | App Service, Logic Apps, Automation                |
| AI・ML                       | Azure AI, Azure OpenAI, Machine Learning           |
| その他                       | none of the above                                  |

## Routing rules (generic)

1. **Breaking / 廃止 is top priority** → Weekly, except an unused-service retirement that matches an exclude rule.
2. **Microsoft focus areas** (SRE Agent, AI Agent, Copilot) → Weekly.
3. **In-use services** (priority keyword match) → Weekly.
4. **Exclude keyword match** → Appendix.
5. **Hard to decide** → Weekly, let AI judge (verify with Azure Updates MCP).

### SKU-based retirement exception

VM / VMSS / AVS retirement → Weekly **only if the SKU is in the in-use list**. Unused SKUs → Appendix.
SKU-agnostic VM common changes (outbound access, Managed Disk, VMSS common spec) are NOT subject to this
exception — if the service is in use, Weekly is fine. Verify AVS SKU via `Microsoft.AVS/privateClouds`
cluster `sku.name`, not `az vm list`.

### Unused-service retirement exception

Even Breaking/廃止 may go to Appendix when the customer does not use the service (e.g. PaaS Azure SQL
elastic features, Front Door / CDN). Exception: `SQL VM` / `SQL Server on VM` is IaaS → never Appendix.
If usage is unconfirmed, keep it in Weekly and let AI judge.

## Two SSOTs to keep in sync

- `.config/exclude-keywords.json` is the SCRIPT source of truth for exclusions.
- The customer profile's exclude list is the human-readable companion. Update **both** together.

