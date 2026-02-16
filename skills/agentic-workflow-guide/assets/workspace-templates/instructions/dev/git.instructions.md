# Git Commit Instructions

このプロジェクトでは **Conventional Commits** に従ったコミットメッセージを必須とします。
エージェントがコミットを作成する際は、以下のルールを厳守してください。

## フォーマット

```text
<type>(<scope>): <subject>

<body>

<footer>
```

## 1. Type (必須)

変更の種類を表す以下のいずれかのプレフィックスを使用してください。

- **feat**: 新機能 (A new feature)
- **fix**: バグ修正 (A bug fix)
- **docs**: ドキュメントのみの変更 (Documentation only changes)
- **style**: コードの動作に影響しない変更 (空白、フォーマット、セミコロン欠落など)
- **refactor**: バグ修正も機能追加も行わないコード変更 (A code change that neither fixes a bug nor adds a feature)
- **perf**: パフォーマンスを向上させるコード変更 (A code change that improves performance)
- **test**: テストの追加や既存テストの修正 (Adding missing tests or correcting existing tests)
- **chore**: ビルドプロセスやドキュメント生成などの補助ツールやライブラリの変更 (Changes to the build process or auxiliary tools)

## 2. Scope (任意)

変更の影響範囲を示す名詞を括弧内に記述します。
例: `feat(auth): add login logic`, `fix(api): handle timeout error`

## 3. Subject (必須)

変更内容の簡潔な説明。

- **命令形**を使用する (例: "add" ではなく "added" や "adds" は避ける。日本語の場合は「〜を追加」「〜を修正」と言い切る)
- 文末にピリオド `.` を付けない
- 英字の場合は先頭を小文字にする (固有名詞を除く)

## 4. Body (任意)

変更の動機や、以前の挙動との違いなどを詳細に記述します。

## 5. Footer (任意)

- **Breaking Changes**: 互換性のない変更がある場合は `BREAKING CHANGE:` で始める。
- **Issue References**: 関連する Issue 番号を記述する (例: `Closes #123`)

## エージェントへの指示

- 複数の論理的な変更を含む場合は、可能な限りコミットを分割してください。
- コミットメッセージは、変更内容を正確に反映させてください。「修正」のような曖昧な表現は避けてください。
- **Push 禁止**: ユーザーからの明示的な指示（例: "PR を作って" "push して"）がない限り、`git push` は行わないでください。作業はローカルコミットまでとします。
