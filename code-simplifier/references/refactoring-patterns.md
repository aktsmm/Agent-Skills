# Refactoring Patterns

Behavior-preserving simplifications. The textbook before/after forms are omitted; this file keeps the decision table, the equivalence traps, and the review format.

## Summary

| Pattern                  | Before                                      | After                                    |
| ------------------------ | ------------------------------------------- | ---------------------------------------- |
| Nested ternaries         | `a ? (b ? c : d) : e`                       | `if/else` or `switch`                    |
| Deep nesting             | Multiple `if` levels                        | Guard clauses + early return             |
| Long functions           | 50+ lines                                   | Extract to smaller functions             |
| Manual loops             | `for (let i = 0; ...)`                      | `map`, `filter`, `reduce`                |
| Silent errors            | Empty `catch` block                         | Log or handle explicitly                 |
| Magic values             | `if (status === 3)`                         | Named constants                          |
| Over-compact chains      | One-letter names across `filter/map/reduce` | Named intermediate values                |
| Single-use wrapper class | `StringUtils.isEmpty(s)`                    | Inline the expression                    |
| Commented-out code       | "Keeping for reference"                     | Delete; history lives in version control |
| Redundant assertions     | `(x as User).name`                          | Type guard                               |

## Equivalence Traps

A simplification that looks equivalent can change behavior. Check these before applying:

- `if x == True: return True / else: return False` becomes `return x == True` (or `bool(x)` only when `x` is known to be `bool`); `return x` leaks non-boolean values.
- `name === ''` and `!name` differ for `null`, `undefined`, `0`, and `NaN`.
- `a || b` and `a ?? b` differ for `0`, `''`, and `false`.
- Replacing an empty `catch` with logging plus `return null` changes the return value (`undefined` -> `null`) and adds output; confirm callers and log policy.
- Converting a loop to `map`/`filter` drops early `break`/`return` and may change evaluation order or side effects.
- Extracting a function can change `this`, closure capture, or exception timing.

---

## Code Review Perspectives

観点: バグ・論理エラー（境界値、null、空配列）、セキュリティ（入力検証、認可、機密露出）、パフォーマンス（N+1、再レンダリング）、保守性、テスト不足、ドキュメント更新。

## Feedback Format

レビュー・リファクタリング結果を以下の形式で整理：

- ❌ **Critical**: 必須修正（機能に影響）
- ⚠️ **Warning**: 推奨修正（品質に影響）
- 💡 **Suggestion**: 改善案（あると良い）
- ✅ **Positive**: 良い点（維持すべき）
