---
name: teams-desktop-automation
description: "Prepare and verify Microsoft Teams desktop chat drafts with Windows UI Automation, stopping before send. Use for Teamsチャット下書き, デスクトップTeams操作, 宛先確認, メッセージ入力, or when Teams Web/CDP is unavailable."
argument-hint: "宛先の表示名・社内メールアドレス、本文、期待するTeamsアカウント"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Teams Desktop Automation

## When to Use

- Teams デスクトップでチャット本文を下書きするとき
- Teams Web / Playwright / CDP が使えず、認証済みデスクトップアプリを使うとき
- 宛先と本文を検証し、ユーザーの最終送信待ちで止めるとき

使わない: 会議参加、通話、チャネル投稿、ファイル共有、メッセージ送信後の編集・削除。

## Safety Contract

- **送信しない。** 宛先と本文を入力した画面で停止し、最終の送信ボタンはユーザー本人に押してもらう。
- 宛先は表示名だけで決めず、組織ディレクトリ等で確認したメールアドレスと照合する。
- Teams のウィンドウタイトルで宛先・期待アカウントを確認する。候補が0件または複数なら停止する。
- 既存下書きが別内容なら上書きしない。同一本文なら再入力せず成功扱いにする。
- `SendKeys`、送信ボタンの click / `InvokePattern`、座標クリックを実行しない。
- 認証、MFA、アカウント切替が必要なら、対象と完了の目印を示してユーザーへ引き継ぐ。

## Workflow

1. 宛先の表示名、社内メールアドレス、期待する Teams アカウント、本文を確定する。
2. Teams が起動中か確認する。必要なら helper の `Open` で対象チャットを開く。この操作は Teams を前面化し得るため、実行前にユーザーへ知らせる。
3. `Inspect` でウィンドウタイトル、composer、既存下書き、送信ボタンを確認する。
4. `Draft` で本文を入力する。異なる既存下書きがあれば停止する。
5. `ready-for-user-send`、`DraftMatches=true`、`SendEnabled=true`、`SendActionPerformed=false` を確認する。
6. 必要なら `-ScreenshotPath` で現在画面を保存し、ユーザーへ送信操作を依頼して止める。

## Commands

PowerShell 7 (`pwsh`) で実行する。

```powershell
$script = '.github/skills/teams-desktop-automation/scripts/Set-TeamsDesktopDraft.ps1'

& $script -Mode Open `
  -RecipientDisplayName '<display-name>' `
  -RecipientEmail '<user@example.com>' `
  -ExpectedAccount '<signed-in-account@example.com>'

& $script -Mode Inspect `
  -RecipientDisplayName '<display-name>' `
  -RecipientEmail '<user@example.com>' `
  -ExpectedAccount '<signed-in-account@example.com>'

& $script -Mode Draft `
  -RecipientDisplayName '<display-name>' `
  -RecipientEmail '<user@example.com>' `
  -ExpectedAccount '<signed-in-account@example.com>' `
  -Message '<message>' `
  -ScreenshotPath 'output/teams-draft.png'
```

## Failure Handling

- `Open` 後に対象タイトルがまだ出ない場合は、同じ `Draft` を連打せず `Inspect` を1回行う。
- UIA が composer を公開しない場合は未確認として止める。Web 版への自動迂回やアプリ再起動は行わない。
- `Draft` の結果が曖昧なら再入力しない。現在値を `Inspect` で読み、同一本文か確認する。
- アプリの foreground、入力欄 focus、送信ボタンの操作は完了条件に含めない。

## Validation

```powershell
& .github/skills/teams-desktop-automation/scripts/Test-TeamsDesktopDraft.ps1
```

実機テストは既存チャットを壊さないよう、`Inspect` を先に実行する。`Draft` は実際にユーザーへ見せる本文が確定している場合だけ使う。

## Done Criteria

- 対象表示名と期待アカウントがウィンドウタイトルで一致する
- composer の下書きが要求本文と完全一致する
- 送信ボタンが存在し有効である
- `SendActionPerformed=false` で終了する
- ユーザーへ「送信ボタンを押してください」と明示して停止する
