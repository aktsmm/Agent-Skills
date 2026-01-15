# Cloud Icons Reference

## Azure Icons

Enable Azure icons in draw.io:
1. Open `.drawio` file
2. Click **"+ More Shapes"** (bottom-left)
3. Check **Azure**
4. Click **Apply**

### Common Azure Icons

| Service | Icon Name | Category |
|---------|-----------|----------|
| Virtual Machine | `Azure VM` | Compute |
| App Service | `Azure App Service` | Compute |
| Azure Functions | `Azure Functions` | Compute |
| Storage Account | `Azure Storage` | Storage |
| SQL Database | `Azure SQL` | Database |
| Cosmos DB | `Azure Cosmos DB` | Database |
| Virtual Network | `Azure VNet` | Networking |
| Load Balancer | `Azure Load Balancer` | Networking |
| Application Gateway | `Azure App Gateway` | Networking |
| Key Vault | `Azure Key Vault` | Security |
| Azure AD | `Azure Active Directory` | Identity |

### Azure Icon Style

```xml
<mxCell id="vm1" value="VM-01"
        style="sketch=0;outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.azure.virtual_machine;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="50" height="50" as="geometry"/>
</mxCell>
```

## AWS Icons

Enable AWS icons in draw.io:
1. Open `.drawio` file
2. Click **"+ More Shapes"** (bottom-left)
3. Check **AWS**
4. Click **Apply**

### Common AWS Icons

| Service | Icon Name | Category |
|---------|-----------|----------|
| EC2 | `AWS EC2` | Compute |
| Lambda | `AWS Lambda` | Compute |
| S3 | `AWS S3` | Storage |
| RDS | `AWS RDS` | Database |
| DynamoDB | `AWS DynamoDB` | Database |
| VPC | `AWS VPC` | Networking |
| ELB | `AWS ELB` | Networking |
| IAM | `AWS IAM` | Security |

### AWS Icon Style

```xml
<mxCell id="ec2" value="EC2"
        style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=#ffffff;fillColor=#232F3E;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="50" height="50" as="geometry"/>
</mxCell>
```

## Best Practices

1. **Consistency**: Use icons from the same provider in one diagram
2. **Labeling**: Always add text labels below icons
3. **Sizing**: Keep icon sizes consistent (48x48 or 50x50 recommended)
4. **Grouping**: Use containers/swimlanes to group related services

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
