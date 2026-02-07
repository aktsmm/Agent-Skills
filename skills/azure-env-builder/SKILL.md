---
name: azure-env-builder
description: "[Alpha] Enterprise Azure environment builder. Deploy apps to App Service/AKS/Container Apps, generate Bicep with AVM modules, configure service connections and CI/CD. Use when building Azure infrastructure, deploying applications, or designing Hub-Spoke/AKS/AI Foundry architectures."
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Azure Environment Builder

Enterprise Azure environment builder skill.

## When to Use

- **Azure**, **Bicep**, **infrastructure**, **deploy app**
- Building enterprise Azure environments
- Deploying apps to App Service, AKS, or Container Apps
- Designing Hub-Spoke, AKS, or AI Foundry architectures

## Features

| Category       | Capabilities                       |
| -------------- | ---------------------------------- |
| Architecture   | Hub-Spoke, Web+DB, AKS, AI Foundry |
| AVM Modules    | 200+ Azure Verified Modules        |
| VM Init        | Squid, Nginx, Docker, IIS setup    |
| Config Linking | SQL/Storage/Redis, Managed ID RBAC |
| CI/CD          | GitHub Actions / Azure Pipelines   |

## Workflow

1. **Interview** - Gather requirements + select architecture pattern
2. **MCP Tools** - Fetch latest AVM/schema info
3. **Scaffold** - Generate environment folder via `scripts/scaffold_environment.ps1`
4. **Implement** - Write Bicep with AVM modules + VM init
5. **CI/CD** - Generate pipeline templates
6. **Deploy** - what-if → execute

## Required: MCP Tools

**Run before generating Bicep code:**

```
mcp_bicep_experim_get_bicep_best_practices
mcp_bicep_experim_list_avm_metadata
mcp_bicep_experim_get_az_resource_type_schema(azResourceType, apiVersion)
microsoft_docs_search(query: "Private Endpoint Bicep")
```

## Interview Checklist

→ **[references/hearing-checklist.md](references/hearing-checklist.md)**

| Item         | Details                 |
| ------------ | ----------------------- |
| Subscription | ID or `az account show` |
| Environment  | dev / staging / prod    |
| Region       | japaneast / japanwest   |
| Deploy Type  | Azure CLI / Bicep       |

## Architecture Patterns

→ **[references/architecture-patterns.md](references/architecture-patterns.md)**

| Pattern    | Use Case                       |
| ---------- | ------------------------------ |
| Hub-Spoke  | Large enterprise               |
| Web + DB   | Standard web applications      |
| AKS        | Container microservices        |
| AI Foundry | AI/ML workloads                |
| Proxy VM   | Private network egress control |

## Commands

```powershell
# Scaffold environment folder
pwsh scripts/scaffold_environment.ps1 -Environment <env> -Location <region>

# Validate
az deployment group what-if --resource-group <rg> --template-file main.bicep

# Deploy
az deployment group create --resource-group <rg> --template-file main.bicep
```

## Key References

| File                                                                  | Purpose                |
| --------------------------------------------------------------------- | ---------------------- |
| [architecture-patterns.md](references/architecture-patterns.md)       | Architecture patterns  |
| [avm-modules.md](references/avm-modules.md)                           | AVM module catalog     |
| [vm-app-scripts.md](references/vm-app-scripts.md)                     | VM init scripts        |
| [app-deploy-patterns.md](references/app-deploy-patterns.md)           | App deploy patterns    |
| [service-config-templates.md](references/service-config-templates.md) | Service config linking |
| [cicd-templates/](references/cicd-templates/)                         | CI/CD templates        |

## Done Criteria

- [ ] Interview checklist completed
- [ ] MCP tools fetched latest info
- [ ] Bicep files generated
- [ ] `az deployment group what-if` succeeded
