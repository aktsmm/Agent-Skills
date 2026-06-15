# ffmpeg Advanced Filters

スライド動画 + アバター動画の合成で使う、頻出フィルタ集。

## 矩形 overlay (最速)

```bash
ffmpeg -y -i base.mp4 -i avatar.mp4 \
  -filter_complex "[1:v]scale=360:-1[av];[0:v][av]overlay=W-w-48:H-h-48:shortest=1[v]" \
  -map "[v]" -map 0:a -c:v libx264 -pix_fmt yuv420p -c:a copy out.mp4
```

- `scale=360:-1`: アバター幅 360px、アスペクト維持
- `overlay=W-w-48:H-h-48`: 右下マージン 48px
- `shortest=1`: 短いほうに合わせる

## 円形マスク + アクセントリング (1パス)

```bash
ffmpeg -i base.mp4 -i avatar.mp4 \
  -filter_complex "
    [1:v]
    crop=min(iw\,ih):min(iw\,ih),
    scale=S:S,
    format=yuva420p,
    geq=
      r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':
      a='if(lte(hypot((X-CX)/CX,(Y-CY)/CY),1),255,0)',
    geq=
      r='if(between(hypot((X-CX)/CX,(Y-CY)/CY),0.94,1),R,r(X,Y))':
      g='if(between(hypot((X-CX)/CX,(Y-CY)/CY),0.94,1),G,g(X,Y))':
      b='if(between(hypot((X-CX)/CX,(Y-CY)/CY),0.94,1),B,b(X,Y))':
      a='if(lte(hypot((X-CX)/CX,(Y-CY)/CY),1),255,0)'
    [av];
    [0:v][av]overlay=W-w-M:H-h-M:shortest=1[v]
  " ...
```

- `S` = アバター直径、`CX=CY=S/2`、`M` = マージン、`R,G,B` = リング色
- 1段目 `geq`: alpha = 楕円判定 `hypot((X-cx)/rx,(Y-cy)/ry) <= 1`
- 2段目 `geq`: リング = `between(.., 0.94, 1)` の範囲だけ色置換 (リング太さは 0.94 を変えて調整、0.92 = 太い)

## よくある間違い

| 症状 | 原因 / 対処 |
|---|---|
| `crop=min(iw,ih):...` でエラー | filter_complex 内のカンマは `\,` でエスケープ |
| 円が楕円になる | `crop` で先に正方形化していない |
| 透過が効かない | `format=yuva420p` を忘れている。`yuv420p` は alpha 無し |
| リングが出ない | `between(...,0.94,1)` の `1` を超えてないか確認 (alphaが0になる) |
| concat 後に音声落ちる | `-c copy` ではなく `-c:v libx264 -c:a aac` で再エンコすると安定 |

## 字幕焼き込み

```bash
ffmpeg -i in.mp4 -vf "subtitles=in.srt:force_style='FontName=BIZ UDGothic,FontSize=22,OutlineColour=&H80000000,BorderStyle=3'" -c:a copy out.mp4
```

`OutlineColour` + `BorderStyle=3` で半透明黒帯背景に。ミュート視聴向け。

## BGM ミックス

```bash
ffmpeg -i in.mp4 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.08,aloop=loop=-1:size=2e9[bg];[0:a][bg]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy out.mp4
```

`volume=0.08` がナレを潰さない目安。`aloop` で BGM をループ。

## concat 安定パターン

```bash
# list.txt:
# file 'seg_00.mp4'
# file 'seg_01.mp4'
ffmpeg -y -f concat -safe 0 -i list.txt -c:v libx264 -pix_fmt yuv420p -r 30 -an out.mp4
```

- 各 seg を **同じ codec / fps / sample rate** で作っておく
- `-c copy` はストリームコピーで高速だが、コンテナ差異で失敗しやすい → 再エンコのほうが安全

## パフォーマンス目安 (1分動画 / RTX 4060Ti)

| 処理 | 時間 |
|---|---|
| 矩形 overlay | 5〜10 秒 |
| geq 楕円マスク (1パス) | 30〜60 秒 |
| 字幕焼き込み | 10〜20 秒 |
| BGM ミックス | 5〜10 秒 |
