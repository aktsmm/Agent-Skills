# Teams Photo Export Implementation Notes

## What was verified

- A Teams chat URL can expose a `chatId` such as `19:...@thread.v2`.
- WorkIQ/Graph-style message listing can reveal inline image URLs under `hostedContents/.../$value`.
- Direct Graph download failed in this environment because the available token did not include `Chat.Read`.
- Teams Web opened in a CDP-enabled Edge session successfully exposed visible message images as `blob:https://teams.cloud.microsoft/...`.
- Fetching those blob URLs inside the Teams page saved 10 `.webp` images successfully.

## Storage model

| Image type | Storage | Best access path |
| --- | --- | --- |
| Inline pasted image | Teams hosted content / ASM | Graph `hostedContents/$value` if `Chat.Read` is available; otherwise Teams Web blob/ASM |
| Chat file attachment | Sender OneDrive, often Microsoft Teams Chat Files | Attachment `contentUrl` / OneDrive sharing URL |
| Channel file | Team SharePoint document library | SharePoint/OneDrive Graph |

Microsoft Graph states that file attachments are not hosted content and are stored in SharePoint or OneDrive:

https://learn.microsoft.com/en-us/graph/api/resources/chatmessagehostedcontent?view=graph-rest-1.0

## Graph permissions

Hosted content APIs:

- Chat delegated: `Chat.Read` or `Chat.ReadWrite`
- Channel delegated: `ChannelMessage.Read.All`
- Chat application: `Chat.Read.All`
- Channel application: `ChannelMessage.Read.All`

References:

- https://learn.microsoft.com/en-us/graph/api/chatmessage-list-hostedcontents?view=graph-rest-1.0
- https://learn.microsoft.com/en-us/graph/api/chatmessagehostedcontent-get?view=graph-rest-1.0
- https://learn.microsoft.com/en-us/graph/api/chat-list-messages?view=graph-rest-1.0
- https://learn.microsoft.com/en-us/graph/api/channel-list-messages?view=graph-rest-1.0

## Why Teams Web is the default

The user may not have admin consent or a token with `Chat.Read`. Teams Web already has the user's interactive session and can render images the user is authorized to see. A Playwright script attached over CDP can fetch page-local blob URLs without handling Graph tokens.

Limitations:

- Blob images may be WebP previews rather than original PNG/JPEG.
- Only rendered or scrolled-into-view messages are available.
- Teams virtualizes message lists; fetch and save while each image is still in DOM.

Enhancement:

- Capture Network responses for `asm.skype.com/.../views/imgpsh_fullsize*` after clicking/opening images to improve quality when available.

## Native Teams

New Teams is WebView2-based and stores data under:

```text
%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams\EBWebView
```

In the verified environment, existing Teams WebView2 processes did not expose `--remote-debugging-port`. Enabling WebView2 debugging may require restarting Teams with extra environment/browser arguments and is less stable than using dedicated Edge.

WebView2 browser flags reference:

https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/webview-features-flags
