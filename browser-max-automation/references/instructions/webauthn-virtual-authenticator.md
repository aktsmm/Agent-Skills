# WebAuthn Virtual Authenticator (CDP)

CDP の `WebAuthn` domain で **仮想認証機** を有効化し、passkey / FIDO2 対応サイトのログインを完全無人化する。物理キー、生体認証、メール OTP を経由しないので、`Not the Best Fit` の「MFA 応答をチャットで受け取らない」原則と矛盾せず、サイト側で **passkey 対応済み** ならこれを最優先する。

## 対象判定

- サイトが WebAuthn / FIDO2 / passkey 対応していること。`#pk-btn` のような「パスキーでログイン」UI、または FIDO2 設定ページが存在する
- 非対応サイト（メール OTP / SMS のみ）は対象外。これは bypass できない
- 優先順位: **CDP 仮想認証機 passkey > メール OTP > SMS > 物理キー / 生体（無人運用不可）**

## 基本フロー

```text
[register] enable → addVirtualAuthenticator → ブラウザで passkey 登録 → getCredentials → JSON 保存
[login]    enable → addVirtualAuthenticator → addCredential(json) → ブラウザで passkey ボタン押下 → 自動 assertion
```

## CDP コマンド

| Method                                | 用途                                                   |
| ------------------------------------- | ------------------------------------------------------ |
| `WebAuthn.enable`                     | 仮想認証機機能を ON。`enableUI=False` で内部 UI を抑止 |
| `WebAuthn.addVirtualAuthenticator`    | 仮想 authenticator 追加。`authenticatorId` を返す      |
| `WebAuthn.getCredentials`             | 登録済み credential を **PKCS#8 秘密鍵込み** で取得    |
| `WebAuthn.addCredential`              | 既存 credential を仮想 authenticator にロード          |
| `WebAuthn.removeVirtualAuthenticator` | 仮想 authenticator 削除                                |
| `WebAuthn.setUserVerified`            | UV 状態を後から切替                                    |

### 推奨パラメータ

```json
{
  "protocol": "ctap2",
  "transport": "internal",
  "hasResidentKey": true,
  "hasUserVerification": true,
  "isUserVerified": true,
  "automaticPresenceSimulation": true,
  "backupEligibility": true,
  "backupState": true
}
```

- `transport=internal` で **platform authenticator**（生体認証相当）として扱われ、サイトの passkey UI から自然に呼ばれる
- `isUserVerified=true` + `automaticPresenceSimulation=true` で UV ダイアログとタッチ要求を自動承認
- `hasResidentKey=true` で discoverable credential（usernameless login）

## Gotchas

- **仮想認証機は tab 単位**。`enable` した tab を閉じると `authenticatorId` 失効。register / login script 実行後は同じ tab で操作する
- **`rpId` は host ベース**。`site2.sbisec.co.jp` で登録した credential は `m.sbisec.co.jp` でも `rpId=sbisec.co.jp` であれば assertion 可。サブドメインを跨いで使うときは登録時の rpId を必ず確認する
- **attach 先タブを正しく選ぶ**。仮想認証機は attach した page target でしか効かない。assertion 用は `#pk-btn` を持つ login タブ、register 用は `sw_page=RegPasskey` のような登録 URL のタブを最優先で掴む。同一サービスで認証済みドメイン (`site2.example.com`) と未認証 login ドメイン (`login.example.com`) のタブが共存しがちで、認証済み側に attach すると assertion ボタンが見つからず OS 生体認証 (Windows Hello / Touch ID) に fallback する。tab 解決は `期待 URL を含むタブ最優先 → 既存タブを navigate → 新規タブで開く` の順で fallback する
- **attach と `#pk-btn` click は同じ helper context で連続実行する**。「ready で停止して click は外部 (MCP / 手動 / 別 prompt) に委任」する設計は、login タブ取り違えと CDP target lifetime で簡単に壊れる。同じ WebSocket 内で `Runtime.evaluate` → URL change poll まで完結させる
- **登録上限**: 多くのサービスでパスキー登録は数件まで（SBI 証券は 3 件）。古い credential が残ると登録が拒否されるので、UI 側で削除してから新規 register する
- **既存 CDP セッションと併用可**: raw WebSocket と同じ性質。MCP Playwright が active な tab に attach しても競合しない

## Credential JSON 永続化

- `getCredentials` の返却に `privateKey` (PKCS#8 base64url) が含まれる。盗まれれば誰でも assertion できる
- 保存先は `secrets/<site>_passkey.json` 等にし、**必ず gitignore**。クラウド同期・USB 持ち出し禁止
- バックアップせず、失効したら register し直す運用が安全
- 失効検知: 期待通り login が走った後に `dump` で `signCount` が増えているかを確認する。停滞していれば SBI 側で credential 解除疑い

## 動作確認 smoke

`webauthn.io` の register / login ボタンで丸ごと検証可能。enable → addVirtualAuthenticator → サイト上で「Register」→ assertion 成立 → JSON 保存 → tab を再 open して `addCredential` + login。

## 既知の参照例

- CDP `WebAuthn.*` の thin wrapper（`enable` → `addVirtualAuthenticator` → `save_credentials_to` / `load_credentials_from`）を 1 ファイル作っておくと、複数サイトで使い回しやすい
- 対応サイトの passkey 登録 URL は固定の `sw_page` / route パラメータを持つことが多い。session 内で見つけた登録ページ URL は repo memory に残す
