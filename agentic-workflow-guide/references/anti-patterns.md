# Anti-Patterns

エージェントワークフローで避けるべきアンチパターン集。

## 概要

| アンチパターン       | 問題                   | 対策                   |
| -------------------- | ---------------------- | ---------------------- |
| God Agent            | 1 エージェントに全責務 | SRP で分割             |
| Context Overload     | 不要な情報を大量に渡す | ISP で最小化           |
| Silent Failure       | エラーを無視して続行   | Fail Fast で即停止     |
| Infinite Loop        | 終了条件なしのループ   | 最大イテレーション設定 |
| Big Bang             | 一度に大きく作る       | Iterative で小さく回す |
| Premature Complexity | 最初から複雑な設計     | Simplicity First       |
| Black Box            | 内部状態が見えない     | Transparency           |
| Tight Coupling       | エージェント間の密結合 | Loose Coupling         |

---

## 詳細

### 1. God Agent

**1 エージェントに全責務を詰め込む**

#### 症状

```
❌ 悪い例:
Agent: "検索して、分析して、レポート作成して、メール送信して..."
```

- 1 つのエージェントが複数の異なるタスクを担当
- プロンプトが肥大化
- デバッグが困難
- 部分的な変更が全体に影響

#### 対策

```
✅ 良い例:
Agent 1 (Searcher): "関連情報を検索"
Agent 2 (Analyzer): "情報を分析"
Agent 3 (Reporter): "レポート作成"
Agent 4 (Sender): "メール送信"
```

**適用原則:** SRP (Single Responsibility Principle)

---

### 2. Context Overload

**不要な情報を大量に渡す**

#### 症状

```
❌ 悪い例:
Agent に渡すコンテキスト:
- 全ファイルの内容
- 過去の会話履歴全て
- 関係ない設定情報
```

- コンテキストウィンドウの無駄遣い
- ノイズが多く本質が埋もれる
- コスト増加
- 処理時間増加

#### 対策

```
✅ 良い例:
Agent に渡すコンテキスト:
- このタスクに必要なファイルのみ
- 直近の関連する会話のみ
- 必要な設定項目のみ
```

**適用原則:** ISP (Interface Segregation Principle)

---

### 3. Silent Failure

**エラーを無視して続行**

#### 症状

```
❌ 悪い例:
try:
    result = agent.execute()
except:
    pass  # エラー無視
```

- エラーが発生しても処理が続く
- 問題が後工程まで伝播
- デバッグが困難
- 不正な結果が生成される

#### 対策

```
✅ 良い例:
try:
    result = agent.execute()
except AgentError as e:
    log.error(f"Agent failed: {e}")
    raise  # 即座に停止
```

**適用原則:** Fail Fast

---

### 4. Infinite Loop

**終了条件なしのループ**

#### 症状

```
❌ 悪い例:
while not evaluator.is_satisfied():
    result = generator.generate()
    # 終了条件なし
```

- 永遠に終わらない可能性
- リソース枯渇
- コスト爆発

#### 対策

```
✅ 良い例:
MAX_ITERATIONS = 5
for i in range(MAX_ITERATIONS):
    result = generator.generate()
    if evaluator.is_satisfied():
        break
else:
    log.warning("Max iterations reached")
```

**適用原則:** 明示的な終了条件

---

### 5. Big Bang

**一度に大きく作る**

#### 症状

```
❌ 悪い例:
1. 全機能の設計を完了
2. 全エージェントを一度に実装
3. 最後にまとめてテスト
→ 問題発見が遅れ、修正コスト大
```

- 全てを一度に実装
- テストが後回し
- 問題の発見が遅い
- 修正範囲が広い

#### 対策

```
✅ 良い例:
1. 最小機能を設計
2. 1エージェントを実装
3. テスト・検証
4. 次のエージェントを追加
5. 繰り返し
```

**適用原則:** Iterative Refinement

---

### 6. Premature Complexity

**最初から複雑な設計**

#### 症状

```
❌ 悪い例:
最初から:
- 10エージェントの複雑なワークフロー
- 複雑な条件分岐
- 高度なエラーハンドリング
→ 実際には必要なかった
```

- YAGNI (You Aren't Gonna Need It) 違反
- 保守コスト増加
- 理解困難

#### 対策

```
✅ 良い例:
1. まず単一エージェントで試す
2. 問題が発生したら分割を検討
3. 必要に応じて複雑化
```

**適用原則:** Simplicity First, YAGNI

**Anthropic の推奨:**

> "Start with simple prompts, optimize them with comprehensive evaluation, and add multi-step agentic systems only when simpler solutions fall short."

---

### 7. Black Box

**内部状態が見えない**

#### 症状

```
❌ 悪い例:
Agent: (何も出力せず処理中...)
User: "何をしているの？"
```

- 進捗が不明
- 問題発生時に原因特定困難
- ユーザーが不安

#### 対策

```
✅ 良い例:
Agent: "Step 1/3: データを取得中..."
Agent: "Step 2/3: 分析中..."
Agent: "Step 3/3: レポート生成中..."
```

**適用原則:** Transparency

---

### 8. Tight Coupling

**エージェント間の密結合**

#### 症状

```
❌ 悪い例:
Agent A の出力形式を変更
→ Agent B, C, D も全て修正が必要
```

- 変更の影響範囲が広い
- テストが困難
- 再利用が困難

#### 対策

```
✅ 良い例:
- 標準化されたインターフェース
- 各エージェントは独立してテスト可能
- 変更が局所化される
```

**適用原則:** Loose Coupling

---

## チェックリスト

ワークフロー設計時にこのリストで確認：

```markdown
- [ ] God Agent: 1 つのエージェントに責務を詰め込みすぎていないか？
- [ ] Context Overload: コンテキストを過剰に渡していないか？
- [ ] Silent Failure: エラーを無視して続行していないか？
- [ ] Infinite Loop: 終了条件なしのループはないか？
- [ ] Big Bang: 一度に大きく作ろうとしていないか？
- [ ] Premature Complexity: 必要以上に複雑にしていないか？
- [ ] Black Box: 内部状態が見えなくなっていないか？
- [ ] Tight Coupling: エージェント間が密結合になっていないか？
```

---

## 関連ドキュメント

- [design-principles.md](design-principles.md) - 設計原則の詳細
- [review-checklist.md](review-checklist.md) - レビューチェックリスト
