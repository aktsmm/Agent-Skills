# Voiced Mascot Pipeline (VOICEVOX + PSD layers)

YouTube/解説動画用の **キャラクター付きナレーション動画** を作るときの定石。`edge-tts + SD 顔` ではなく、より自然で著作権クリアな構成。

## 採用判断

| 用途 | 推奨スタック |
|---|---|
| 個人実験・PoC | `edge-tts` + 任意の顔 (本SKILLの既定) |
| YouTube 定期投稿・「ゆるふわ系」キャラ運営 | **VOICEVOX + 公式キャラPSD立ち絵** (本reference) |
| 顧客向け・商用安定運用 | Azure Speech + 自作 or ライセンス取得アバター |

VOICEVOX 派生キャラ(ずんだもん/四国めたん/春日部つむぎ等)は **クレジット表記だけで商用OK**。チャンネルマスコットとして強い。

## スタック

| 役割 | ツール |
|---|---|
| TTS | **VOICEVOX engine** (`http://localhost:50021` REST API) |
| キャラ素材 | **公式SD立ち絵 PSD**(差分付き) + VOICEVOX engine 同梱の portrait |
| レイヤー抽出 | `psd-tools` |
| 合成 | `Pillow` (alpha_composite) → `ffmpeg` libvpx-vp9 webm → overlay |
| クレジット | ffmpeg `drawtext` |

## ライセンス必須事項

- **クレジット表記**: `VOICEVOX:<キャラ名>` を動画内常時表示 or 概要欄に記載
- **規約**: https://zunko.jp/con_ongen_kiyaku.html (ずんだもん系の場合)
- 公式SD立ち絵 PSD は Google Drive で配布: https://drive.google.com/drive/folders/1z9hKO8EEDXohu1jPuoIg06mWAhZWJ-48

## VOICEVOX セットアップ

```powershell
# CPU 版 (約 300MB DL, 解凍後 約 4GB)
$url = 'https://github.com/VOICEVOX/voicevox_engine/releases/latest'
# 'voicevox_engine-windows-cpu-X.Y.Z.7z.001' を DL → 7-Zip で展開
# run.exe を起動すると localhost:50021 でエンジン稼働
```

**Speaker ID 主要**(ずんだもん):
- 3: ノーマル / 1: あまあま / 7: ツンツン / 5: セクシー / 22: ささやき

API 呼び出し:

```python
import requests
def voicevox_tts(text, out_wav, speaker=3, url="http://localhost:50021"):
    q = requests.post(f"{url}/audio_query", params={"text": text, "speaker": speaker}).json()
    wav = requests.post(f"{url}/synthesis", params={"speaker": speaker}, json=q).content
    out_wav.write_bytes(wav)
```

## VOICEVOX engine 同梱の立ち絵 (簡易)

各キャラの UUID フォルダ配下に portrait が **同梱されている**(知られざる便利機能):

```
voicevox_engine/resources/character_info/<speaker_uuid>/
├── portrait.png       メイン立ち絵
├── portraits/<id>.png スタイル別立ち絵
├── icons/<id>.png     スタイル別アイコン (256x256)
├── policy.md          ライセンス
└── voice_samples/     サンプル音声
```

**罠**: `portraits/*.png` は **スタイル違いで顔がほぼ同じ**(diff 0-500px)。リップシンクには使えない。表情差分が必要なら次セクションへ。

## 公式SD立ち絵 PSD でリップシンク (本命)

Drive から `gdown` で取得:

```python
import gdown
gdown.download_folder(
    "https://drive.google.com/drive/folders/1z9hKO8EEDXohu1jPuoIg06mWAhZWJ-48",
    output="assets/sd/", quiet=False)
```

`<キャラ>差分付き.psd` (典型 3000x3000) に以下のレイヤーグループが入っている:
- **口差分** 7枚程度 (デフォルト / 点口 / アホ開き / 開き口 / 舌だし / 猫口 / への字)
- **左目差分 / 右目差分** 各10枚 (デフォルト / 閉じ / 笑顔 / ジト / 怒り / 丸 / きょとん / ウインク / 眉)
- **胴体 / 鼻 / 背景**

