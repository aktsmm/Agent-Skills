# Azure Infra Validation Runbook

## Deployment Constraint Branches

- `VpnGw1-5 non-AZ not allowed`: switch to an AZ SKU such as `VpnGw1AZ`.
- `Public IPs must have zones configured`: recreate Standard Public IPs with zones.
- VNet overlap: reassign spoke address spaces.
- `useRemoteGateways` fails early: apply it only after the hub gateway is complete.
- MFA / tenant mismatch: switch tenant or re-login before deployment.

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

## Ready Rules

- Do not continue before `Succeeded`, `READY`, or `Connected` is observed.
- Prefer `scripts/watch-az-resource-state.ps1` or `scripts/check-vpn-lab-status.ps1` when available.
- Do not claim no outage from Activity Log alone; use polling, route, health, or metrics evidence.
