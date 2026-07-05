# YouTube Auto-Upload

定期配信を「人手ゼロ」で回すための YouTube Data API v3 連携。

## いつ使うか

- 週次/隔週で動画を自動アップロードしたい
- 公開日時を予約しておきたい (例: 月曜 7:00 JST)
- サムネ + 概要欄 + タグ + プレイリストまで自動化したい

## 初回セットアップ (一度だけ)

1. **Google Cloud Console** で新規プロジェクト作成
2. **YouTube Data API v3** を有効化
3. **OAuth 同意画面**: 外部 / Testing でOK、自分の Google アカウントを test user に追加
4. **OAuth クライアント ID** 作成: アプリの種類 = **デスクトップアプリ**
5. `client_secret.json` ダウンロード → `secrets/client_secret.json` へ
6. 初回 Python 実行時にブラウザで認証 → `secrets/token.json` 生成
7. 以降は token 自動リフレッシュ

```powershell
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

## 公開予約コード (核)

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

def get_youtube_client(secrets_dir: Path):
    token_path = secrets_dir / "token.json"
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(secrets_dir / "client_secret.json"), SCOPES)
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)

def upload(yt, mp4: Path, title: str, description: str, tags: list[str],
           publish_at_utc: str, thumbnail: Path | None = None) -> str:
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "28",  # Science & Technology
            "defaultLanguage": "ja",
        },
        "status": {
            "privacyStatus": "private",     # 予約は private + publishAt
            "publishAt": publish_at_utc,    # RFC3339, e.g. "2026-06-22T22:00:00Z" = JST 月7:00
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(mp4), chunksize=-1, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = req.execute()
    video_id = resp["id"]
    if thumbnail and thumbnail.exists():
        yt.thumbnails().set(videoId=video_id,
                            media_body=MediaFileUpload(str(thumbnail))).execute()
    return video_id
```

## 字幕 (captions) を API でアップロード

正確な `.srt` を載せたいときは **Studio の字幕エディタ UI を使わない**。UI は「セル→ファイルをアップロード→形式選択→**ネイティブ file chooser**→公開」の多段で、ブラウザ自動化だと file chooser がレンダラーをブロックして詰まりやすい。Data API なら冪等で堅牢。

**スコープが別**: 動画 insert は `youtube.upload` だが、**captions は `youtube.force-ssl` が必要**。captions も使うなら token をその両スコープで取り直す。

```python
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]  # captions 操作に必須

def upload_caption(yt, video_id, srt_path, lang="ja", name="日本語", replace=False):
    from googleapiclient.http import MediaFileUpload
    existing = yt.captions().list(part="snippet", videoId=video_id).execute().get("items", [])
    # ASR(自動字幕)とは trackKind で区別。手動トラックだけ対象にする
    ours = [c for c in existing
            if c["snippet"].get("language") == lang
            and c["snippet"].get("trackKind") != "ASR"
            and c["snippet"].get("name") == name]
    if ours and not replace:
        return "EXISTS"           # 冪等: 既存ならスキップ
    if ours and replace:
        for c in ours:
            yt.captions().delete(id=c["id"]).execute()
    body = {"snippet": {"videoId": video_id, "language": lang, "name": name, "isDraft": False}}
    media = MediaFileUpload(srt_path, mimetype="application/octet-stream", resumable=False)
    yt.captions().insert(part="snippet", body=body, media_body=media, sync=False).execute()
    return "INSERTED"
```

- `sync=False` + `.srt` のタイムコードをそのまま使う（`sync=True` は字幕本文だけ渡して YT 側で時刻推定する別用途）。
- アップロード後の確認は `captions().list`。手動トラックは `ja/standard/<name>`、自動は `ja/asr/` として両方並ぶ（共存して良い）。
- クォータ: `captions.insert` ≈ 400 units/本（video.insert 1,600 よりずっと軽い）。

## カスタムサムネは別の認証ゲート