抽出:

```python
from psd_tools import PSDImage
from PIL import Image

psd = PSDImage.open("char_with_diffs.psd")
canvas_size = psd.size

def extract(layer, prefix=""):
    if layer.is_group():
        for child in layer:
            extract(child, prefix + layer.name + "__")
        return
    img = layer.composite()
    if img is None: return
    canvas = Image.new("RGBA", canvas_size, (0,0,0,0))
    canvas.paste(img, layer.offset, img if img.mode == "RGBA" else None)
    canvas.save(f"layers/{prefix}{layer.name}.png")

for L in psd: extract(L)
```

`canvas.paste(img, layer.offset, ...)` の **第3引数(mask)を忘れない**: 透過がずれる。

## 簡易リップシンクアルゴリズム

```python
# 1. WAV から振幅トラックを取る (peak per window @ ANALYSIS_FPS=96)
# 2. FPS=24 にダウンサンプル
# 3. 非対称スムージング: open は速く(0.7) close は遅く(0.32)
# 4. ヒステリシス: ON=0.18 / OFF=0.09 でバタつき防止
# 5. 開き具合で 3 viseme 選択: closed / small (a<0.45) / large
# 6. 瞬き: 4 秒 ± 1.5 秒間隔・0.18秒持続
```

合成順序(下→上):

```
胴体 → 鼻 → 左目 → 右目 → 左眉 → 右眉 → 口
```

6パターン(口3 × 瞬き2)を**事前合成キャッシュ**してフレーム書き出しを高速化。

## 出力パイプライン

```python
# 1. フレーム書き出し (caches から選択)
for i, mouth_state in enumerate(states):
    cache[(mouth_state, i in blink_frames)].save(f"f_{i:05d}.png")

# 2. WebM with alpha (libx264 は alpha 不可、libvpx-vp9 を使う)
ffmpeg -framerate 24 -i f_%05d.png -c:v libvpx-vp9 -pix_fmt yuva420p \
       -auto-alt-ref 0 -b:v 1500k pose.webm

# 3. ベース動画に overlay
ffmpeg -i base.mp4 -c:v libvpx-vp9 -i pose.webm \
  -filter_complex "[1:v]fps=30[zm];[0:v][zm]overlay=W-w-40:H-h+20[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 20 -c:a copy out.mp4
```

**注意**: 2 番目の入力は `-c:v libvpx-vp9` を **入力側に指定**しないと alpha が落ちる。

## クレジット焼き込み

```bash
# drawtext で text= のコロンは \: にエスケープ必須
ffmpeg -i in.mp4 -vf "drawtext=fontfile='C\:/Windows/Fonts/BIZ-UDGothicR.ttc':\
text='VOICEVOX\:ずんだもん':fontsize=28:fontcolor=white@0.85:\
box=1:boxcolor=black@0.5:boxborderw=10:x=w-tw-32:y=32" -c:a copy out.mp4
```

## 落とし穴

| 症状 | 原因 / 対処 |
|---|---|
| 「同梱立ち絵で口パクできない」 | `portraits/*.png` はスタイル違いの全身ポーズ。表情差分なし。PSD取得が必要 |
| psd-tools の `Image.new` でエラー | `from PIL import Image` していない / pillow と diffusers の Image を混同 |
| webm に alpha が乗らない | `-pix_fmt yuva420p` + `-auto-alt-ref 0` 両方必要 |
| overlay 後にアバターが消える | 2番目入力に `-c:v libvpx-vp9` を入力側で明示しないと alpha 落ち |
| 全身ポーズ切替が機械的に見える | ポーズ全体ではなく **口レイヤーだけ**差替える |
| 口パクがバタつく | ヒステリシス未実装。ON/OFF閾値を別々にする (例: 0.18/0.09) |
| 立ち絵が顔アップで大きすぎる | SD チビキャラは crop しない (`getbbox()` で余白だけ削る)。サイズも display height 600-800 程度に |
| drawtext で `:` が原因のエラー | `text='X\:Y'` のように `:` を `\:` に置換 |
| gdown で Drive フォルダ DL 一部失敗 | `FileURLRetrievalError` は権限制限ファイルだけ。残りはDL継続。`remaining_ok` は古い版で動かない |
| WAV 読み込み時に `len(samples)` がでかすぎる | `nch>1` の時は `samples[::nch]` で mono 化必須 |

