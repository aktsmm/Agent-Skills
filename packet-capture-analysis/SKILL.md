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

## What This Skill Does

この skill は、pcap / pcapng ファイルを調査するときに、

- 初動トリアージ
- 一般的な切り分け
- Wireshark CLI と Python の使い分け
- IP アドレスの意味付け
- PNG グラフ生成
- Markdown レポート化

までを一気通貫で進めるための手順をまとめたものです。

単にツールを叩くだけではなく、どの順番で見ればよいか、どこで仮説を立てるか、どこで断定を避けるべきか、という方法論も含みます。

## Methodology Principles

### 1. まずキャプチャ品質を疑う

- 解析対象の内容を読む前に、キャプチャ自体が信頼できるかを確認します。
- 期間が短すぎる、snaplen で切れている、時系列が崩れている、件数が少なすぎる、といった場合は結論の信頼度が下がります。

### 2. 最初の 3 手を固定する

- まず全体像を作ります。
- 基本は次の順です。
  - Protocol Hierarchy
  - Endpoints
  - Conversations
- これで「誰が」「何で」「いつから」「どれだけ」通信したかを短時間で掴みます。

### 3. IP は生のまま並べない

- 読み手にとって、IP の羅列は理解コストが高いです。
- 可能な限り、HTTP Host、DNS 応答、TLS SNI、RDAP、reverse DNS を使って意味付けしてから見せます。
- ただし、ラベルの証拠源は混ぜずに分離します。

### 4. Expert Information は入口であって結論ではない

- Warning や Error が出ても、それだけで障害確定しません。
- 前後のフロー、再送、再組立て、方向、会話量を見て再確認します。

### 5. 暗号化通信は本文ではなく行動特性で説明する

- TLS / QUIC が中心で本文が見えない場合は、相手先、方向、量、時間帯、継続時間、SNI、DNS で説明します。
- 見えないものを見えたことにしないのが重要です。

### 6. 一次集計は CLI、派生集計は Python

- 大きいキャプチャの一次集計は `capinfos` / `tshark` に寄せます。
- Python は、二次加工、ラベル付け、レポート整形、描画に使います。

## When To Use

- `pcap` や `pcapng` を渡されて、まず何が起きているか把握したいとき
- 通信量の大きい相手、主要会話、プロトコル構成を短時間で掴みたいとき
- DNS、HTTP Host、TLS SNI、RDAP を使って IP に意味付けしたいとき
- PNG グラフや Markdown レポートまで一緒に作りたいとき
- Wireshark CLI と Python のどちらを使うべきか迷うとき
- 暗号化通信が多く、本文ではなく行動特性から説明したいとき
- セキュリティ調査として、不審通信、外部送信、IOC 候補、想定外宛先の切り分けをしたいとき
- 性能・運用調査として、帯域消費、アプリ通信、更新ダウンロード、業務通信の特徴を説明したいとき

## Recommended Stack

### 標準構成

- `capinfos`: キャプチャ品質の初期確認
- `tshark`: 一次集計、プロトコル階層、Endpoints、Conversations、TLS/DNS 抽出
- `scapy`: 派生集計、柔軟な整形、追加ロジック
- `matplotlib`: Python 内で完結する PNG 生成の標準手段

### オプション

- `gnuplot`: 軽量な CLI ベース描画。時系列や単純ランキングに向く
- RDAP / reverse DNS: IP 所有者や組織名の補完

## Platform Assumptions

- 基本方針はクロスプラットフォームです。
- Windows では Wireshark CLI のパス解決や PowerShell 実行が必要になる場合があります。
- Linux / macOS でも同じ分析手順を使えますが、CLI パスやパッケージ導入方法は環境に合わせて読み替えます。

## Prerequisites

- 解析対象の `pcap` または `pcapng`
- 可能なら Wireshark CLI (`tshark`, `capinfos`)
- Python 環境
- Python ライブラリ:
  - `scapy`
  - `matplotlib`
- 任意:
  - `gnuplot`

## Procedure

1. 調査目的を固定する

- まず、何を知りたいのかを明確にします。
- 例: 通信量が大きい相手を知りたい、怪しい外部送信を見たい、特定アプリ通信の特徴を見たい、レポートを作りたい。

2. キャプチャ品質を確認する

