# Production Upgrade

無料 `edge-tts` の代替で顧客配布・常時運用に耐える構成に上げる手順。

## なぜ差し替えるか

| 項目 | edge-tts | Azure Speech 正規 |
|---|---|---|
| 認証 | なし (匿名) | サブスクキー or Entra ID |
| SLA | なし | 99.9% |
| 商用利用 | グレー | 明示OK |
| 安定性 | エンドポイント変更で突然停止リスク | 公式 |
| 機能 | Neural voices | + HD voices / Custom Neural Voice / **TTS Avatar** |

## Azure Speech (TTS) に差し替え

```powershell
pip install azure-cognitiveservices-speech
```

```python
import azure.cognitiveservices.speech as speechsdk

def tts_azure(text: str, out_path: str, voice: str = "ja-JP-NanamiNeural"):
    cfg = speechsdk.SpeechConfig(subscription=KEY, region=REGION)
    cfg.speech_synthesis_voice_name = voice
    cfg.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3
    )
    audio_out = speechsdk.audio.AudioOutputConfig(filename=out_path)
    synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=audio_out)
    synth.speak_text_async(text).get()
```

`scripts/build_video.py` の `tts()` をこれに差し替えるだけ。声名は edge-tts と同じものが多くそのまま使える。

参考: https://learn.microsoft.com/azure/ai-services/speech-service/

## Azure TTS Avatar (アバター動画)

スライド+アバター解説をやるなら Azure Speech の `Text to speech avatar` API。

- バッチ合成 → mp4 が返ってくる
- 標準アバター (Lisa 他) は申請不要、Custom Avatar は審査あり
- 既存スライド mp4 と ffmpeg `overlay` で右下ワイプ合成すれば「スライド+喋るLisa」になる

```powershell
ffmpeg -i slides_video.mp4 -i avatar.mp4 -filter_complex \
  "[1:v]scale=480:-1[av];[0:v][av]overlay=W-w-40:H-h-40" \
  -map 0:a -c:a copy out.mp4
```

公式: https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech-avatar/what-is-text-to-speech-avatar

## Entra ID 認証 (会社サブで disableLocalAuth=true の場合)

会社サブの Azure AI Services は API key 無効化ポリシーが当たっていることがある。その場合は `DefaultAzureCredential` で Bearer token を取得。

```python
from azure.identity import DefaultAzureCredential
cred = DefaultAzureCredential()
token = cred.get_token("https://cognitiveservices.azure.com/.default").token
cfg = speechsdk.SpeechConfig(auth_token=f"aad#{RESOURCE_ID}#{token}", region=REGION)
```

`RESOURCE_ID` は Speech リソースの完全な ARM ID (`/subscriptions/.../providers/Microsoft.CognitiveServices/accounts/<name>`)。
