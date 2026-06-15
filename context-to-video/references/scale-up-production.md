# Scale-up: PoC → Production Channel

「1本作って終わり」から「定期配信チャンネル」に育てる時のディレクトリ・運用設計。

## いつ昇格するか

以下が複数当てはまったら昇格時:

- [ ] 同じパイプラインで 2 本目以降を作る予定がある
- [ ] マスコット / テンプレ / BGM など**全話で共通使い回す素材**が出てきた
- [ ] YouTube / Udemy など外部公開先が決まっている
- [ ] 週次や月次の**定期スケジュール**を入れたい
- [ ] 重複防止や進捗トラックが必要 (同じトピックを2回扱わない 等)

## ディレクトリ昇格パターン

### PoC 期 (1〜2本)

```
<topic>-poc/
├── notes/script.json
├── slides/  audio/  output/
├── scripts/
└── README.md
```

### Production 期 (継続運用)

```
<channel>/
├── episodes/                  ← 各話ごとに完全分離
│   ├── ep01_topic-a/
│   │   ├── script.json
│   │   ├── slides/  audio/  output/
│   │   └── metadata.json      ← episode番号・公開日・video_id 等
│   ├── ep02_topic-b/
│   └── ...
├── assets/                    ← 全話共通の固定素材
│   ├── mascot/
│   │   ├── face.jpg
│   │   ├── original.png
│   │   └── prompt.md          ← seed + プロンプト記録
│   ├── templates/             ← intro/outro/font config
│   └── bgm/
├── scripts/                   ← build_video.py 等は1箇所に集約
├── sources/                   ← 週次収集の snapshot (yyyy-Wnn ごと)
├── db/                        ← topics.sqlite (重複防止) / episodes.sqlite
├── secrets/                   ← gitignore: YouTube OAuth等
├── notes/                     ← 戦略・パイプライン設計の人間向けdoc
├── .gitignore
└── README.md
```

## 設計原則

| レイヤ | 役割 | 注意 |
|---|---|---|
| `episodes/` | 各話の成果物 + メタ | 1話 = 1ディレクトリ。次の話に影響させない |
| `assets/` | 再利用部品 | チャンネル全体の一貫性 (マスコット顔・配色等) |
| `scripts/` | 実行コード | 単一実装、`--project` 引数で各 episode を処理 |
| `db/` | 状態管理 | SQLite で重複・進捗・公開状況 |
| `secrets/` | 認証情報 | `.gitignore` 必須 |
| `sources/` | 入力スナップショット | 週次の RSS/API 取得結果。後で再現可能に |
| `notes/` | 人間向け企画 | 戦略・分析・進捗ログ |

## マイグレーション手順

```powershell
# 1. 新ワークスペース作成
$new = 'D:\projects\<channel>'
@('episodes','assets\mascot','assets\templates','assets\bgm','scripts','sources','db','secrets','notes') |
  ForEach-Object { New-Item -ItemType Directory -Force -Path "$new\$_" | Out-Null }

# 2. PoC のスクリプト・素材を移動
Copy-Item -Recurse <poc>\scripts\* "$new\scripts\"
Copy-Item <poc>\avatar\input\face.jpg "$new\assets\mascot\face.jpg"

# 3. 第1話を episodes/ep01 にアーカイブ
$ep1 = "$new\episodes\ep01_<slug>"
New-Item -ItemType Directory -Force -Path "$ep1\output" | Out-Null
Copy-Item <poc>\notes\script.json "$ep1\"
Copy-Item <poc>\output\final*.mp4 "$ep1\output\"
Copy-Item <poc>\output\final.srt "$ep1\output\"

# 4. metadata.json
@{ episode=1; title='...'; topic='...'; published_at=$null; video_id=$null } |
  ConvertTo-Json | Set-Content "$ep1\metadata.json" -Encoding UTF8

# 5. .gitignore
@'
secrets/
db/*.sqlite
episodes/*/audio/
episodes/*/slides/
episodes/*/avatar/
__pycache__/
*.pyc
'@ | Set-Content "$new\.gitignore" -Encoding UTF8
```

## スクリプトの汎用化

PoC のスクリプトはハードコード絶対パスが多い。Production化時に `--project` 引数で抽象化:

```python
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--project", required=True, type=Path,
                help="<channel>/episodes/<slug>/ を指す")
args = ap.parse_args()

script = args.project / "script.json"
slides = args.project / "slides"
out = args.project / "output"
```

これで全 episode に同じスクリプトを使い回せる。

## メタデータ JSON スキーマ (episodes/*/metadata.json)

```json
{
  "episode": 1,
  "slug": "copilot-cli-smarter-subagent",
  "title": "【AI週報 #1】Copilot CLI smarter subagent delegation",
  "topic_tags": ["github-copilot", "cli"],
  "duration_sec": 143,
  "language": "ja",
  "voice": "ja-JP-NanamiNeural",
  "use_avatar": true,
  "source_urls": ["https://github.blog/..."],
  "published_at": null,
  "youtube": {
    "video_id": null,
    "playlist_id": null,
    "thumbnail_path": "output/thumb.jpg"
  },
  "status": "draft"
}
```

`status` は `draft` → `ready` → `scheduled` → `published` で遷移。

## 重複防止 DB

```sql
CREATE TABLE topics_used (
  url TEXT PRIMARY KEY,
  first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  used_in_episode TEXT
);
```

週次ニュース収集時に `INSERT OR IGNORE` で記録、`SELECT` で除外。同じ記事を2週連続で扱わない保険。

## 一括処理スクリプト (orchestrate.py)

複数 episode をまとめて build:

```powershell
python scripts\orchestrate.py --from 2 --to 5 --upload
```

中で各 episode に対して `build_video.py` → `add_avatar.py` → `ellipse_overlay.py` → (任意で) `upload_youtube.py` を順に呼ぶ。

## 旧 PoC の扱い

昇格後も PoC ワークスペースは**消さずアーカイブとして残置**:
- 過去の検証ログ・ノートが価値情報
- 比較リファレンスとして有用
- README に「アーカイブ・新規制作は <new path>」と明記

## 落とし穴

| 症状 | 原因 / 対処 |
|---|---|
| 「PoCのコードコピペで動かない」 | 絶対パスがハードコードされてる。`--project` 引数で抽象化 |
| 「マスコットが話によって変わる」 | `assets/mascot/` から固定的に読まない。各 episode 直下に置いて編集してしまう |
| 「同じトピックを2週連続で扱った」 | `db/topics_used` テーブルでチェックする習慣を入れる |
| 「secrets を git に push してしまった」 | `.gitignore` 設定済みでも `git rm --cached` で履歴清掃。token は速やかに失効/再発行 |
