# Azure Infra Validation Output Template

```markdown
## 検証目的

{何を確かめたかったか}

## 検証構成

{tenant / subscription / topology}

## 事前状態

{before routes / status}

## 変更内容

{設定したもの}

## 変更時刻

{要求開始 / Accepted / Succeeded / correlation ID}

## 事後状態

{after routes / status}

## 評価

{目的を満たしたか、未確定は何か、再収束時間や瞬断有無をどこまで言えたか}

## Cleanup

{残すか削除するか}
```
