# Refactoring Patterns

Common refactoring patterns for code simplification.

## Table of Contents

- [Conditional Simplification](#conditional-simplification)
- [Function Extraction](#function-extraction)
- [Early Returns](#early-returns)
- [Loop Optimization](#loop-optimization)
- [Error Handling](#error-handling)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Conditional Simplification

### Before: Nested Ternaries (❌)

```javascript
const status = isActive ? (isPremium ? "premium" : "active") : "inactive";
```

### After: Switch or If/Else (✅)

```javascript
function getStatus(isActive, isPremium) {
  if (!isActive) return "inactive";
  if (isPremium) return "premium";
  return "active";
}
```

---

## Function Extraction

### Before: Long Function (❌)

```javascript
function processOrder(order) {
  // Validate order
  if (!order.items || order.items.length === 0) {
    throw new Error("Order must have items");
  }
  if (!order.customer) {
    throw new Error("Order must have customer");
  }

  // Calculate total
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity;
  }

  // Apply discount
  if (order.coupon) {
    total = total * (1 - order.coupon.discount);
  }

  return { ...order, total };
}
```

### After: Extracted Functions (✅)

```javascript
function validateOrder(order) {
  if (!order.items?.length) {
    throw new Error("Order must have items");
  }
  if (!order.customer) {
    throw new Error("Order must have customer");
  }
}

function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function applyDiscount(total, coupon) {
  if (!coupon) return total;
  return total * (1 - coupon.discount);
}

function processOrder(order) {
  validateOrder(order);
  const subtotal = calculateTotal(order.items);
  const total = applyDiscount(subtotal, order.coupon);
  return { ...order, total };
}
```

---

## Early Returns

### Before: Deeply Nested (❌)

```javascript
function getUserDisplayName(user) {
  if (user) {
    if (user.profile) {
      if (user.profile.displayName) {
        return user.profile.displayName;
      } else {
        return user.email;
      }
    } else {
      return user.email;
    }
  } else {
    return "Anonymous";
  }
}
```

### After: Guard Clauses (✅)

```javascript
function getUserDisplayName(user) {
  if (!user) return "Anonymous";
  if (!user.profile) return user.email;
  return user.profile.displayName || user.email;
}
```

---

## Loop Optimization

### Before: Manual Loop (❌)

```javascript
const activeUsers = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].isActive) {
    activeUsers.push(users[i].name);
  }
}
```

### After: Array Methods (✅)

```javascript
const activeUserNames = users
  .filter((user) => user.isActive)
  .map((user) => user.name);
```

---

## Error Handling

### Before: Silent Catch (❌)

```javascript
try {
  const data = JSON.parse(response);
  return data;
} catch (e) {
  // Ignore error
}
```

### After: Explicit Handling (✅)

```javascript
function parseResponse(response) {
  try {
    return JSON.parse(response);
  } catch (error) {
    console.error("Failed to parse response:", error.message);
    return null;
  }
}
```

---

## Anti-Patterns to Avoid

### 1. Overly Compact Code

```javascript
// ❌ Too compact
const r = a
  .filter((x) => x.v > 0)
  .map((x) => ({ ...x, s: x.v * 2 }))
  .reduce((a, b) => a + b.s, 0);

// ✅ Clear and readable
const positiveItems = items.filter((item) => item.value > 0);
const withScores = positiveItems.map((item) => ({
  ...item,
  score: item.value * 2,
}));
const totalScore = withScores.reduce((sum, item) => sum + item.score, 0);
```

### 2. Unnecessary Abstraction

```javascript
// ❌ Over-engineered
class StringUtils {
  static isEmpty(str) {
    return str === '';
  }
}
if (StringUtils.isEmpty(name)) { ... }

// ✅ Simple and direct
if (name === '') { ... }
// or
if (!name) { ... }
```

### 3. Magic Numbers

```javascript
// ❌ Unclear intent
if (status === 3) { ... }

// ✅ Self-documenting
const STATUS_COMPLETED = 3;
if (status === STATUS_COMPLETED) { ... }
```

### 4. Dead Code

```javascript
// ❌ Unused code left in
function processData(data) {
  // Old implementation - keeping for reference
  // const result = oldProcess(data);

  const result = newProcess(data);
  return result;
}

// ✅ Clean
function processData(data) {
  return newProcess(data);
}
```

---

## Language-Specific Patterns

### TypeScript

```typescript
// ❌ Redundant type assertions
const user = getUser() as User;
const name = (user as User).name;

// ✅ Type guards
function isUser(obj: unknown): obj is User {
  return obj !== null && typeof obj === "object" && "name" in obj;
}

const user = getUser();
if (isUser(user)) {
  const name = user.name; // Type-safe
}
```

### Python

```python
# ❌ Verbose conditional
if x == True:
    return True
else:
    return False

# ✅ Direct
return x
```

### React/JSX

```jsx
// ❌ Unnecessary fragments
return (
  <>
    <div>Content</div>
  </>
);

// ✅ Direct
return <div>Content</div>;
```

---

## Summary

| Pattern          | Before                 | After                        |
| ---------------- | ---------------------- | ---------------------------- |
| Nested ternaries | `a ? (b ? c : d) : e`  | `if/else` or `switch`        |
| Deep nesting     | Multiple `if` levels   | Guard clauses + early return |
| Long functions   | 50+ lines              | Extract to smaller functions |
| Manual loops     | `for (let i = 0; ...)` | `map`, `filter`, `reduce`    |
| Silent errors    | Empty `catch` block    | Log or handle explicitly     |
| Magic values     | `if (status === 3)`    | Named constants              |

---

## Code Review Perspectives

コードレビュー時に確認すべき6つの観点（リファクタリング前後で活用）：

### 🐛 バグ・論理エラー
- ランタイムエラー、エッジケース、null/undefined 問題
- 境界値、空配列、空文字列の処理

### 🔒 セキュリティ
- XSS、インジェクション、機密データ露出
- 入力バリデーション、認証・認可チェック

### ⚡ パフォーマンス
- N+1 クエリ、不要な再レンダリング、メモリリーク
- 計算量の最適化、キャッシュの活用

### 📖 保守性・可読性
- 命名、コード構造、複雑度
- 関数の責務分離、モジュール化

### 🧪 テストカバレッジ
- 不足しているテストケース
- エッジケースのテスト

### 📚 ドキュメント
- コメント、JSDoc、README 更新
- API ドキュメント

## Feedback Format

レビュー・リファクタリング結果を以下の形式で整理：

- ❌ **Critical**: 必須修正（機能に影響）
- ⚠️ **Warning**: 推奨修正（品質に影響）
- 💡 **Suggestion**: 改善案（あると良い）
- ✅ **Positive**: 良い点（維持すべき）
