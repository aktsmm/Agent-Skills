# レビューチェックリスト

## 一般

- [ ] 環境名とリソース命名が命名規約に従っている
- [ ] `env/<environment>/README.md` に目的・スコープ・手順が記載されている
- [ ] 認証情報・シークレットがハードコードされていない
- [ ] タグ (環境/プロジェクト/コストセンター) が設定されている

## Azure CLI 方式

- [ ] `deploy.ps1` に対象リソースグループ / サブスクリプションが明示されている
- [ ] `-WhatIf` / dry-run の結果が確認済み
- [ ] ログ / 出力が `env/<environment>/logs/` に保存されている

## Bicep 方式

- [ ] `az bicep build` でエラーなくビルドできる
- [ ] `az bicep lint` で警告がない (または理由が明記)
- [ ] パラメータファイルにデフォルトが設定され、必須項目が明確
- [ ] `what-if` の結果が確認済みで、意図しないリソース削除がない
- [ ] 公式サンプル (MCP) を参考にしている

## ネットワーク

- [ ] VNet / サブネット設計が要件を満たしている
- [ ] Private Endpoint が必要なリソースに設定されている
- [ ] NSG / UDR が適切に設定されている
- [ ] DNS 設定 (Private DNS Zone) が正しい

## データサービス

- [ ] SQL Database: TDE / 監査設定が有効
- [ ] Cosmos DB: パーティションキー設計が適切
- [ ] Redis: TLS 1.2 以上、AAD 認証が有効
- [ ] バックアップ / リテンション設定が要件を満たす

## コンピュート

- [ ] AKS: プライベートクラスター設定 (必要な場合)
- [ ] Container Apps: VNet 統合 (必要な場合)
- [ ] App Service: VNet 統合 + Private Endpoint

## 監視・可観測性

- [ ] Log Analytics Workspace が作成されている
- [ ] Diagnostic Settings が主要リソースに設定
- [ ] アラートルールが定義されている

## セキュリティ

- [ ] Managed Identity (User-Assigned 推奨) が設定されている
- [ ] Key Vault 参照でシークレット管理
- [ ] 最低限の RBAC ロールで権限設計されている
- [ ] Microsoft Defender for Cloud の推奨事項を確認

## DR・バックアップ

- [ ] Recovery Services Vault が設定 (必要な場合)
- [ ] バックアップポリシーが要件を満たす
- [ ] Geo 冗長 / ゾーン冗長の設定が適切

## ドキュメント

- [ ] 手順の再現性が確認できる
- [ ] 変更ログ / 履歴が追跡可能 (コミットや README の更新)
- [ ] 次のアクションまたは改善点が記載されている
- [ ] アーキテクチャ図が含まれている (推奨)
