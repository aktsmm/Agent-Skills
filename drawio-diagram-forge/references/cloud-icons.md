# Cloud Icons Reference

## ⚠️ Critical: Azure Icon Format

**VS Code Draw.io Integration では `mxgraph.azure.*` 形式が正しく表示されない。**

必ず `img/lib/azure2/**/*.svg` 形式を使用すること。

| 形式                            | Web 版 | VS Code 版  | 推奨 |
| ------------------------------- | ------ | ----------- | ---- |
| `shape=mxgraph.azure.*`         | ✅     | ❌ 青い四角 | ❌   |
| `image=img/lib/azure2/**/*.svg` | ✅     | ✅          | ✅   |

## 🔧 Initial Setup (Required)

Azure/AWS アイコンを使うには、**事前にシェイプライブラリを有効化**する必要がある。

### 手順

1. `.drawio` ファイルを VS Code で開く
2. 左下の **「+ その他の図形」** (+ More Shapes) をクリック
3. **「図形」ダイアログ**が開く
4. 「ネットワーク」カテゴリで以下にチェック：
   - ✅ **Azure** - Azure アイコン
   - ✅ **AWS17** / **AWS18** / **AWS 2026** - AWS アイコン（用途に応じて）
   - ✅ **AWS 3D** - 3D 表現が必要な場合
5. **「設定を保存」** にチェック（次回以降も有効）
6. **「適用」** をクリック

### 推奨設定

| ライブラリ | 用途                     | 推奨    |
| ---------- | ------------------------ | ------- |
| Azure      | Azure サービスアイコン   | ✅ 必須 |
| AWS 2026   | 最新 AWS アイコン        | ✅ 推奨 |
| AWS18      | AWS アイコン（安定版）   | ⚪ 任意 |
| AWS17      | AWS アイコン（レガシー） | ⚪ 任意 |
| AWS 3D     | 3D アイコン              | ⚪ 任意 |

> **Note**: 設定は `.drawio` ファイルごとではなく、VS Code 全体で保存される。一度設定すれば他のファイルでも有効。

## Azure Icons (Azure2 形式)

### Common Azure Icons

