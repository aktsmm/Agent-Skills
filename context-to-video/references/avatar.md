# Avatar Mode (SadTalker)

GPU(VRAM 8GB+)があるなら、SadTalker で右下にアバターを足せる。完全無料・ローカル完結。

## 制約 / 期待値

- フォトリアル顔は若干違和感がある(SadTalker 256px の限界)。`--size 512 --enhancer gfpgan` で改善するが処理時間 2〜3 倍
- 顔は **正面・笑顔・髪が顔にかかっていない** ものほど安定
- thispersondoesnotexist.com は **西洋顔バイアスが強い**。日本人/アジア風が必要なら Stable Diffusion で自前生成 (推奨) かやまぱんさん自身の写真
- イラスト/アニメ顔も使えるが、SadTalker は実写最適化なので口パクの自然さは下がる

## 初回セットアップ (30〜40分)

```powershell
# 1. Python 3.10 用意 (SadTalker は 3.10 まで。3.12 は不可)
uv python install 3.10

# 2. 専用 venv
cd <project>\avatar
uv venv --python 3.10 .\venv
$py = ".\venv\Scripts\python.exe"

# 3. torch CUDA 12.1 (大: ~2GB)
& $py -m pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu121

# 4. numpy ダウングレード (torch 2.1.2 は NumPy 1.x 必須)
& $py -m pip install "numpy==1.23.5"

# 5. SadTalker 依存
& $py -m pip install face_alignment==1.3.5 imageio==2.19.3 imageio-ffmpeg==0.4.7 librosa==0.9.2 numba pydub==0.25.1 scipy==1.10.1 kornia==0.6.8 tqdm yacs==0.1.8 pyyaml joblib==1.1.0 scikit-image==0.19.3 basicsr==1.4.2 facexlib==0.3.0 gfpgan av safetensors resampy==0.3.1

# 6. SadTalker 本体
git clone --depth 1 https://github.com/OpenTalker/SadTalker.git

# 7. ffmpeg + ffprobe (pydub が ffprobe を呼ぶので両方必要)
winget install --id Gyan.FFmpeg -e

# 8. チェックポイントDL (2.3GB) → see scripts/download_models.ps1
```

## チェックポイントDL

`scripts/download_models.ps1` を実行(本リポジトリに同梱)。中身は SadTalker 公式の bash 版を PowerShell に翻訳したもので、以下を `SadTalker/checkpoints/` と `SadTalker/gfpgan/weights/` に配置する:

- mapping_00109-model.pth.tar (149MB)
- mapping_00229-model.pth.tar (148MB)
- SadTalker_V0.0.2_256.safetensors (692MB)
- SadTalker_V0.0.2_512.safetensors (692MB)
- alignment_WFLW_4HG.pth, detection_Resnet50_Final.pth, GFPGANv1.4.pth, parsing_parsenet.pth (計700MB)

## 顔画像の選び方

| 出所 | 品質 | 著作権 | 日本人風 |
|---|---|---|---|
| 自分の顔写真 | ◎ | 完全クリア | (自分) |
| Stable Diffusion ローカル生成 | ◎ | クリア | プロンプトで自由制御 |
| thispersondoesnotexist.com | ○ | クリア (CC0扱い) | △ 西洋寄り |
| ICONS8 generated photos | ○ | 要ライセンス確認 | フィルタあり |
| イラスト/フリー素材 | △ (口パク違和感) | 各ライセンスに従う | 自由 |

**YouTube 定期投稿で本キャラ固定するなら Stable Diffusion で1枚生成 → 永久使用が最強**。プロンプト例:

```
photorealistic portrait of a Japanese woman in her 30s, friendly smile,
news anchor style, clean background, soft lighting, high detail
```

## 前処理: SD 生成顔は要パディング

Stable Diffusion などで生成した「顔アップ」画像をそのまま渡すと、SadTalker の `--preprocess full` が OpenCV ROI assertion で失敗する。

**対処**: 元画像を 720x720 にリサイズし、1024x1024 白背景にセンター配置してから渡す。

```python
from PIL import Image
src = Image.open(SRC).convert("RGB").resize((720, 720), Image.LANCZOS)
pad = Image.new("RGB", (1024, 1024), "white")
pad.paste(src, ((1024 - 720) // 2, (1024 - 720) // 2))
pad.save(FACE_JPG, quality=95)
```

