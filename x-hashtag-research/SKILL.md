---
name: x-hashtag-research
description: "Collect and analyze public X posts from hashtags to discover primary sources, official docs, related GitHub repos, and reusable images. Use when researching launch-day announcements, event hashtags like #MSBuild or #MicrosoftBuild, keynote reactions, or when you want to turn noisy X posts into a structured research note under research/. X専用のハッシュタグ調査 workflow。"
argument-hint: "対象ハッシュタグ、時間窓、件数、保存先メモ名"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# X Hashtag Research

X の live search を起点に、公開投稿を大量収集し、一次情報 URL、関連 GitHub repo、画像、論点を research 配下へ整理する workspace 用 skill。

## When to Use

- X のハッシュタグからイベント当日の発表を追いたいとき
- `#MSBuild` や `#MicrosoftBuild` のような event hashtag を直近数時間で総ざらいしたいとき
- keynote 直後に、一次情報 URL と repo の導線を先に集めたいとき
- noisy な実況投稿から、Microsoft Learn / blog / GitHub / session repo に収束させたいとき
- 画像付き投稿も research asset として残したいとき

## Scope

- この skill は X 専用にする
- Bluesky、LinkedIn、YouTube comments などは対象外
- それらを扱いたい場合は別 skill に切り出す

## Default Profile

明示指定がないときの既定候補はこれ。

- time window: `直近 4 時間`
- target posts: `500`
- raw artifact: `tmp/`
- research note: `research/YYYYMMDD-<topic>-from-x.md`
- curated images: `research/assets/YYYYMMDD-<topic>-from-x/`
- bulk images: `research/images/YYYYMMDD-<topic>-from-x/`

## Always Confirm Before Running

既定値はあるが、毎回この 4 点は確認する。

1. 対象ハッシュタグ
2. 時間窓
3. 目標件数
4. 保存先メモ名

ユーザーが省略した場合は既定値を提案して確認を取る。勝手に `4時間 / 500件` で走らせない。

## Minimal Browser Fallback

`browser-max-automation` が無い環境でも、この skill の進め方は変えない。

- 使えるブラウザ系ツールで、最低限次ができればよい
  - X の live search を開く
  - 投稿 URL、時刻、本文、画像 URL を取る
  - 下へスクロールして追加投稿を読む
- 構造化抽出が弱い環境でも、順番は固定する
  1. raw 投稿の保存
  2. visible domain / card title で粗く分類
  3. 高シグナルな一次情報だけ深掘る
- 全件自動化にこだわらず、公式アカウント、live blog 導線、代表画像を優先する

この skill の本体はブラウザ操作のコツではなく、SNS ノイズを一次情報へ収束させる順番にある。

## Workflow

1. 収集対象を固定する
   対象ハッシュタグ、時間窓、件数目標、主目的、research の保存先を決める。

2. live search から効率よく収集する
   利用可能なブラウザ系ツールで `article` 相当の単位を構造化抽出し、status URL を主キーに重複排除する。

3. raw artifacts を先に保存する
   `tmp/<slug>-posts-raw.json` と batch 単位の中間 JSON を残す。

4. ローカル分類を先にやる
   rawText、tweetText、display text、X card の visible domain から theme、domain、repo、image candidates を作る。

5. 高シグナルリンクだけ深掘る
   全 t.co を解決せず、高頻度リンク、公式アカウント、画像付き高シグナル投稿、repo 名が半分読めている投稿だけを追う。

6. research ノートは source-centric に書く
   投稿の感想ではなく、投稿がどの一次情報へ収束したかを正本にする。

7. 画像は 2 層で保存する
   curated set は 5〜10 枚、bulk は 20〜30 枚程度を目安にする。

8. 再現可能な成果物で終える
   research ノート、raw JSON、主要一次情報 URL、画像保存先、必要なら manifest 追記まで揃える。

## Branching Rules

- X live search が使える場合: live search を正本にして収集する
- X live search が不安定な場合: 公式アカウント、live blog、official blog、repo 導線付き投稿を優先する
- 短縮 URL 解決が重い場合: 全解決しない。高頻度・高シグナルだけ解決する
- 画像が多すぎる場合: curated を先に確保し、bulk は上限を切る

## Quality Gates

- 収集件数と時間窓の両方を満たしている
- 主要テーマが公開情報の塊として整理されている
- repo 名が切れている場合は本文・card title・公式 blog で補正している
- 画像保存先が research 配下で整理されている
- 元の公開投稿を改変した断定はしていない

## Efficiency Rules

- `tmp/*.json` に途中結果を保存して取り直しを避ける
- ローカル分類を先にやって、外部 fetch はその後
- 公式 blog の横断記事があるなら、それを hub にして個別記事へ降りる
- browser 固有 tips は抱え込みすぎない。必要なら `browser-max-automation` を使う

## Example Prompts

- `/x-hashtag-research #MSBuild と #MicrosoftBuild を直近4時間で500件以上集めて、一次情報と repo と画像を research に保存して`
- `/x-hashtag-research #Build2026 で GitHub Copilot app と Foundry まわりだけ拾って`
- `/x-hashtag-research #Ignite と #MicrosoftIgnite を2時間で300件、画像は代表8枚だけでいい`

## Related Customizations To Create Next

- ハッシュタグ research 結果を keynote research に差し込む prompt
- 保存画像から記事向きのものだけ選別する skill
- official blog / Learn / GitHub repo のみを二次整理する prompt
