---
name: m365-copilot-research
description: "Use Microsoft 365 Copilot APIs to offload lightweight research, Microsoft 365 grounding, and evidence retrieval before bringing only compact excerpts back into GitHub Copilot context. Use for context-saving searches over SharePoint, OneDrive, Copilot connectors, and short Copilot Chat answers. Do not use for long-running deep research, file generation, sending mail, scheduling, or actions."
argument-hint: "調査したいテーマ、検索クエリ、対象資料の範囲"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan
---

# M365 Copilot Research

Use this skill to reduce GitHub Copilot context usage by delegating early research and grounding to Microsoft 365 Copilot APIs, then returning only compact evidence and short summaries.

## When to Use

- The user wants a lightweight search or preliminary investigation over Microsoft 365 work content.
- The user wants to find relevant SharePoint, OneDrive, or Copilot connector content before asking GitHub Copilot to reason over it.
- The user wants a short Microsoft 365 Copilot grounded answer, if Chat API permissions are already available.
- The user explicitly wants to save GitHub Copilot context by retrieving only relevant excerpts.
- The user is preparing a report, deck, memo, or technical explanation and first needs source material compressed into a small evidence pack.

## Do Not Use

- Long-running deep research or Researcher-style jobs.
- Creating PowerPoint, Word, Excel, image, or other files directly through Microsoft 365 Copilot.
- Sending email, scheduling meetings, modifying files, or performing any action visible to other people.
- Replacing careful verification for customer-facing or security-sensitive conclusions.
- Automatically falling back to Scout/WorkIQ when the goal is GitHub Copilot context savings; Scout/WorkIQ may still consume GitHub Copilot SDK/model context.

## Core Model

Prefer this pipeline:

```text
User question
  -> Retrieval API / Search API / short Chat API call
  -> compact evidence pack
  -> GitHub Copilot consumes only the evidence pack
```

Use `retrieve` mode by default. Use `chat` mode only when the user needs a short synthesized answer and the required delegated Graph scopes are already consented.

## Capabilities

### Retrieval API

Use Retrieval API when you need relevant text chunks and source links from Microsoft 365 data.

Supported sources:

- SharePoint
- OneDrive for Business
- Microsoft 365 Copilot connectors

Return only:

- 3-10 relevant excerpts
- source URL
- resource metadata, if present
- sensitivity label, if present
- short notes on gaps or uncertainty

### Chat API

Use Chat API only for short, bounded prompts that can complete quickly.

Good prompts:

- "Summarize the top risks in the retrieved materials in 5 bullets."
- "Based on work and web grounding, give a short answer with caveats."

Avoid:

- "Do deep research for an hour."
- "Create a PowerPoint."
- "Send this to someone."
- "Analyze a very large corpus end-to-end."

## Authentication and Permissions

This skill requires Microsoft Graph delegated access for the signed-in user.

The Azure CLI first-party app often cannot request the required scopes for this scenario. Prefer a dedicated Entra ID app registration with MSAL device code flow or another approved delegated auth flow.

Minimum practical permissions:

- Retrieval API over SharePoint: `Sites.Read.All`
- Retrieval API over OneDrive: `Files.Read.All` or equivalent
- Connectors: `ExternalItem.Read.All`
- Chat API commonly requires a broader set such as `Sites.Read.All`, `Mail.Read`, `People.Read.All`, `OnlineMeetingTranscript.Read.All`, `Chat.Read`, `ChannelMessage.Read.All`, and `ExternalItem.Read.All`

If Graph returns 403, report the exact missing scopes and stop. Do not mask the error with a different backend.

## Helper Script

Use the helper script when available:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass `
  -File "$env:USERPROFILE\.copilot\skills\m365-copilot-research\scripts\Invoke-M365CopilotResearch.ps1" `
  -Query "Find documents about the SRE Agent weekly report setup" `
  -Mode retrieve `
  -DataSource sharePoint `
  -MaxResults 5
```

The helper accepts either:

- `-AccessToken <token>`
- `$env:M365_COPILOT_GRAPH_TOKEN`
- an Azure CLI Graph token fallback, if it already has the required scopes

Use `-Mode root` to test whether the tenant exposes `/copilot` before running retrieval.

## Output Format

When presenting results to the user or feeding them into another model, use this compact format:

```markdown
## M365 Copilot Evidence Pack

Query: {query}
Mode: retrieve|chat
Data source: sharePoint|oneDriveBusiness|externalItem

### Findings

1. {one-sentence finding}
   Source: {url}
   Evidence: "{short excerpt}"
   Label: {sensitivity label or none returned}

### Gaps / Caveats

- {what was not searched, permission gaps, no hits, preview limitation, or generated-content caveat}
```

Keep the total response under roughly 2,000-4,000 characters unless the user explicitly asks for more.

## Execution Steps

1. Restate the exact research query in one sentence.
2. Choose `retrieve` unless the user explicitly asks for a short synthesized answer and Chat API is available.
3. Run the helper with a small `MaxResults` value first, normally 3-5.
4. If the result is too broad, refine the query or add a narrower source/path filter when available.
5. Return only compact excerpts and source URLs. Do not paste full documents.
6. If the API fails due to missing scopes, report the missing scopes and the recommended Entra app consent path.

## Safety and Privacy

- Treat all returned Microsoft 365 content as private user data.
- Do not send retrieved content to third-party services.
- Do not include private retrieved details in outbound messages.
- Preserve sensitivity label information in the evidence pack when returned by Graph.
- For customer-facing output, verify important claims against the cited source material before finalizing.

## References

- Microsoft 365 Copilot APIs overview: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/copilot-apis-overview
- Microsoft 365 Copilot Chat API overview: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/api/ai-services/chat/overview
- Microsoft 365 Copilot Retrieval API overview: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/api/ai-services/retrieval/overview