## 哲学: 「徹底的にいいものを」

このパイプラインで動画作るとき、**時短のために妥協しない**:

- 「立ち絵が落とせないから絵文字で代用」→ NG。素材を粘り強く探す (公式Drive、Booth、GitHub等)
- 「リップシンク無理だから静止画で出す」→ NG。PSD レイヤーまで掘る
- 「公式立ち絵で済ませる」→ NG。差分なしと判明したら次の手段へ進む
- ユーザーが「徹底的に」と言ったら **本気で品質を上げる**。ショートカット禁止
- 一方、**勝手な実装簡略化や時短判断は事前に意図を伝えて承認を取る**

## 英単語の読みは原稿でカタカナ化する (必須・ただし二層分離)

VOICEVOX は英単語のスペルを誤読する。だが **スライド表示まで全部カタカナにすると逆に読みにくい・カッコ悪い** ことが ep01 制作で判明。
**ナレ(音声) と スライド表示(視覚) を分離する** のが必須:

| 場面 | 表記 |
|---|---|
| **ナレ原稿(narration)** | **カタカナで書く** (`ギット`, `ギットハブ`, `プッシュ`) |
| **スライド見出し・箇条書き(heading/bullets)** | **英語そのまま** (`Git`, `GitHub`, `push`, `pull`) |
| **初出時のナレ補足** | 「ギットハブ。スペルは ジー アイ ティー エイチ ユー ビー なのだ」と1回だけ読み方を明示 |

一般的に日本語混じりで英語のまま書く慣習がある用語(`Git`, `GitHub`, `Pull Request`, `README`, `LICENSE`, `commit`, `push`, `pull`, `branch`, `clone`, `fork`, `Issue`, `Actions`, `Copilot` 等) は **スライドでは英語推奨**。視覚的に読みやすい。

頻出辞書例 (シリーズ・チャンネルごとに専用辞書を持つこと):
- Azure → ナレ「アジュール」/ スライド「Azure」
- GitHub → ナレ「ギットハブ」/ スライド「GitHub」
- Copilot → ナレ「コパイロット」/ スライド「Copilot」
- pull request → ナレ「プルリクエスト」/ スライド「Pull Request」
- README → ナレ「リードミー」/ スライド「README」

シリーズ用辞書テンプレ: `<content-workspace>/_shared/voicevox-readings.md`
変換スクリプト `content_to_script.py` 側で **ナレフィールドだけカタカナ化適用、bullets/headingは英語のまま** にする実装が安全。

## 漢字の誤読対策 (必須)

VOICEVOX は文脈で漢字も誤読する。**用言・接続詞・副詞・同音異義語はひらがなに開く**。

| 場面 | 方針 |
|---|---|
| 体言(専門用語の名詞) | 漢字OK |
| 用言(動詞・形容詞) | ひらがなに開く |
| 接続詞・副詞 | ひらがなに開く (殆ど→ほとんど、兎に角→とにかく、為→ため、各々→おのおの) |
| 同音異義語(重複/開く/入る等) | ひらがなに開いて読みを固定 (じゅうふく / ひらく / はいる) |

絶対ひらがな化リスト(誤読率特に高い):
- 出来る → できる
- 無い → ない / 有る → ある
- 此の/其の/彼の → この/その/あの
- 沢山 → たくさん
- 良い → いい (or よい)
- 殆ど → ほとんど
- 兎に角 → とにかく
- 各々 → おのおの
- 為 → ため
- 様々 → さまざま

