# WebAuthn Virtual Authenticator (CDP)

CDP の `WebAuthn` domain で仮想認証機を使う承認済みフロー。認証は本人入力が既定で、対応サイトというだけでは無人利用を許可しない。対象サイト・アカウント・credential運用の明示承認と認証方針への適合が必要。MFA要求や拒否を回避しない。

## 対象判定

- サイトが WebAuthn / FIDO2 / passkey 対応していること。`#pk-btn` のような「パスキーでログイン」UI、または FIDO2 設定ページが存在する
- 非対応サイト（メール OTP / SMS のみ）は対象外。これは bypass できない
- ログインには当該アカウントに登録済みのcredentialとowned targetを確認する。未登録なら登録・秘密鍵取得／保存を承認してから進み、既存credentialの削除も個別に承認する。OTPや生体認証が要求されたら本人対応まで停止する。

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
- **`rpId` は登録可能ドメイン単位**。`site2.example.com` で登録した credential は `m.example.com` でも `rpId=example.com` であれば assertion 可。サブドメインを跨いで使うときは登録時の rpId を必ず確認する
- **attach 先タブを正しく選ぶ**。仮想認証機は attach した page target でしか効かない。assertion 用は `#pk-btn` を持つ login タブ、register 用は `sw_page=RegPasskey` のような登録 URL のタブを最優先で掴む。同一サービスで認証済みドメイン (`site2.example.com`) と未認証 login ドメイン (`login.example.com`) のタブが共存しがちで、認証済み側に attach すると assertion ボタンが見つからず OS 生体認証 (Windows Hello / Touch ID) に fallback する。tab 解決は `期待 URL を含むタブ最優先 → 既存タブを navigate → 新規タブで開く` の順で fallback する
- **attach と `#pk-btn` click は同じ helper context で連続実行する**。「ready で停止して click は外部 (MCP / 手動 / 別 prompt) に委任」する設計は、login タブ取り違えと CDP target lifetime で簡単に壊れる。同じ WebSocket 内で `Runtime.evaluate` → URL change poll まで完結させる
- **登録上限**: 登録が上限で拒否されたら停止する。古いcredentialを自動削除せず、所有者と復旧手段を確認し、削除対象の明示承認後だけUIで削除する。
- **既存 CDP セッション**: ポート接続成功だけでは所有を証明しない。他のcontrollerが同じtargetを使用中なら操作を停止し、owned targetに限定する。

## Credential JSON 永続化

- `getCredentials` の返却に `privateKey` (PKCS#8 base64url) が含まれる。盗まれれば誰でも assertion できる
- 保存先は `secrets/<site>_passkey.json` 等にし、**必ず gitignore**。クラウド同期・USB 持ち出し禁止
- バックアップせず、失効したら register し直す運用が安全
- 失効検知: 期待通り login が走った後に `dump` で `signCount` が増えているかを確認する。停滞していればサービス側で credential 解除疑い

## 動作確認 smoke

`webauthn.io` の register / login ボタンで丸ごと検証可能。enable → addVirtualAuthenticator → サイト上で「Register」→ assertion 成立 → JSON 保存 → tab を再 open して `addCredential` + login。

## 既知の参照例

- CDP `WebAuthn.*` の thin wrapper（`enable` → `addVirtualAuthenticator` → `save_credentials_to` / `load_credentials_from`）を 1 ファイル作っておくと、複数サイトで使い回しやすい
- 対応サイトの passkey 登録 URL は固定の `sw_page` / route パラメータを持つことが多い。session 内で見つけた登録ページ URL は repo memory に残す
