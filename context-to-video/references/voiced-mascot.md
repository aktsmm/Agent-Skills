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

## 英単語の読みは原稿でカタカナ化する (必須)

VOICEVOX は英単語のスペルを誤読する。**ナレ原稿には最初からカタカナで書く** ことを徹底:

| 原則 | 例 |
|---|---|
| 「日本人エンジニアが普段会話で発音している読み」を採用 | Azure → アジュール |
| 製品名は Microsoft 公式日本語サイト・GitHub Docs 日本語版の表記を最優先 | Copilot → コパイロット |
| 公式読みが無ければエンジニア界隈の一般慣用 | repository → リポジトリ |
| 迷ったら検索: `<英単語> 読み方 エンジニア` | YAML → ヤメル or ワイエーエムエル |
| 原稿側のナレ文字列に半角英字を残さない (数字とURLは例外) | — |

頻出辞書例 (シリーズ・チャンネルごとに専用辞書を持つこと):
- Azure → アジュール
- GitHub → ギットハブ
- Git → ギット
- Copilot → コパイロット
- Codespaces → コードスペース
- pull request → プルリクエスト
- repository → リポジトリ
- README → リードミー
- 2FA → ツーエフエー
- API → エーピーアイ
- CI/CD → シーアイ シーディー

シリーズ用辞書テンプレ: `<content-workspace>/_shared/voicevox-readings.md`
将来的に `content_to_script.py` で **辞書ベース自動置換** を実装すると、原稿に英字が残っても変換時にカタカナ化される(両方の保険)。

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

## 関連スキル

- 動画パイプライン本体: [SKILL.md](../SKILL.md)
- SDXL での顔生成 (リアル系アバター): [avatar-generation-sdxl.md](avatar-generation-sdxl.md)
- ffmpeg フィルタ詳細: [ffmpeg-advanced-filters.md](ffmpeg-advanced-filters.md)