校正手順:
1. 原稿を **音読**する(詰まる漢字は視聴者も詰まる→ひらがな化候補)
2. **VOICEVOX で試聴**してから本生成(動画フル生成は時間かかるので試聴必須)
3. 違和感あった単語は **辞書に追記**

詳細表: `<content-workspace>/_shared/voicevox-readings.md` の「漢字の誤読対策」セクション

## OP/タイトルスライドの尺ルール (ep01 教訓)

タイトルスライド1枚に **OPナレ全部(挨拶+シリーズ紹介+テーマ+フック計30秒以上)** を流すと、視聴者は「タイトル画面長すぎ」と感じる(`スライドが遅い` フィードバックの実態)。

**ルール:**
- タイトルスライド(slide_00) の音声は **最大10-12秒** に収める
- それ以上の OP 内容は **slide_01 として「今日のテーマ + フック」スライド** を1枚作って分割
- 1スライドあたりの音声 = 上限 60-90秒。それを超えるなら2枚以上に分ける
- 視覚要素(スライド)と聴覚要素(ナレ)の **テンポを合わせる**

## クイズスライドは bullets 必須 + シンキングタイム必須

確認問題スライドで bullets(=選択肢A〜D)が空だと、視聴者は **選択肢を耳だけで覚える** ことになり、考える時間がない。
さらに、問題ナレ直後に解答スライドが来ると **考える間がない** ので「ただの読み上げ」になる。

**ルール:**
- クイズ問題スライドの `bullets` には **必ず選択肢A〜Dを書く**
- 表示テキスト例: `A. git push` / `B. git add` / `C. git commit` / `D. git pull`
- 解説スライドの bullets は **正解の根拠を3点** (なぜ正解 / 他がなぜ違う / 試験頻度)
- **問題スライドの直後にシンキングタイムスライド (3-2-1 カウントダウン) を自動挿入**
  - 構造: 問題スライド → thinking スライド (3-5秒) → 解説スライド
  - ナレ例: `シンキングタイム! ......さん、にー、いち。それじゃあ、正解を発表するぞ!`
  - `content_to_script.py` で「heading が Q で始まり 正解 を含まない quiz」の後に自動挿入

**重要な追加ルール (ep01/ep02の事故より):**
- thinking スライドは **3-2-1 だけを表示しない**。必ず直前の quiz 問題見出しと A〜D 選択肢を引き継ぐ。
- `render_thinking()` は `heading` と `bullets` を描画し、その下にカウントダウンを置く。
- 問題スライドだけでなく thinking スライドも目視確認する。視聴者は thinking 中に問題を見返すため。
- ページ番号はカウントダウンと重なりやすいので、thinking レイアウトでは右下など安全な位置へ逃がす。
- QA対象: 最初の quiz 問題スライド + その直後の thinking スライド。

## OPタイトルのプレースホルダー事故を防ぐ

タイトルスライドは、`**見出し**: OP タイトル` や `箇条書き` だけで作ると、レンダラーが **OP タイトル** をそのまま表示してしまう。

**ルール:**
- `title` スライドには必ず `**タイトル**` / `**サブタイトル**` / `**出典**` を書く。
- `content_to_script.py` は title スライドでは `**タイトル**` を最優先で抽出し、`**見出し**` より優先する。
- `**タイトル**` がない title スライドはエラーにするか、少なくとも生成前QAで止める。
- 長いタイトルは原稿側で `\n` を入れる。さらに `render_title()` 側で横幅を測り、自動縮小して右端クリップを防ぐ。
- QA対象: `slide_00.png`。本タイトルが出ているか、右端で切れていないかを必ず見る。

## 生成前PNG QAゲート (長尺VOICEVOX動画では必須)

フル生成は20分動画だと数十分かかる。生成後にOPやクイズの表示不具合を見つけると、TTS・動画・アバター合成をやり直すことになる。

フルビルド前に、最低限次をPNGで目視確認する:

