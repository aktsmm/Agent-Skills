# Low-cost Azure operations demo patterns

Use these patterns when building demo environments for Azure operations, RCA, alert response, or assistant-driven investigation. Prefer cheap, disposable resources and explicit manual setup artifacts over assuming everything can be automated by CLI.

## Design defaults

- Start with **1 demo resource group + 1 minimal app + 1-2 alerts + short-retention logs**.
- Prefer Azure Container Apps Consumption for low-cost app demos, especially when App Service plan creation fails because regional or subscription VM quota is unavailable.
- Avoid always-on VMs, AKS, and always-on databases unless the demo specifically requires runtime compute.
- Tag demo resource groups and resources with `purpose`, `costProfile`, `owner`, and `demo` so cleanup is obvious.
- Keep Log Analytics retention short and avoid verbose logs or high-frequency alert rules.

## App hosting choice

| Constraint | Preferred pattern |
| --- | --- |
| Lowest idle cost | Container Apps Consumption with `minReplicas: 0` and `maxReplicas: 1` |
| App Service quota error such as `Current Limit (Total VMs): 0` | Switch to Container Apps Consumption instead of retrying regions repeatedly |
| Stable enterprise web app demo | App Service if quota and plan cost are acceptable |
| Kubernetes-specific demo | AKS only when Kubernetes behavior is the point |

## Operations demo scenarios

- **App RCA**: make the app return HTTP 500 and emit a distinctive log string so logs, metrics, configuration, and recent changes can be correlated.
- **Control-plane network issue**: reproduce path problems without VMs by using NSG deny rules, a UDR with a missing NVA next hop, orphan Private DNS records, or missing Private DNS VNet links.
- **Alert response**: create only 1-2 Azure Monitor alerts and scope response flows to the demo resource group, alert name, and severity.
- **Review-mode remediation**: start with Reader or review/approval mode. Use autonomous remediation only for verified non-production actions.
- **Knowledge / runbook**: include known failures, expected root causes, safe mitigations, and escalation text as reusable Markdown.

## Portal and connector work

If the workflow involves portal-only configuration, OAuth, admin consent, Teams, Outlook, incident platform connectors, or managed agent setup, do not claim CLI-only completion. Produce setup artifacts instead:

- `setup-portal.md`: portal steps, consent points, resource scopes, and manual verification
- `prompts.md`: prompts for resource discovery, RCA, network analysis, daily Teams summary, and weekly Outlook summary
- `demo-commands.ps1`: traffic generation, failure-mode toggles, and cleanup commands
- `deployment-result.json`: resource names, endpoints, active failure mode, and cleanup hints

For outbound Teams or Outlook demos, avoid forwarding raw alerts. Send a summarized RCA with impact, evidence, and recommended action.

## Done criteria

- [ ] Cost-driving always-on resources are justified or avoided
- [ ] App hosting choice accounts for quota and idle cost
- [ ] Manual portal / OAuth / consent steps are captured when automation is not reliable
- [ ] Demo failure modes are reversible and cleanup is documented
- [ ] Microsoft Learn or pricing references are captured in final deliverables when claims depend on current product behavior