- 期間、件数、平均レート、ファイルサイズ、時系列の乱れ、snaplen の問題がないかを確認します。
- `capinfos` が使えるなら最優先で見ます。
- この時点で品質に問題があれば、後段の結論の信頼度を下げる前提を明記します。
- `pcapng` に名前解決情報が入っているかも確認対象に含めます。

3. 全体像を 3 つの観点で押さえる

- 最初の 3 手は固定です。
  - Protocol Hierarchy
  - Endpoints
  - Conversations
- これにより、支配的プロトコル、主要通信先、主要会話、開始時刻、継続時間、送受信偏りを把握します。
- ここではまだ細部へ潜りすぎず、ベースラインを作る意識で進めます。

4. ローカル端末と主要外部通信先を切り分ける

- private IP を中心にローカル端末候補を特定します。
- 主要な外部 IP を上位 N 件に絞ります。
- 全件を細かく掘るのではなく、通信量上位から見る方が効率的です。

5. IP を意味付けする

- IP をそのまま並べず、裏付けが取れる範囲でラベル化します。
- 優先順は次の通りです。
  - HTTP Host
  - DNS 応答
  - TLS SNI / gQUIC SNI
  - RDAP 所有者情報
  - reverse DNS
- ラベルの根拠は混ぜずに保持します。
- 例: `hostname`, `dns_name`, `tls_sni`, `rdap_org` を別属性として扱う。
- 全件一括で外部照会するのではなく、上位通信先や報告対象候補だけに限定して調べます。
- `organization` と `hostname` は別の意味なので、同じ列に潰さないようにします。

6. 行動特性を掘る

- HTTP が見えるなら request path、host、方向、応答量を見る。
- TLS / QUIC しか見えないなら、相手先、方向、時間帯、会話サイズ、継続時間で説明する。
- Expert Information は入口にはなるが、単独で障害確定しません。
- 必要に応じて `Follow Stream`、DNS 統計、HTTP 統計、I/O Graph、SRT/RTD 系へ進みます。

7. 異常候補を整理する

- 次の観点で異常候補を整理します。
  - 想定外の大容量送信
  - 短時間の大量ダウンロード
  - 通常業務で見慣れない外部宛先
  - 再送や malformed の偏在
  - 時間帯の偏り
- 結果は次の 3 区分でまとめます。
  - 確認できたこと
  - 要再確認
  - 未解決
- いきなり「不審」と断定せず、まず「ベースラインから外れているか」で整理します。
- セキュリティ調査でも同様に、IOC や外部送信の有無を即断せず、通常業務通信や CDN、更新処理との区別を先に付けます。

8. PNG グラフを作る

- 最低限、次の 2 系統を出します。
  - 時系列系: 全体 throughput、主要通信先別の時間推移
  - ランキング系: 上位通信先、上位会話、プロトコル構成
- グラフには次を明記します。
  - 対象期間
  - 集計単位
  - フィルタ条件
  - top N 基準
- 1 位だけ極端に大きい場合は、対数軸、横棒、または 1 位除外版を検討します。
- 時系列グラフでは bin 幅を必ず明記します。

9. レポート化する

- まず要約を書く
- 次に主要表とグラフを置く
- そのあと所見を書く
- 重要なのは、IP をそのまま並べることではなく、調査できた範囲で意味付けしたうえで読みやすく並べることです。

## Tool Strategy

### Wireshark CLI を優先する場面

- 初動トリアージ
- 大きいキャプチャの一次集計
- Protocol Hierarchy、Endpoints、Conversations
- DNS / HTTP / TLS 情報の抽出
- 応答関係や再組立てを伴う二段階解析が必要なとき

### Python を優先する場面

- Wireshark CLI の結果を二次加工したいとき
- 独自のランキングやラベル付けをしたいとき
- PNG を自動生成したいとき
- Markdown レポートまで一緒に作りたいとき
- Wireshark CLI で足りない独自ロジックを入れたいとき

### matplotlib を優先する場面

- Python の解析結果からそのまま描画したいとき
- グラフとレポートを 1 スクリプトで完結させたいとき

### gnuplot を優先する場面

- TSV から素早く PNG を作りたいとき
- 時系列や単純ランキングを軽量に描きたいとき
- Python 側では集計だけ行い、描画を分離したいとき

## Visualization Patterns

### 最低限出すグラフ

1. 全体スループット推移
2. 通信先別バイト量ランキング
3. 会話別バイト量ランキング

### あると良いグラフ