`thumbnails().set` も、Studio UI 手動も、**「ワンタイム認証 / 上級者向け機能」**（自撮り動画 or 身分証、審査 ~24h）が未完了だと使えない。これは**長尺動画用の電話認証とは別物**。未認証だとサムネは数枚だけ通って以降ブロックされることがある。サムネが効かないときはまずこの verification 状態を疑う。

## AI 開示 (改変/合成コンテンツ) の判定

VOICEVOX 等の**合成音声 + イラストキャラ + AI 制作支援(台本/サムネ/字幕生成)**は、YouTube の「開示**不要**」例に該当するので `AI の使用 = いいえ` でよい。開示が要るのは「実在人物が言っていないことを言ったように見せる」「実際の出来事を改変」など写真リアルで誤解を招くもの。合成音声を使っている旨は概要欄クレジットで別途明示すれば誠実性も担保できる。参照: https://support.google.com/youtube/answer/14328491

## クォータと制約

| 項目 | 値 |
|---|---|
| 1日のクォータ | **10,000 units** (デフォルト) |
| video.insert | 1,600 units/本 → **約 6 本/日** |
| thumbnail.set | 50 units |
| 動画あたり最大 | 256GB or 12時間 |
| **新規 / 未認証チャンネル** | private/unlisted 限定 (申請で解除) |

→ 週1〜3本のチャンネルなら問題なし。それ以上はクォータ増加申請。

## 公開時刻の指定 (JST → UTC 変換)

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# 例: 月曜 7:00 JST の次の発生
jst = ZoneInfo("Asia/Tokyo")
target_jst = datetime(2026, 6, 22, 7, 0, tzinfo=jst)
publish_at_utc = target_jst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
```

## メタデータのベストプラクティス

| 項目 | 戦略 |
|---|---|
| タイトル | 60字以内、`【AI週報 #12】` 等の固定 prefix で連番感 |
| 概要欄 | 1行目で結論、2行目以降にタイムスタンプ + 元URLリスト |
| タグ | 5〜15個。固定 ("AI","Copilot","Azure") + 当週固有 |
| categoryId | `28` = Science & Technology |
| defaultLanguage | `ja` |
| AI 生成明示 | 概要欄に「※AIナレーション含む」を入れる (YouTube ポリシー) |

## タイムスタンプ自動生成 (SRTから)

```python
def srt_to_chapters(srt_path: Path, headings: list[str]) -> str:
    """SRT から各スライドの開始秒を抜き出して "00:00 タイトル" 形式に。"""
    lines = []
    cur = 0.0
    for i, h in enumerate(headings):
        ts = f"{int(cur//60):02d}:{int(cur%60):02d}"
        lines.append(f"{ts} {h}")
        # 各スライドの長さは srt から計算 ...
    return "\n".join(lines)
```

YouTube は概要欄に `00:00 〜` 形式があると**自動でチャプター分割**してくれる。

## 失敗時のフェイルセーフ

| 失敗箇所 | 対処 |
|---|---|
| OAuth token 期限切れ | `creds.refresh(Request())` で自動更新。失敗時はフロー再実行 |
| upload 中ネットワーク断 | `resumable=True` で resumable upload。`req.next_chunk()` でリトライ |
| クォータ超過 (403) | 24h 待機 / 翌日に回す / クォータ増加申請 |
| メタデータ拒否 (400) | タイトル 100字超 / カテゴリ無効 等。lint してから insert |
| 動画削除されたい | `yt.videos().delete(id=video_id).execute()` (1日のクォータ 50 units) |

## 通知

成功/失敗を Teams Webhook で投げる:

```python
import requests
requests.post(TEAMS_WEBHOOK, json={
    "text": f"📺 公開予約完了: {title}\nhttps://youtube.com/watch?v={video_id}\n予定: {publish_at_jst}"
})
```

## 倫理 / コンプライアンス

- **AI 生成だと冒頭またはタイトル/概要で明示**
- 元記事 URL を概要欄に必ず掲載
- 本文丸読みは避けて要約 + 引用範囲に留める
- 顧客名・社内情報を含めない
- 月1本は手動レビュー入れる(全自動だと誤情報リスクが蓄積)