| PNG | 確認内容 |
|---|---|
| `slide_00.png` | OPタイトルが本タイトル。`OP タイトル` などのプレースホルダーでない。右端で切れていない。 |
| `slide_01.png` | 本文1枚目が「今日のテーマ」。OP仮スライドが混入していない。 |
| 最初の図表 | table / hierarchy / matrix の中身が空でない。アバター予約領域に被らない。 |
| 最初の quiz | 問題見出しとA〜D選択肢が見える。 |
| 最初の thinking | 問題見出しとA〜D選択肢が残っている。3-2-1だけではない。 |

NGなら動画生成へ進まない。`script.md` / `content_to_script.py` / `build_episode.py` を直して、PNG QAからやり直す。

## 絵文字は使わない (BIZ UDGothic 等の和文フォントに無いので豆腐になる)

スライドの bullets / heading に **絵文字を入れない**:

- ❌ `❌ fix → ダメ` (豆腐 □ になる)
- ❌ `⭕ 良い書き方`
- ❌ `🌱 ED`
- ❌ `📌 ポイント`

代替:
- 評価表現は **`BAD:` / `MID:` / `GOOD:`** または **`NG:` / `OK:`** のテキストラベル
- 「ポイント」「重要」等は **`POINT:` / `KEY:`** または `★`(これは大丈夫)
- 装飾アイコンは Pillow で描画(`d.ellipse()` 等)

ナレ(音声)側にも絵文字は入れない(VOICEVOX が読み飛ばすので不要)。

## 和欧混植: 半角英数字の前後に半角スペースを入れる

スライド表示の **可読性向上** のため、和文中の半角英数字には **必ず前後に半角スペース**:

- ❌ `Gitのコミット履歴` (詰まって読みにくい)
- ⭕ `Git のコミット履歴`
- ❌ `GH-900合格コース第1話`
- ⭕ `GH-900 合格コース 第1話`
- ❌ `git addコマンドで`
- ⭕ `git add コマンドで`
- ❌ `Pull RequestをDraftで`
- ⭕ `Pull Request を Draft で`

例外:
- 半角句読点/括弧の隣接時は不要: `Git(ギット)` / `Git, GitHub` はOK
- ナレ(音声)は VOICEVOX が読むだけなのでスペース不要

`script.md` のテーブルや bullets を書くときに意識する。

## スライドは「箇条書きだけ」にしない (図表必須)

20分動画で **全スライド = 見出し + 箇条書きのみ** だと飽きる・記憶残らない。
種類別に slide_type を分けて、内容に応じて視覚化方法を選ぶ:

| slide_type | 用途 | 実装 |
|---|---|---|
| `title` | OP/ED 表紙 | 大きめテキスト |
| `content` | 通常の解説 | 見出し + 箇条書き(最大4個) |
| `quiz` | 確認問題 | A〜D 選択肢 bullets 必須 |
| **`table`** | 2-3列の比較 (Git vs GitHub等) | 行 = 観点、列 = 対象 |
| **`flow`** | 矢印付きフロー (push/pull 向き、GitHub Flow 6段階) | 横並び/縦並びの箱+矢印 |
| **`hierarchy`** | ピラミッド (Role 5段階、Org階層) | 上下に積む |
| **`timeline`** | 状態遷移 (Modified→Staged→Committed) | 横線+ノード |
| **`screenshot`** | UI 説明 (GitHub画面+注釈矢印) | スクショ画像+赤枠/矢印 |
| **`mermaid`** | 複雑図 | Mermaid 記法 → 別レンダラで PNG 化 |

### 使い分けの目安

1本の動画で **content 6-8割 / 図表 2-4割** が目安。少なくとも以下は必ず図表化:

- **2つを比較する話** (Git vs GitHub、Merge 3方式) → `table`
- **順序・遷移がある話** (GitHub Flow、ファイル状態) → `flow` or `timeline`
- **階層がある話** (Role、Org構造) → `hierarchy`
- **UI 操作** (Issue 作成画面等) → `screenshot`

### 実装の現実解

