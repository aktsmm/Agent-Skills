---
name: ascii-banner
description: "Generate ASCII-art text banners for terminals, READMEs, and CLI startup messages. Use when a user asks for an ASCII banner, text art, バナー, アスキーアート, or a decorative header for a script/README."
argument-hint: "バナーにしたい文字列、用途（README / CLI 起動メッセージなど）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# ASCII Banner

短い文字列を ASCII アートのバナーへ変換する Skill。デモ用の最小スキル。

## When to Use

- README の見出しや CLI 起動メッセージに装飾バナーを入れたいとき
- キーワード: `ASCII banner`, `テキストアート`, `アスキーアート`, `バナー`

## How to Generate

優先順位は次のとおり。

1. `pyfiglet`（Python）が使えるなら最優先。
   ```powershell
   python -c "import pyfiglet; print(pyfiglet.figlet_format('TEXT'))"
   ```
   未導入なら `pip install pyfiglet` を提案する（ユーザー確認後）。
2. `figlet` CLI が使えるなら次点。
3. どちらも無ければ、自前で box-drawing 文字を使った簡易バナーを生成する。

## Fallback Box Banner

ツールが無いときは、次の形でテキストを枠で囲んで出力する。

```text
+==============================+
|        TEXT GOES HERE        |
+==============================+
```

- 中央寄せにする
- 枠は `=` と `|`、角は `+`
- 横幅は文字列長 + 左右パディング 4 以上

## Output Rules

- 生成結果は ` ```text ` コードブロックで囲んで返す
- 余計な説明は付けず、バナーと「どの方式で生成したか」を 1 行添えるだけにする