加えて、SD 生成のヘッドショットには **`--preprocess crop`** のほうが安定する (`full` は背景含む全身想定)。

## 推奨コマンド (style別)

| 元画像タイプ | preprocess | 備考 |
|---|---|---|
| 普通の証明写真風 | `full` | デフォルト |
| SD 生成ヘッドショット (バストアップ) | `crop` + パディング | OOM/ROIエラー回避 |
| 全身ポートレート | `full` | 動きを許容するなら `--still` 外す |
| イラスト/アニメ | `crop` | 口パクの自然さは下がる |

## 推論コマンド

```powershell
$py = ".\venv\Scripts\python.exe"
cd SadTalker
& $py inference.py `
  --driven_audio  <path>\audio_00.mp3 `
  --source_image  ..\input\face.jpg `
  --result_dir    ..\clips `
  --still --preprocess full --size 256
```

オプション:
- `--still`: 頭の動きをほぼ止める(安定優先)。外すと頭が動くが破綻リスク上昇
- `--preprocess full`: 全身を含めずバストアップ
- `--size 512 --enhancer gfpgan`: 高解像度+顔修復 (処理 2〜3 倍)

## ffmpeg 楕円マスク合成

スクエア overlay の代わりに円形ワイプにする。`scripts/ellipse_overlay.py` 参照。

filter graph (核):

```
[1:v]crop=min(iw\,ih):min(iw\,ih),scale=S:S,format=yuva420p,
geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lte(hypot((X-S/2)/(S/2),(Y-S/2)/(S/2)),1),255,0)',
geq=r='if(between(hypot(..,..),0.94,1),56,r(X,Y))':...  ← リング描画
[av];
[0:v][av]overlay=W-w-M:H-h-M:shortest=1[v]
```

ポイント:
- `crop=min(iw,ih):min(iw,ih)` で中央スクエア化
- `format=yuva420p` で alpha 必須
- `geq` の `a=` 式で楕円判定 `hypot((X-cx)/rx, (Y-cy)/ry) <= 1`
- リングは 2段目の `geq` で `between(.., 0.94, 1)` の範囲だけ色を上書き

## 推論時間の目安 (RTX 4060 Ti 16GB)

| ナレ長 | 256px | 512px+GFPGAN |
|---|---|---|
| 5 秒 | 〜90 秒 | 〜3 分 |
| 15 秒 | 〜2 分 | 〜5 分 |
| 30 秒 | 〜3 分 | 〜8 分 |

→ 8スライド 2分動画で約 20〜25 分(256px)

## トラブル

| 症状 | 対処 |
|---|---|
| `FileNotFoundError: ffprobe` | `winget install Gyan.FFmpeg` + PATH 通す。`pydub` は ffprobe 必須 |
| `UserWarning: Failed to initialize NumPy` | `pip install "numpy==1.23.5"` で 1.x に固定 |
| `face_alignment` インストール失敗 (Python 3.12) | Python 3.10 を使う (`uv python install 3.10`) |
| OpenCV ROI assertion failure | SD ヘッドショットを `--preprocess full` で渡している。`crop` + 1024x1024 白パディングへ |
| 顔が検出されない | `--preprocess crop` に変更 / 顔がはっきり写った写真に差し替え |
| 口パクが完全に外れる | 音声が極端に短い (<1秒) と起きやすい。短いセグメントは結合 |
| OOM | `--size 256` に下げる / 1音声ずつ処理 (本リポの `add_avatar.py` 実装済み) |
| 単発で exit code 3221226505 | 一時的な CUDA blip。同じ引数で単体リトライすれば通ることが多い |
| OpenCV MP4V タグ警告 | 無視可 (出力 mp4 は正常) |

## 商用代替

無料 SadTalker は **品質・SLA・商用ライセンス** で限界がある。本格運用は:

- **Azure TTS Avatar** (Standard avatar Lisa 等、$0.30/分〜) → [production-upgrade.md](production-upgrade.md)
- **HeyGen / D-ID / Synthesia** (SaaS、月額)
- **Microsoft Foundry の TTS Avatar GUI** (ノーコード)
