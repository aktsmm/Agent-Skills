---
name: packet-capture-analysis
description: "Use when analyzing pcap or pcapng files, triaging network captures, labeling IPs with evidence, generating PNG charts, or writing packet analysis reports. Keywords: pcap, pcapng, tshark, Wireshark, scapy, DNS, TLS SNI, RDAP, graph, matplotlib, gnuplot, packet capture."
argument-hint: "対象の pcap/pcapng ファイル、調査目的、欲しい出力形式"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Packet Capture Analysis

pcap / pcapng を読んで、全体像の把握、IP の意味付け、PNG 可視化、Markdown レポート化まで進めるための skill。

## When To Use

- `pcap` や `pcapng` を渡されて、まず何が起きているか把握したいとき
- 主要通信先、主要会話、プロトコル構成を短時間で掴みたいとき
- DNS、HTTP Host、TLS SNI、RDAP を使って IP に根拠付きラベルを付けたいとき
- PNG グラフや Markdown レポートまで一緒に作りたいとき
- 暗号化通信が多く、本文ではなく行動特性から説明したいとき
- セキュリティ調査と運用調査のどちらにも使いたいとき

## Core Principles

- **まずキャプチャ品質を見る**。snaplen、時系列、件数、期間に問題があれば結論の強さを下げる。
- **最初の 3 手は固定**。`Protocol Hierarchy` → `Endpoints` → `Conversations` で全体像を作る。
- **IP は生のまま並べない**。`HTTP Host -> DNS 応答 -> TLS SNI / gQUIC SNI -> RDAP -> reverse DNS` の順で意味付けする。
- **証拠源は混ぜない**。`hostname` と `organization` のような別種の根拠は分けて持つ。
- **Expert Information は入口であって結論ではない**。前後の会話量、方向、再送、再組立てを見直す。
- **暗号化通信は本文ではなく行動特性で説明する**。相手先、方向、量、時間帯、継続時間で語る。
- **一次集計は CLI、派生集計は Python**。`capinfos` / `tshark` で切ってから `scapy` / `matplotlib` へ渡す。

## Default Workflow

1. **調査目的を固定する**

- 何を知りたいのかを先に決める。
- 例: 大容量通信の相手、怪しい外部送信、特定アプリ通信、レポート化。

2. **キャプチャ品質を確認する**

- 期間、件数、平均レート、時系列、snaplen、`pcapng` の名前解決情報を確認する。
- 品質に問題があるなら、その後の結論は「傾向把握寄り」に落とす。

3. **全体像を作る**

- `Protocol Hierarchy` / `Endpoints` / `Conversations` でベースラインを作る。
- ここでは細部に潜りすぎず、支配的プロトコル、主要通信先、主要会話を押さえる。

4. **主要通信先を意味付けする**

- 上位 N 件の通信先から順にラベル付けする。
- 全件一括照会は避け、報告対象候補だけを調べる。
- 根拠が弱いものは `Unknown` のまま残す。

5. **行動特性と異常候補を整理する**

- HTTP が見えるなら path / host / 方向 / 応答量を見る。
- TLS / QUIC しか見えないなら、相手先、量、時間帯、継続時間で説明する。
- 異常候補は `確認できたこと / 要再確認 / 未解決` で整理する。

6. **可視化とレポート化を行う**

- 最低限、時系列 1 枚とランキング 1 枚を出す。
- グラフには対象期間、集計単位、フィルタ条件、top N 基準を書く。
- レポートは、要約 → 主要表/グラフ → 所見 → 未解決点 の順にまとめる。

## Tool Choice

### CLI を優先する場面

- 初動トリアージ
- 大きいキャプチャの一次集計
- `Protocol Hierarchy` / `Endpoints` / `Conversations`
- DNS / HTTP / TLS 情報の抽出

### Python を優先する場面

- CLI 結果の二次加工
- 独自ランキングやラベル付け
- PNG 生成
- Markdown レポート化

### 描画の選び方

- Python 内で完結したいなら `matplotlib`
- 軽量 CLI で描きたいなら `gnuplot`

## Minimum Outputs

- 短い要約
- 上位通信先表
- 上位会話表
- 根拠付き IP ラベル
- 少なくとも 2 枚の PNG
  - 時間推移系 1 枚
  - ランキング系 1 枚
- `確認できたこと / 要再確認 / 未解決` の整理

## Anti-Patterns

- Expert Information だけで障害確定する
- 全 IP を無差別に外部照会する
- 所有者情報をサービス名と同一視する
- 暗号化通信を無理に本文ベースで説明しようとする
- グラフに期間、集計単位、フィルタ条件を書かない
- 大きいキャプチャを最初から Python で全件読込する

## Completion Checks

- キャプチャ品質確認が済んでいる
- 主要プロトコル、主要通信先、主要会話を説明できる
- 上位 IP または上位会話に、根拠付きラベルが付いている
- 少なくとも 1 枚の時間推移 PNG と 1 枚のランキング PNG がある
- 異常候補が `確認できたこと / 要再確認 / 未解決` に整理されている
- レポートに、グラフ条件とラベル付け方針が書かれている
- 暗号化通信でも行動特性ベースの説明ができている

4. `extract_tshark_stats.py`

- `tshark` と `capinfos` の標準統計を TSV / JSON / text に落とす専用スクリプト

### スクリプト設計の原則

- 1 本で全部やる総合版と、補助用途の小さいスクリプトを分ける
- 解析ロジックと描画ロジックを分離できるようにする
- ラベルの証拠源を別フィールドで保持する
- 出力先ディレクトリを引数で変えられるようにする
- レポート生成をオフにして、表や PNG だけ出せるモードを持たせると再利用しやすい

## Notes

- IP ラベル付けは、読みやすさを大きく改善します。
- ただし、所有者情報と実サービス名は同じではないため、根拠源を分けて扱います。
- Expert Information は開始点としては有効ですが、単独で結論にはしません。
- 暗号化通信は本文よりも行動特性で説明した方が安全です。
- 日本語版レポートは便利ですが、標準必須ではなく、必要に応じて追加出力とします。

## References

- Wireshark `tshark` manual: https://www.wireshark.org/docs/man-pages/tshark.html
- Wireshark `capinfos` manual: https://www.wireshark.org/docs/man-pages/capinfos.html
- Wireshark User's Guide: Conversations
  https://www.wireshark.org/docs/wsug_html_chunked/ChStatConversations.html
- Wireshark User's Guide: Endpoints
  https://www.wireshark.org/docs/wsug_html_chunked/ChStatEndpoints.html
- Wireshark User's Guide: Protocol Hierarchy
  https://www.wireshark.org/docs/wsug_html_chunked/ChStatHierarchy.html
- Wireshark User's Guide: I/O Graphs
  https://www.wireshark.org/docs/wsug_html_chunked/ChStatIOGraphs.html
- Wireshark User's Guide: Expert Information
  https://www.wireshark.org/docs/wsug_html_chunked/ChAdvExpert.html
- Wireshark User's Guide: Name Resolution
  https://www.wireshark.org/docs/wsug_html_chunked/ChAdvNameResolutionSection.html
- Wireshark User's Guide: Resolved Addresses
  https://www.wireshark.org/docs/wsug_html_chunked/ChStatResolvedAddresses.html
- Scapy Usage Guide
  https://scapy.readthedocs.io/en/latest/usage.html
- RFC 7482: RDAP Query Format
  https://datatracker.ietf.org/doc/html/rfc7482
- ICANN RDAP Overview
  https://www.icann.org/rdap/
- ARIN Whois / RDAP Guide
  https://www.arin.net/resources/registry/whois/rdap/