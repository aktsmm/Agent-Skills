# Content Guidelines

Best practices for creating content.json files.

## URL Format (Required)

### Standard Format: "Title - URL"

Reference URLs in slides must follow this format:

```
{Document Title} - {URL}
```

#### Examples

```
VPN Gateway の新機能 - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/whats-new
Basic IP 移行について - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/basic-public-ip-migrate-about
```

### content.json Example

```json
{
  "type": "content",
  "title": "参考URL一覧",
  "bullets": [
    {
      "text": "VPN Gateway の新機能 - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/whats-new",
      "level": 0
    },
    {
      "text": "Basic IP 移行について - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/basic-public-ip-migrate-about",
      "level": 0
    }
  ]
}
```

### Why This Format?

| Aspect        | Benefit                                 |
| ------------- | --------------------------------------- |
| Readability   | Title provides context before URL       |
| Clickability  | URL is clearly separated and clickable  |
| Consistency   | Uniform style across all presentations  |
| Accessibility | Screen readers can announce title first |

### Anti-patterns (Avoid)

```
❌ https://learn.microsoft.com/... (URL only, no context)
❌ [VPN Gateway の新機能](https://...) (Markdown format doesn't render in PPTX)
❌ VPN Gateway の新機能 (https://...) (Parentheses break some URL parsers)
```

## Bullet Point Guidelines

### Hierarchy Levels

| Level | Use Case       | Example                  |
| ----- | -------------- | ------------------------ |
| 0     | Main points    | Key feature descriptions |
| 1     | Sub-points     | Details, examples        |
| 2     | Nested details | Rare, avoid if possible  |

### Example

```json
{
  "type": "content",
  "title": "Azure VPN Gateway Features",
  "bullets": [
    { "text": "High Availability", "level": 0 },
    { "text": "Active-active configuration", "level": 1 },
    { "text": "Zone-redundant gateways", "level": 1 },
    { "text": "Security", "level": 0 },
    { "text": "IPsec/IKE encryption", "level": 1 }
  ]
}
```

## Image References

### Local Images

```json
{
  "image": {
    "path": "images/architecture.png",
    "position": "right",
    "width_percent": 45
  }
}
```

### Remote Images

```json
{
  "image": {
    "url": "https://example.com/diagram.png",
    "position": "bottom",
    "height_percent": 50
  }
}
```

### Position Options

| Position | Description                  |
| -------- | ---------------------------- |
| `right`  | Image on right, text on left |
| `bottom` | Image below text             |
| `full`   | Full-slide image             |

## URL Priority (Japanese First)

| Priority | URL Format                             |
| -------- | -------------------------------------- |
| 1        | `/ja-jp/` Japanese version (if exists) |
| 2        | `/en-us/` English version (fallback)   |

## URL Hyperlink (Required)

> ⚠️ **Rule**: All URL strings in slides MUST have hyperlinks.

### Target Elements

| Location             | Hyperlink   |
| -------------------- | ----------- |
| `footer_url` field   | ✅ Required |
| URLs in bullets      | ✅ Required |
| Reference URL slides | ✅ Required |
| Appendix URLs        | ✅ Required |

### Link Style

| Attribute | Value                          |
| --------- | ------------------------------ |
| Color     | Blue (`RGBColor(0, 120, 212)`) |
| Underline | Yes                            |
| Hyperlink | Set to URL itself              |

### Anti-patterns

```
❌ Leave URL as plain text
❌ Keep link color as black
❌ URL without hyperlink setting
```

## GitHub Commit History (Optional)

> Requires GitHub CLI (`gh`) to be installed.

For schedule/deadline information, fetch GitHub commit history:

```powershell
gh api "repos/MicrosoftDocs/azure-docs/commits?path=articles/{service}/{file}.md&per_page=5" \
  --jq '.[] | "\(.commit.author.date | split("T")[0]): \(.commit.message | split("\n")[0])"'
```

### Slide Format

```json
{
  "type": "content",
  "title": "Document Update History (GitHub)",
  "bullets": [
    { "text": "Recent changes to whats-new.md", "level": 0 },
    { "text": "2026-01-30: Active-Passive GA, deadline extended", "level": 1 },
    { "text": "Source: MicrosoftDocs/azure-docs", "level": 0 }
  ]
}
```

## Slide Numbers

### Enable in content.json

```json
{
  "title": "Presentation Title",
  "settings": {
    "slide_numbers": true,
    "date_footer": "2026-02-03"
  },
  "slides": [...]
}
```

> ⚠️ If slide numbers don't appear, enable them in the template via "Insert → Header and Footer".
