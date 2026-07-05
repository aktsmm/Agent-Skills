# Avatar Generation with Stable Diffusion XL

SadTalker のソース顔を SDXL でローカル生成する。チャンネルマスコット/コース講師を**著作権クリア・固定キャラ・自由表情差分**で運用するための定石。

## なぜ自前生成か

| 出所 | 著作権 | 民族表現 | 表情差分 | 再現性 |
|---|---|---|---|---|
| thispersondoesnotexist.com | クリア | 西洋顔バイアス強 / 子供混入 | ✗ | ✗ |
| ストック素材 / 友人写真 | 要許諾 | 自由 | ✗ | ✗ |
| 自分の写真 | クリア | 自由 | ✗ (実写撮影必要) | ◎ |
| **SD ローカル生成** | クリア | 自由 | ◎ (seed+末尾差替え) | ◎ (seed固定) |

## スタック (VRAM 6GB+ 推奨)

```powershell
uv venv --python 3.12 .\sd-venv
uv pip install --python .\sd-venv\Scripts\python.exe `
  torch torchvision --index-url https://download.pytorch.org/whl/cu121
uv pip install --python .\sd-venv\Scripts\python.exe `
  diffusers transformers accelerate safetensors sentencepiece pillow
```

`uv venv` 直後は pip が無いので **必ず `uv pip install --python <venv>\Scripts\python.exe`** を使う(`& $py -m pip` は失敗する)。

## モデル選定

| モデル | 速度 | 品質 | 商用 | 用途 |
|---|---|---|---|---|
| `stabilityai/sdxl-turbo` | ⚡⚡⚡ (4 steps, 0.5秒/枚 @ 4060Ti) | ○ 512px | △ 非商用ライセンス | 候補スクリーニング |
| `stabilityai/stable-diffusion-xl-base-1.0` | ⚡ (30 steps) | ◎ 1024px | ◎ CreativeML OpenRAIL++ | 本番固定キャラ |
| `cagliostrolab/animagine-xl-3.1` | ⚡ | ◎ アニメ調 | △ 確認要 | VTuber風 |

→ **探索は SDXL Turbo、確定後の高解像度化は SDXL Base 1.0** が定石。

## プロンプト進化パターン

最初から完璧を狙わず、**5〜6回イテレーション**するのが効率的。

| 段階 | 焦点 | 例の追加トークン |
|---|---|---|
| v1 ベース | 民族・性別・年齢 | `Japanese woman, late 20s` |
| v2 雰囲気 | 表情・髪型 | `gentle smile, shoulder-length wavy bob` |
| v3 体型 | スリム化(必要なら) | `slim, slender, refined oval face, sharp jawline` |
| v4 服装 | 用途別 | `casual private wear, beige knit, no jewelry` |
| v5 撮影 | カメラ感 | `85mm portrait, shallow depth of field, soft window light` |
| v6 細部 | 抜け感・親しみ | `slightly droopy soft eyes, kind onee-san vibe` |

## Negative の決め技

| 入れるべき | 理由 |
|---|---|
| `cartoon, anime, illustration, 3d render` | 写実モデルでも稀にイラスト化する |
| `chubby, fat, plump, round face, double chin` | 「痩せ型」をしっかり出す |
| `wide face, puffy cheeks, broad shoulders` | 小顔・華奢に寄せる |
| `formal suit, business attire, necktie, blazer` | 「私服感」を出す |
| `multiple people, extra limbs, distorted face` | 解剖学エラー除去 |
| `watermark, text, logo, signature` | 学習データに混入してた透かし排除 |

## Seed 管理 (固定キャラ運用の核)

**seed を JSON に記録**しておけば、後で「同じ顔の表情差分」を作れる:

```json
{
  "mascot_name": "channel_mascot_v4",
  "model": "stabilityai/sdxl-turbo",
  "seed": 410597652899700,
  "size": 512,
  "steps": 4,
  "guidance": 0.0,
  "prompt": "photorealistic portrait of a slim Japanese woman in her late 20s, ...",
  "negative": "cartoon, anime, ..."
}
```

### 表情差分の作り方

同 seed + プロンプト末尾だけ差替え:

| 用途 | 末尾追加 |
|---|---|
| サムネ用驚き顔 | `surprised expression, raised eyebrows, slightly open mouth` |
| 真面目解説 | `serious thoughtful expression, slight smile` |
| お祝い回 | `bright cheerful smile showing teeth, joyful` |
| アウトロ | `looking to the side, three-quarter view, gentle smile` |

完全に同じ顔は保たれないが「兄弟姉妹レベルの同一性」は維持できる。

## 候補スクリーニングの定石

1. プロンプト v1 で **9〜12 枚**生成 (size 512, steps 4)
2. Pillow で 3x3 or 3x4 のコンタクトシートに合成、番号付き
3. ユーザーに見せて 1 枚選定
4. その seed をベースに次のバリエーション or 高解像度版

```python
def make_contact_sheet(paths, out, cols=3, thumb=384):
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*thumb, rows*thumb), "white")
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((thumb, thumb))
        sheet.paste(im, ((i%cols)*thumb, (i//cols)*thumb))
        # 左上に番号バッジ
        ...
    sheet.save(out, quality=88)
```

## SadTalker への引き渡し

SD 生成画像をそのまま SadTalker に投げると ROI エラーで落ちる。前処理する:

```python
src = Image.open(SD_PNG).convert("RGB").resize((720, 720), Image.LANCZOS)
pad = Image.new("RGB", (1024, 1024), "white")
pad.paste(src, ((1024-720)//2, (1024-720)//2))
pad.save(FACE_JPG, quality=95)
```

SadTalker 側の引数は `--preprocess crop` を使う。詳細: [avatar.md](avatar.md)

## 倫理・権利ガード

**やってはいけない**:
- 実在人物の名前をプロンプトに入れる ("吉高〇〇のような", "佐々木〇〇風" 等)
  - 用途を問わず、肖像権・パブリシティ権の侵害リスクがあるため**生成自体を断る**
- 著名キャラクター名・作品名 (Disney 等)
- 「子供」「underage」を示唆する語

**OK の代替**:
- 「親しみ系の笑顔・少し垂れ目・ナチュラル」のような **特徴語に翻訳**して使う
- 「20代後半 / 30代前半」などの年齢レンジ
- 完全に独立したキャラを seed 固定で運用

このガードは Skill 利用者に **拒否理由を簡潔に伝えて代替案を提示** すること。
