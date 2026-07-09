# WorkIQ Query Playbook

Run all six query lanes for the confirmed colleague and period. Record zero-result or failed lanes instead of silently skipping them.

## Q1: Direct Messages

```text
{name} との 1:1 のダイレクトメッセージを {period} の分を教えてください。主なトピックや相談内容のサマリーもお願いします。
```

## Q2: Shared Group Chats

```text
{name} と私の両方が参加したグループチャットを {period} の分で教えてください。どんな話題・プロジェクトの会話だったか概要もお願いします。
```

## Q3: Mutual Mentions

```text
{period} に {name} が私をメンションしたメッセージ、または私が {name} をメンションしたメッセージを教えてください。
```

## Q4: Shared Meetings

```text
{period} に {name} と私の両方が参加した会議の一覧を教えてください。会議名と日時もお願いします。
```

## Q5: Email Threads

Include direct mail, To/Cc combinations, and threads containing both people.

```text
{period} に {name} と私が関与したメールを教えてください。To での直接往来だけでなく、片方が To で片方が Cc に入っているもの、または同じスレッドに両者がいるものも含めてください。件名と概要、両者の関与（To / Cc / From）をリストで。
```

## Q6: Shared Files

```text
{period} に {name} と私が共同で編集または共有した SharePoint・OneDrive のファイルを教えてください。
```

Before structuring evidence, confirm the actual purpose of major meetings or chats with the user. Display names can misrepresent the underlying activity.