| Service              | SVG Path                                                            | Category              |
| -------------------- | ------------------------------------------------------------------- | --------------------- |
| **Compute**          |                                                                     |                       |
| Virtual Machine      | `img/lib/azure2/compute/Virtual_Machine.svg`                        | compute               |
| VM Scale Sets        | `img/lib/azure2/compute/VM_Scale_Sets.svg`                          | compute               |
| App Service          | `img/lib/azure2/compute/App_Services.svg`                           | compute               |
| Function Apps        | `img/lib/azure2/compute/Function_Apps.svg`                          | compute               |
| AKS                  | `img/lib/azure2/compute/Azure_Kubernetes_Service.svg`               | compute               |
| Container Instances  | `img/lib/azure2/compute/Container_Instances.svg`                    | compute               |
| Disks                | `img/lib/azure2/compute/Disks.svg`                                  | compute               |
| Batch Accounts       | `img/lib/azure2/compute/Batch_Accounts.svg`                         | compute               |
| **Containers**       |                                                                     |                       |
| Container Registry   | `img/lib/azure2/containers/Container_Registries.svg`                | containers            |
| Red Hat OpenShift    | `img/lib/azure2/containers/Azure_Red_Hat_OpenShift.svg`             | containers            |
| Service Fabric       | `img/lib/azure2/containers/Service_Fabric_Clusters.svg`             | containers            |
| **Storage**          |                                                                     |                       |
| Storage Account      | `img/lib/azure2/storage/Storage_Accounts.svg`                       | storage               |
| **Databases**        |                                                                     |                       |
| SQL Database         | `img/lib/azure2/databases/SQL_Database.svg`                         | databases             |
| SQL Managed Instance | `img/lib/azure2/databases/SQL_Managed_Instance.svg`                 | databases             |
| Cosmos DB            | `img/lib/azure2/databases/Azure_Cosmos_DB.svg`                      | databases             |
| Redis Cache          | `img/lib/azure2/databases/Cache_Redis.svg`                          | databases             |
| MySQL                | `img/lib/azure2/databases/Azure_Database_MySQL_Server.svg`          | databases             |
| PostgreSQL           | `img/lib/azure2/databases/Azure_Database_PostgreSQL_Server.svg`     | databases             |
| Data Factory         | `img/lib/azure2/databases/Data_Factory.svg`                         | databases             |
| Synapse Analytics    | `img/lib/azure2/databases/Azure_Synapse_Analytics.svg`              | databases             |
| Data Explorer        | `img/lib/azure2/databases/Azure_Data_Explorer_Clusters.svg`         | databases             |
| **Networking**       |                                                                     |                       |
| Virtual Network      | `img/lib/azure2/networking/Virtual_Networks.svg`                    | networking            |
| Subnet               | `img/lib/azure2/networking/Subnet.svg`                              | networking            |
| Load Balancer        | `img/lib/azure2/networking/Load_Balancers.svg`                      | networking            |
| Application Gateway  | `img/lib/azure2/networking/Application_Gateways.svg`                | networking            |
| Front Door           | `img/lib/azure2/networking/Front_Doors.svg`                         | networking            |
| ExpressRoute         | `img/lib/azure2/networking/ExpressRoute_Circuits.svg`               | networking            |
| VPN Gateway          | `img/lib/azure2/networking/Virtual_Network_Gateways.svg`            | networking            |
| Firewall             | `img/lib/azure2/networking/Firewalls.svg`                           | networking            |
| Bastion              | `img/lib/azure2/networking/Bastions.svg`                            | networking            |
| Private Endpoint     | `img/lib/azure2/networking/Private_Endpoint.svg`                    | networking            |
| Private Link         | `img/lib/azure2/networking/Private_Link.svg`                        | networking            |
| NSG                  | `img/lib/azure2/networking/Network_Security_Groups.svg`             | networking            |
| DNS Zone             | `img/lib/azure2/networking/DNS_Zones.svg`                           | networking            |
| Virtual WAN          | `img/lib/azure2/networking/Virtual_WANs.svg`                        | networking            |
| Virtual WAN Hub      | `img/lib/azure2/networking/Virtual_WAN_Hub.svg`                     | networking            |
| Traffic Manager      | `img/lib/azure2/networking/Traffic_Manager_Profiles.svg`            | networking            |
| NAT Gateway          | `img/lib/azure2/networking/NAT.svg`                                 | networking            |
| **Security**         |                                                                     |                       |
| Key Vault            | `img/lib/azure2/security/Key_Vaults.svg`                            | security              |
| Defender             | `img/lib/azure2/security/Azure_Defender.svg`                        | security              |
| Sentinel             | `img/lib/azure2/security/Azure_Sentinel.svg`                        | security              |
| Security Center      | `img/lib/azure2/security/Security_Center.svg`                       | security              |
| **Identity**         |                                                                     |                       |
| Azure AD / Entra ID  | `img/lib/azure2/identity/Azure_Active_Directory.svg`                | identity              |
| **Integration**      |                                                                     |                       |
| API Management       | `img/lib/azure2/integration/API_Management_Services.svg`            | integration           |
| Logic Apps           | `img/lib/azure2/integration/Logic_Apps.svg`                         | integration           |
| Service Bus          | `img/lib/azure2/integration/Service_Bus.svg`                        | integration           |
| **Analytics**        |                                                                     |                       |
| Event Hubs           | `img/lib/azure2/analytics/Event_Hubs.svg`                           | analytics             |
| Databricks           | `img/lib/azure2/analytics/Azure_Databricks.svg`                     | analytics             |
| Stream Analytics     | `img/lib/azure2/analytics/Stream_Analytics_Jobs.svg`                | analytics             |
| HDInsight            | `img/lib/azure2/analytics/HD_Insight_Clusters.svg`                  | analytics             |
| Power BI Embedded    | `img/lib/azure2/analytics/Power_BI_Embedded.svg`                    | analytics             |
| **AI / ML**          |                                                                     |                       |
| Azure OpenAI         | `img/lib/azure2/ai_machine_learning/Azure_OpenAI.svg`               | ai_machine_learning   |
| Cognitive Services   | `img/lib/azure2/ai_machine_learning/Cognitive_Services.svg`         | ai_machine_learning   |
| Machine Learning     | `img/lib/azure2/ai_machine_learning/Machine_Learning.svg`           | ai_machine_learning   |
| Bot Services         | `img/lib/azure2/ai_machine_learning/Bot_Services.svg`               | ai_machine_learning   |
| AI Studio            | `img/lib/azure2/ai_machine_learning/AI_Studio.svg`                  | ai_machine_learning   |
| Speech Services      | `img/lib/azure2/ai_machine_learning/Speech_Services.svg`            | ai_machine_learning   |
| Computer Vision      | `img/lib/azure2/ai_machine_learning/Computer_Vision.svg`            | ai_machine_learning   |
| Form Recognizer      | `img/lib/azure2/ai_machine_learning/Form_Recognizers.svg`           | ai_machine_learning   |
| **IoT**              |                                                                     |                       |
| IoT Hub              | `img/lib/azure2/iot/IoT_Hub.svg`                                    | iot                   |
| IoT Central          | `img/lib/azure2/iot/IoT_Central_Applications.svg`                   | iot                   |
| IoT Edge             | `img/lib/azure2/iot/IoT_Edge.svg`                                   | iot                   |
| Digital Twins        | `img/lib/azure2/iot/Digital_Twins.svg`                              | iot                   |
| **DevOps**           |                                                                     |                       |
| Azure DevOps         | `img/lib/azure2/devops/Azure_DevOps.svg`                            | devops                |
| DevTest Labs         | `img/lib/azure2/devops/DevTest_Labs.svg`                            | devops                |
| **Management**       |                                                                     |                       |
| Monitor              | `img/lib/azure2/management_governance/Monitor.svg`                  | management_governance |
| Log Analytics        | `img/lib/azure2/management_governance/Log_Analytics_Workspaces.svg` | management_governance |
| Backup (Recovery)    | `img/lib/azure2/management_governance/Recovery_Services_Vaults.svg` | management_governance |
| Application Insights | `img/lib/azure2/management_governance/Application_Insights.svg`     | management_governance |
| Policy               | `img/lib/azure2/management_governance/Policy.svg`                   | management_governance |
| Automation           | `img/lib/azure2/management_governance/Automation_Accounts.svg`      | management_governance |
| Azure Arc            | `img/lib/azure2/management_governance/Azure_Arc.svg`                | management_governance |
| Cost Management      | `img/lib/azure2/management_governance/Cost_Management_and_Billing.svg` | management_governance |