- 全部 Pillow で書くのは大変なので、**段階導入**:
  - 第1段階: `table` と `timeline` だけ実装(最頻出)
  - 第2段階: `flow` を Mermaid 経由で実装
  - 第3段階: スクショ取り込みフロー整備
- やまぱんさんが原稿で `**タイプ**: table` と書いたら自動でテーブル描画されるようにする

### script.md でのテンプレ例

```markdown
### スライドXX - Git vs GitHub 比較 (60秒)

**タイプ**: table
**見出し**: 一目でわかるGitとGitHub
**テーブル**:
| 観点 | Git | GitHub |
|---|---|---|
| 役割 | 履歴管理の仕組み | 共同作業プラットフォーム |
| 場所 | ローカル | クラウド |
| 主な操作 | commit/branch/merge | Issue/PR/Actions |

**ナレ**:
```text
ここで一覧で見てみるのだ! ...
```
```

詳細実装ガイド: 別 reference (`slide-visuals-guide.md`) として今後拡充予定。

## 動画 mp4 concat の安全パターン

ffmpeg concat demuxer は **list.txt 内のパスが相対だと cwd 依存で失敗する**(`returned non-zero exit status 4294967294` の元凶):

```python
list_file.write_text(
    "".join(f"file '{p.resolve().as_posix()}'\n" for p in segs),  # 必ず resolve() で絶対化
    encoding="utf-8"
)
subprocess.run([..., "-i", str(list_file.resolve()), "-c", "copy", str(out.resolve())])
```

`Path.resolve()` で絶対化 + `as_posix()` で Windows パス区切りを `/` に。**両方やる**(`as_posix()` だけだと相対パスのまま forward slash になるだけで cwd 依存は解消されない)。

## スライドと音声のインデックス対応 (ep01 v3教訓・致命的バグ)

`script.json` が以下構造のとき:
```
slides[0] = {heading: "OP", narration: <OP用>}      # 仮想スライド
slides[1] = {heading: "今日のテーマ", narration: ...}  # 実コンテンツ1枚目
slides[2] = ...                                       # 実コンテンツ2枚目
```

`build_episode.py` で **`for i, s in enumerate(slides, start=1):` だと**:
- `slide_01.png` ← `render_content(slides[0])` = **「OP」テキストが描かれた空スライド**
- `slide_02.png` ← `render_content(slides[1])` = 今日のテーマ
- → 全画像が1枚ズレ

正しい実装:
```python
# slides[0] が "OP" heading なら、それは OP 音声専用。 content_slides を別取り出し。
op_narration = ""
content_slides = slides
if slides and slides[0].get("heading") == "OP":
    op_narration = slides[0]["narration"]
    content_slides = slides[1:]

# render
for i, s in enumerate(content_slides, start=1):
    render_content(s, slides_dir / f"slide_{i:02d}.png", ...)

# audio: slide_00(title)=op_narration、slide_NN=content_slides[N-1].narration
for i in range(total):
    text = op_narration if i == 0 else content_slides[i - 1]["narration"]
```

**症状**: 視聴者は「スライドが音声に1枚遅れてる」と感じる。
**検出方法**: `slide_01.png` を目視 → そこに heading「OP」とか空白のスライドが描かれていたらこのバグ。

## 生成パイプラインの索引ズレ防止 (一般則)

`script.md → script.json → 画像 + 音声 + 動画` のように **複数段階の変換** がある生成パイプラインでは、**段階間でインデックスがズレる** バグが頻発する。再発防止のため:

### ルール1: 仮想スライド(OP/EDの音声のみ等) は構造で区別する

JSON 上で **「描画する」スライドと「音声だけ」スライドが混在**するなら、`heading: "OP"` のような **マーカー** を使う or **別フィールド** (`op_narration`, `ed_narration`) に分離する。後段スクリプトは構造を見て分岐する。

### ルール2: 1段階の出力ごとに「期待件数」を print する

```python
print(f"[ok] rendered {total} slides (1 title + {len(content_slides)} content)")
print(f"[ok] generated {total} audio files")
print(f"[ok] {len(segs)} segments built")
```

