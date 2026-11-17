# Azure Infra Validation Runbook

## Deployment Constraint Branches

- `VpnGw1-5 non-AZ not allowed`: switch to an AZ SKU such as `VpnGw1AZ` (non-AZ VpnGw1-5 creation is blocked since 2025-11-01; [SKU consolidation](https://learn.microsoft.com/azure/vpn-gateway/gateway-sku-consolidation)).
- `Public IPs must have zones configured`: recreate Standard Public IPs with zones.
- VNet overlap: reassign spoke address spaces.
- `useRemoteGateways` fails early: apply it only after the hub gateway is complete.
- On MFA-policy ARM denial, verify `aud` / `tid` and `amr` / `acrs` claims for that exact request without exposing the token; do not infer missing RBAC from another audience/tenant or bypass MFA.

## Phase Detail

1. Feasibility: write the validation goal in one line, decide whether Azure-only is enough, minimize topology, and set cleanup expectations.
2. Scope Fix: choose lab vs production, fix tenant/subscription, and define the target observation.
3. Official Grounding: verify prerequisites, limits, SKUs, and gaps against Microsoft Learn.
4. Preflight: run `az account show`, check provider registration, region availability, SKU/zone/RBAC, and decide polling evidence.
5. Baseline Build: create RG, hub/branch/spoke VNets, GatewaySubnet, and peering. Apply remote gateway after gateway readiness.
6. Core Deployment: create Public IPs, VPN Gateway / Route Server / NVA, and monitor long-running resources.
7. Connectivity: create VPN or peer connections and wait for `Connected`.
8. Baseline Capture: collect BGP peer status, learned routes, route table, prefix count, and observation start time.
9. Change: apply one setting change, capture Accepted/Succeeded/correlation ID, and wait for reconfiguration.
10. Compare: recapture routes/status, compare route count and summarization, and separate control-plane completion from route/metric impact.
11. Cleanup or Persist: delete one-shot labs or record why they remain.

## CLI and Lab Observations

- Do not merge stderr into JSON output (`2>&1`): CLI extensions print warnings that break `ConvertFrom-Json`. Redirect stderr to a temp file and read stdout only.
- Judge `az provider register` by an independent read-back (`az provider show` / `list`), not by its acceptance output. Separate `Registering` from `Registered`; if the acceptance output is unexpected, read back before resending.
- For SKU availability, read `restrictions` per region (`az vm list-skus --all`). `NotAvailableForSubscription` means pick another region or SKU; do not treat quota and restriction as the same thing.
- Run Command needs outbound connectivity to return results; a private subnet needs NAT or an equivalent egress path.
- To test host-based routing from inside a VNet, use `curl --resolve` with the URL host as SNI and a separate `-H "Host: ..."` to cross SNI and Host; trust a self-signed chain explicitly with `--cacert` and report that this differs from browser trust. Observed on an internal Container Apps environment: internal-only ingress returned HTTP 404 over HTTP and a TLS reset over HTTPS, and an unbound hostname got a TLS reset. With one wildcard certificate, the app that answered followed the HTTP Host (SNI picks the certificate, not the app; selection among several certificates was not tested). Adding a hostname already bound to another app in the same environment was rejected (`CustomDomainConflictOnEnvironment`) while both apps accepted traffic from anywhere, so it is not specific to restricted ingress. Treat these as observations, not documented behavior.
- Single observation: `az containerapp create --yaml` returned HTTP 400 while an ARM REST PUT with typed JSON succeeded. Try REST on a repeat failure; do not assume the cause.
- Retail Prices API: filter by exact product name (a VM series and a similarly named Cloud Services product differ in price), and record "unit price not retrievable" instead of estimating when a region has no result.

## Ready Rules

- Do not continue before `Succeeded`, `READY`, or `Connected` is observed.
- Prefer `scripts/watch-az-resource-state.ps1` or `scripts/check-vpn-lab-status.ps1` when available.
- Do not claim no outage from Activity Log alone; use polling, route, health, or metrics evidence.