### Azure Icon Style (✅ Correct)

```xml
<mxCell id="vm1" value="VM-01"
        style="aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Virtual_Machine.svg;verticalLabelPosition=bottom;verticalAlign=top;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="68" height="68" as="geometry"/>
</mxCell>
```

### Azure2 Library Structure

```
img/lib/azure2/
├── ai_machine_learning/    # Azure ML, Cognitive Services
├── analytics/              # Synapse, Event Hubs
├── compute/                # VM, App Service, Functions, AKS
├── containers/             # Container Instances
├── databases/              # SQL, Cosmos DB, Redis
├── devops/                 # Azure DevOps
├── identity/               # Azure AD / Entra ID
├── integration/            # API Management, Logic Apps, Service Bus
├── iot/                    # IoT Hub
├── management_governance/  # Monitor, Log Analytics, Recovery Services, Policy
├── networking/             # VNet, Load Balancer, Front Door, VPN (Virtual_Network_Gateways)
├── security/               # Key Vault, Defender, Sentinel
├── storage/                # Storage Accounts, Data Lake
└── web/                    # App Service Plans
```

### ⚠️ Common Mistakes (Verified against GitHub)

| サービス        | ❌ 間違いやすいパス          | ✅ 正しいパス                                          |
| --------------- | ---------------------------- | ------------------------------------------------------ |
| VPN Gateway     | `VPN_Gateway.svg`            | `Virtual_Network_Gateways.svg`                         |
| Azure Monitor   | `Azure_Monitor.svg`          | `Monitor.svg`                                          |
| App Gateway     | `Application_Gateway.svg`    | `Application_Gateways.svg` (複数形)                    |
| Backup          | `Backup.svg`                 | `Recovery_Services_Vaults.svg`                         |

## AWS Icons (AWS4 形式)

### Setup

1. Open `.drawio` file in VS Code
2. Click **"+ More Shapes"** (bottom-left)
3. Check **AWS**
4. Click **Apply**

### Common AWS Icons

