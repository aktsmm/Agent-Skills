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

| Service             | SVG Path                                                 | Category    |
| ------------------- | -------------------------------------------------------- | ----------- |
| Virtual Machine     | `img/lib/azure2/compute/Virtual_Machine.svg`             | compute     |
| App Service         | `img/lib/azure2/compute/App_Services.svg`                | compute     |
| Function Apps       | `img/lib/azure2/compute/Function_Apps.svg`               | compute     |
| AKS                 | `img/lib/azure2/compute/Azure_Kubernetes_Service.svg`    | compute     |
| Storage Account     | `img/lib/azure2/storage/Storage_Accounts.svg`            | storage     |
| SQL Database        | `img/lib/azure2/databases/SQL_Database.svg`              | databases   |
| Cosmos DB           | `img/lib/azure2/databases/Azure_Cosmos_DB.svg`           | databases   |
| Virtual Network     | `img/lib/azure2/networking/Virtual_Networks.svg`         | networking  |
| Load Balancer       | `img/lib/azure2/networking/Load_Balancers.svg`           | networking  |
| Application Gateway | `img/lib/azure2/networking/Application_Gateway.svg`      | networking  |
| Front Door          | `img/lib/azure2/networking/Front_Doors.svg`              | networking  |
| ExpressRoute        | `img/lib/azure2/networking/ExpressRoute_Circuits.svg`    | networking  |
| VPN Gateway         | `img/lib/azure2/networking/VPN_Gateway.svg`              | networking  |
| Key Vault           | `img/lib/azure2/security/Key_Vaults.svg`                 | security    |
| Azure AD            | `img/lib/azure2/identity/Azure_Active_Directory.svg`     | identity    |
| API Management      | `img/lib/azure2/integration/API_Management_Services.svg` | integration |
| Logic Apps          | `img/lib/azure2/integration/Logic_Apps.svg`              | integration |
| Service Bus         | `img/lib/azure2/integration/Service_Bus.svg`             | integration |
| Event Hubs          | `img/lib/azure2/analytics/Event_Hubs.svg`                | analytics   |
| Azure Monitor       | `img/lib/azure2/management_governance/Azure_Monitor.svg` | management  |

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
├── identity/               # Azure AD
├── integration/            # API Management, Logic Apps, Service Bus
├── iot/                    # IoT Hub
├── management_governance/  # Monitor, Log Analytics
├── networking/             # VNet, Load Balancer, Front Door, VPN
├── security/               # Key Vault, Sentinel
├── storage/                # Storage Accounts, Data Lake
└── web/                    # App Service Plans
```

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