→ 数字が一致しなければ即発見できる。

### ルール3: ファイル名のインデックスを「意味」とそろえる

- `slide_00.png` = title slide
- `slide_01.png` = content_slides[0] (← 実コンテンツ1枚目)
- `audio_00.wav` = OP 音声
- `audio_01.wav` = content_slides[0] の音声

→ **`slide_NN` と `audio_NN` は同じ瞬間に再生される** ことを保証する。

### ルール4: 試聴前に視覚チェックを1枚だけ手動でやる

フル動画生成は20-30分かかる。途中で1枚だけ目視確認すべきポイント:

- `slide_01.png` の見出しが期待通りか(「OP」とか空白だったらバグ)
- `audio_01.wav` を再生して、`slide_01` の見出しと文脈が合うか
- `slide_(末尾).png` が空白でないか

これだけで **致命的なインデックスズレ** は事前に潰せる。

### ルール5: 「修正→全部再生成」を避ける中間キャッシュ

スライド画像と音声は分離して `.png/.wav` で持つ。動画 concat だけ失敗したなら、画像/音声は再利用して concat だけリトライ。20分のフル再生成を毎回やらない。

## スライド生成の3軸チェックリスト (ep01教訓)

スライド画像を Pillow で生成するときは、フル動画ビルド (20-30分) 前に **3軸を必ず手動チェック**:

### 1. フォント軸 (字形の有無)

そのフォントに字形があるかを確認。和文フォント (BIZ UDGothic / Yu Gothic / Meiryo) の典型欠落:

| 欠落するもの | 代替 |
|---|---|
| 絵文字 (❌⭕🌱📌等) | テキストラベル (`BAD:`/`GOOD:`) / Pillow 描画 |
| 一部の記号 (♥♦等) | `★◆●▲` 等の基本記号を使う |
| 特殊な漢字 (旧字体・人名外字) | 別フォント / ふりがな化 |

検証: 生成画像を目視。豆腐 (□) があったらフォント欠落。

### 2. レイアウト軸 (画面領域の確保)

オーバーレイ (アバター/ワイプ/字幕焼き込み) と本コンテンツが **重ならない**:

- アバター用に **右下 X% を予約領域** として確保 (例: 380px幅×540px高)
- table/timeline 等の自動レイアウトは **`avail_w = W - margin - mascot_reserve`** で計算
- 字幕焼き込みする場合は **下 10-15%** を字幕用予約

検証: アバター付き mp4 でなく、まず **スライド単体 PNG** で「予約領域に何も無いか」を見る。

### 3. 文字種軸 (和欧混植・改行・読み速度)

CJK 文字と ASCII 文字が混在するときの可読性ルール:

- **半角英数字の前後に半角スペース**: `Git のコミット` (`Gitのコミット` は詰まる)
- **長い英単語の改行**: `pull_request_review_comment` 等は折り返し配慮(改行可能位置を考慮)
- **数字+単位**: 必ず半角スペース: `120 分` / `1080 px` (ASCII 数字)、`30秒` でも可 (全角混じり)

自動化案: 変換スクリプトで `re.sub(r"([ぁ-んァ-ヶ一-龥])([A-Za-z0-9])", r"\1 \2", text)` を入れる(narration 除外)。

### 検証フロー

フル動画生成 (20-30分) する前に **1スライドだけ手動 PNG 出力 → 目視チェック**:

```python
# Quick sanity check before full build
render_slide(test_slide, "test.png", page=1, total=1, brand="test")
# Open test.png and verify: no tofu / no overlay collision / spaces in JP-EN
```

これだけで「フル生成→違和感→全部やり直し (合計 60-90分ロス)」が防げる。

## 関連スキル

- 動画パイプライン本体: [SKILL.md](../SKILL.md)
- SDXL での顔生成 (リアル系アバター): [avatar-generation-sdxl.md](avatar-generation-sdxl.md)
- ffmpeg フィルタ詳細: [ffmpeg-advanced-filters.md](ffmpeg-advanced-filters.md)