1. 通信先別時系列推移
2. プロトコル別パケット数
3. 送信量と受信量の比較
4. 平均レートまたは継続時間を併記した会話比較

### 見やすくするコツ

- ランキング系は上位 N 件に絞る
- 1 位だけ極端に大きい場合は対数軸、横棒、または 1 位除外版を検討する
- 時系列は bin 幅を明記する
- Unknown を無理に説明しない

## Decision Points

### キャプチャ品質に問題があるか

- snaplen や truncation が怪しい場合は、本文解析より傾向把握を優先します。
- この場合、レポートにも「capture quality に依存する」という前提を明記します。

### 大きいファイルか

- 大きい場合は、最初から Python で全読込せず、`capinfos` と `tshark` で上位 N と対象期間を先に切ります。

### two-pass が必要か

- `response in frame` や再組立て前提の解析が必要なら、`tshark` の two-pass を検討します。
- ライブキャプチャや pipe では使えない前提も意識します。

### 暗号化通信が中心か

- 暗号化通信が中心なら、本文よりも相手先、量、方向、時間帯、会話継続時間で説明します。

### IP に根拠付きラベルが付けられるか

- 付けられる場合はラベル化します。
- 付けられない場合は Unknown のまま残します。

### どこまで外部照会するか

- RDAP や reverse DNS は、上位通信先や要報告対象に限定します。
- 全件照会は再現性、速度、observer effect の観点で避けます。

### PNG は何で作るか

- Python 内で完結したいなら `matplotlib`
- 軽量 CLI で分けたいなら `gnuplot`

## IP Labeling Policy

- IP は可能ならラベル化してから見せる
- ラベル付けの優先順は `HTTP Host -> DNS 応答 -> TLS SNI / gQUIC SNI -> RDAP -> reverse DNS`
- `hostname` と `organization` は別属性で持つ
- 用途ヒントは、裏付けがある場合だけ付ける
- 裏付けが弱いものは `Unknown` のまま残す

## Anti-Patterns

- Expert Information だけで障害確定する
- 全 IP を無差別に外部照会してラベルを付ける
- 所有者情報をサービス名と同一視する
- 暗号化通信を無理に本文ベースで説明しようとする
- グラフに期間、集計単位、フィルタ条件を書かない
- 大きいキャプチャを最初から Python で全件読込して重くする

## Output Expectations

この skill の成果物は、必要に応じて以下です。

- 短い要約
- 上位通信先表
- 上位会話表
- DNS / HTTP / TLS の補助表
- PNG グラフ
- Markdown レポート

### 最低限レポートに含めるもの

- スコープ
- 主要所見
- 主要通信先と主要会話
- IP ラベル付け根拠
- 未解決点
- 再実行手順

### 標準出力

- Markdown レポート
- 上位通信先表
- 上位会話表
- 根拠付き IP ラベル
- 少なくとも 2 枚の PNG
  - 1 枚は時間推移系
  - 1 枚はランキング系

### オプション出力

- 日本語版レポート
- gnuplot 版 PNG
- IOC 候補一覧
- 調査対象に特化した補助表

## Completion Checks

- キャプチャ品質確認が済んでいる
- 主要プロトコル、主要通信先、主要会話を説明できる
- 上位 IP または上位会話に、根拠付きラベルが付いている
- 少なくとも 1 枚の時間推移 PNG と 1 枚のランキング PNG がある
- 異常候補が `確認済み / 要再確認 / 未解決` に整理されている
- レポートに、グラフ条件とラベル付け方針が書かれている
- Expert を盲信せず、前後確認が済んでいる
- 暗号化通信でも行動特性ベースの説明ができている
- セキュリティ観点で見る場合でも、通常通信との区別を説明できている

## Reusable Script Ideas

この skill に合わせて、汎用スクリプトを併置すると再利用性が上がります。

### 推奨スクリプト

1. `analyze_capture.py`

- `pcap` / `pcapng` を読み、主要通信先、主要会話、DNS、HTTP Host、TLS SNI、RDAP 補完、PNG、Markdown レポートまで出す総合スクリプト

2. `plot_with_gnuplot.py`

- 集計済み TSV を `gnuplot` で PNG 化する軽量スクリプト

3. `label_endpoints.py`

- 上位 IP に対して DNS、HTTP Host、TLS SNI、RDAP を順に当てて、証拠源つきラベル表を作る専用スクリプト

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