| Service     | resIcon Value                                     | Category    |
| ----------- | ------------------------------------------------- | ----------- |
| EC2         | `mxgraph.aws4.ec2`                                | Compute     |
| Lambda      | `mxgraph.aws4.lambda`                             | Compute     |
| ECS         | `mxgraph.aws4.ecs`                                | Containers  |
| EKS         | `mxgraph.aws4.eks`                                | Containers  |
| S3          | `mxgraph.aws4.s3`                                 | Storage     |
| RDS         | `mxgraph.aws4.rds`                                | Database    |
| DynamoDB    | `mxgraph.aws4.dynamodb`                           | Database    |
| VPC         | `mxgraph.aws4.vpc`                                | Networking  |
| ELB         | `mxgraph.aws4.elastic_load_balancing`             | Networking  |
| CloudFront  | `mxgraph.aws4.cloudfront`                         | Networking  |
| Route 53    | `mxgraph.aws4.route_53`                           | Networking  |
| IAM         | `mxgraph.aws4.identity_and_access_management_iam` | Security    |
| API Gateway | `mxgraph.aws4.api_gateway`                        | Integration |

### AWS Icon Style

```xml
<mxCell id="ec2" value="EC2"
        style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#ffffff;fillColor=#232F3E;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="50" height="50" as="geometry"/>
</mxCell>
```

## Style Comparison

| Attribute   | Azure2 (✅)               | AWS4                        | Azure 旧形式 (❌) |
| ----------- | ------------------------- | --------------------------- | ----------------- |
| `shape`     | 不要                      | `mxgraph.aws4.resourceIcon` | `mxgraph.azure.*` |
| `image`     | `img/lib/azure2/**/*.svg` | 不要                        | 不要              |
| `resIcon`   | 不要                      | `mxgraph.aws4.*`            | 不要              |
| `aspect`    | `fixed`                   | `fixed`                     | なし              |
| `fillColor` | 不要（SVG 内）            | `#232F3E`                   | 指定必要          |

## Best Practices

1. **Azure は必ず `img/lib/azure2/` 形式を使用**
2. **Consistency**: Use icons from the same provider in one diagram
3. **Labeling**: Always add text labels below icons
4. **Sizing**: Keep icon sizes consistent (68x68 for Azure, 50x50 for AWS)
5. **Grouping**: Use containers/swimlanes to group related services

## Validation Checklist

生成後に確認：

- [ ] Azure アイコンが `img/lib/azure2/` パスを使用している
- [ ] `shape=mxgraph.azure.*` が含まれて**いない**
- [ ] VS Code Draw.io Integration で正しく表示される

## Icon Detection Keywords

When the input mentions these keywords, use corresponding cloud icons:

### Azure Keywords

- `Azure`, `Microsoft Cloud`
- `VM`, `Virtual Machine` (in Azure context)
- `App Service`, `Function App`, `Logic App`
- `VNET`, `Virtual Network`
- `AAD`, `Azure AD`, `Entra ID`

### AWS Keywords

- `AWS`, `Amazon Web Services`
- `EC2`, `Lambda`, `ECS`, `EKS`
- `S3`, `RDS`, `DynamoDB`
- `VPC`, `CloudFront`, `Route 53`

## Reference

