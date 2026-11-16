---
name: screenpresso-troubleshoot
description: Screenpresso のシステム音声録音エラーを調査し、64 ビット側の wavemapper 登録欠落時だけ復旧する。Screenpresso の音が録れない、システム音声録音エラー、BadDeviceId calling waveOutOpen の調査・復旧を依頼されたときに使う。
argument-hint: "エラー全文、システム音声の有無、通常再生・他アプリでの音声動作、実施済みの対処"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan
---

# Screenpresso の音声録音エラー

## 対象と根拠

システム音声を有効にしたときの `BadDeviceId calling waveOutOpen` を中心に扱う。他の録音エラーを同じ原因と決めつけない。

提供された 2026-11-16 の解決事例では、通常再生・Teams は正常で、再起動でも改善しなかった。64 ビット側の wavemapper 登録を復元後、利用者が復旧を確認した。単一事例であり、再発原因は未特定。

## 調査・復旧

1. エラー全文、システム音声の有無、通常再生・他アプリでの動作、実施済みの対処を確認する。
2. 次の読み取りコマンドで 64 ビット側の登録を確認する。

   ```powershell
   reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Drivers32" /v wavemapper /reg:64
   ```

   期待値は `REG_SZ msacm32.drv`。値が見つからない旨の出力を確認し、アクセス拒否やコマンド失敗を欠落と扱わない。

3. 期待値が既にある場合はこの修復を行わず、別の原因を調査する。別の型・値がある場合も上書きしない。
4. 欠落を確認した場合だけ、対象のレジストリ値と管理者権限での復元について承認を得る。未保存の録画・編集を保護して Screenpresso を通常終了し、次を管理者ターミナルで実行する。権限を取得できない場合は停止する。

   ```powershell
   reg.exe add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Drivers32" /v wavemapper /t REG_SZ /d msacm32.drv /reg:64
   ```

   `/f` は付けない。既存値の上書き確認が出たら変更を中止し、登録を読み直す。Drivers32 キー全体や 32 ビット側は変更しない。

5. コマンドの終了コードと登録値を再確認し、Screenpresso を起動する。システム音声付きで短く録画し、再生して音声が入ることまで確認する。

## 完了・停止

- 登録の復元だけで復旧済みとせず、録画・再生の確認結果を報告する。利用者による確認と実際に観測した結果を区別し、未確認なら明記する。
- 改善しない場合は同じ登録操作を繰り返さず、登録値・エラー・試行済み手順を残す。再発時は登録を変更した処理の調査へ進む。

## License

ライセンス通知: [LICENSE.txt](LICENSE.txt)。