- [Draw.io Azure2 Icons](https://github.com/jgraph/drawio/tree/dev/src/main/webapp/img/lib/azure2)
- [Draw.io AWS4 Icons](https://github.com/jgraph/drawio/tree/dev/src/main/webapp/img/lib/aws4)

## AWS → Azure Migration Patterns

AWS 図を Azure 化する際のサービス対応表：

| AWS Service          | Azure Equivalent        | Azure Icon Path                                             |
| -------------------- | ----------------------- | ----------------------------------------------------------- |
| VPC                  | Virtual Network         | `img/lib/azure2/networking/Virtual_Networks.svg`            |
| Subnet               | Subnet                  | `img/lib/azure2/networking/Subnet.svg`                      |
| EC2                  | Virtual Machine         | `img/lib/azure2/compute/Virtual_Machine.svg`                |
| RDS                  | Azure SQL / Cosmos DB   | `img/lib/azure2/databases/SQL_Database.svg`                 |
| S3                   | Storage Account (Blob)  | `img/lib/azure2/storage/Storage_Accounts.svg`               |
| Lambda               | Function Apps           | `img/lib/azure2/compute/Function_Apps.svg`                  |
| EKS                  | AKS                     | `img/lib/azure2/compute/Azure_Kubernetes_Service.svg`       |
| ALB/NLB              | Load Balancer           | `img/lib/azure2/networking/Load_Balancers.svg`              |
| CloudFront           | Front Door / CDN        | `img/lib/azure2/networking/Front_Doors.svg`                 |
| Route 53             | Azure DNS               | `img/lib/azure2/networking/DNS_Zones.svg`                   |
| Network Firewall     | Azure Firewall          | `img/lib/azure2/networking/Firewalls.svg`                   |
| NAT Gateway          | Azure Firewall (SNAT)   | Azure Firewall に統合可能                                   |
| VPC Endpoint         | Private Endpoint        | `img/lib/azure2/networking/Private_Endpoint.svg`            |
| Service Endpoint     | Private Endpoint        | `img/lib/azure2/networking/Private_Endpoint.svg`            |
| Transit Gateway      | Virtual WAN Hub         | `img/lib/azure2/networking/Virtual_WAN_Hub.svg`             |
| Direct Connect       | ExpressRoute            | `img/lib/azure2/networking/ExpressRoute_Circuits.svg`       |
| Site-to-Site VPN     | VPN Gateway             | `img/lib/azure2/networking/Virtual_Network_Gateways.svg`    |
| IAM                  | Azure AD / Entra ID     | `img/lib/azure2/identity/Azure_Active_Directory.svg`        |
| KMS                  | Key Vault               | `img/lib/azure2/security/Key_Vaults.svg`                    |
| CloudWatch           | Azure Monitor           | `img/lib/azure2/management_governance/Monitor.svg`          |
| GuardDuty            | Defender / Sentinel     | `img/lib/azure2/security/Azure_Defender.svg`                |

### Migration Tips

1. **NAT Gateway → Azure Firewall**: Azure では Firewall が SNAT 機能を持つため、NAT Gateway を別途配置せず Firewall 直結構成が可能
2. **Service Endpoint → Private Endpoint**: Azure では Private Endpoint が推奨。より安全なプライベート接続を提供
3. **形式変換**: `mxgraph.aws4.*` や `mxgraph.azure.*` は `img/lib/azure2/**/*.svg` 形式に置換

### Conversion Commands

```bash
# sed での一括置換例（旧形式 → 新形式は手動対応推奨）
sed -i 's/mxgraph\.azure3\./mxgraph.azure./g' diagram.drawio
```

```python
# ID重複チェック（編集時に発生しやすい）
import re, collections, pathlib
p = pathlib.Path('diagram.drawio')
text = p.read_text(encoding='utf-8')
ids = re.findall(r'\bid="([^"]+)"', text)
ctr = collections.Counter(ids)
dups = [i for i,c in ctr.items() if c > 1]
if dups:
    print(f'⚠️ Duplicate IDs: {dups}')
```

## Azure Architecture Patterns

### Hub-Spoke Topology Icons

典型的な Hub-Spoke アーキテクチャで使用するアイコン：

| Layer             | Components                                    | Icons                                              |
| ----------------- | --------------------------------------------- | -------------------------------------------------- |
| On-Premises       | Users, AD, Servers                            | 汎用アイコン or カスタム                           |
| Hybrid Connection | ExpressRoute, VPN Gateway                     | `ExpressRoute_Circuits.svg`, `Virtual_Network_Gateways.svg` |
| Hub VNet          | Firewall, Bastion, DNS, Key Vault             | `Firewalls.svg`, `Bastions.svg`, `DNS_Zones.svg`, `Key_Vaults.svg` |
| Hub Services      | Monitor, Backup, Defender                     | `Monitor.svg`, `Recovery_Services_Vaults.svg`, `Azure_Defender.svg` |
| Spoke VNets       | Production, Development, Shared Services      | `Virtual_Networks.svg` + ラベルで区別              |

### Example: Hub VNet Components

```xml
<!-- Firewall -->
<mxCell value="Azure Firewall"
        style="aspect=fixed;image=img/lib/azure2/networking/Firewalls.svg;..."
        .../>

<!-- Bastion -->
<mxCell value="Bastion"
        style="aspect=fixed;image=img/lib/azure2/networking/Bastions.svg;..."
        .../>

<!-- Monitor -->
<mxCell value="Azure Monitor"
        style="aspect=fixed;image=img/lib/azure2/management_governance/Monitor.svg;..."
        .../>

<!-- Backup (Recovery Services) -->
<mxCell value="Backup"
        style="aspect=fixed;image=img/lib/azure2/management_governance/Recovery_Services_Vaults.svg;..."
        .../>
```
