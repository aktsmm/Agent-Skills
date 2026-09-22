---
name: ai-cli-benchmark
description: "Design, run, and review fair performance, token, and cost comparisons across GitHub Copilot CLI, Codex CLI, and direct model APIs. Use for AI CLI benchmark, Copilot vs Codex, prompt-cache diagnosis, cache read/write analysis, fresh-process latency measurement, token-cost comparison, or when a benchmark must separate provider caching from local CLI caches."
argument-hint: "比較対象、dataset/prompt、model、測定回数、cache観測条件、出力先"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# AI CLI Benchmark

## When to Use

- Copilot CLI、Codex CLI、直接 API の速度・token・費用を比較する。
- prompt cache の read / write を区別し、cache-offを主張できるか確認する。
- fresh process、temporary home、instruction/tool isolationを揃えた再現可能なbenchmarkを作る。

過去sessionの事後分析だけなら`analyze-copilot-sessions`を使う。このskillは比較条件の設計、実行、証拠化を担当する。

## Cache Boundaries

- Copilot CLI / Codex CLIには、provider側model prompt cacheを無効化する公開optionがない。fresh process、一時home、ephemeral、nonceでも`cache off`と呼ばない。
- `COPILOT_CACHE_HOME`はMarketplace、自動更新packageなどのローカル一時データ用。`COPILOT_MCP_TOOL_CACHE`はローカルMCP serverのtool-list snapshot用。model prompt cacheではない。
- OpenAI prompt cacheは手動消去できない。GPT-5.6以降をResponses APIから直接呼ぶ場合だけ、explicit-only modeでbreakpointを置かず、そのrequestのcache writeを避けられる。CLIへ推測適用しない。
- nonceはuser prompt全体の一致を避ける補助であり、その前のhidden system / agent prefixのcache readを防がない。

## Workflow

1. **Freeze the task**
  - dataset、expected labels、prompt、schema、input order、model、reasoningを固定し、hashを取る。
  - accuracyと性能を同時に比較する場合、同じ合格条件を全providerへ適用する。
2. **Define measurement boundaries**
  - `one request`、`serial total`、`fresh-process end to end`を区別する。
  - API直呼びとCLI起動込み時間を`model speed`として並べない。
3. **Isolate each CLI**
  - repo外のowned temp directory、fresh process、一時`COPILOT_HOME` / auth-only `CODEX_HOME`を使う。
  - custom instructions、tools、MCP、session reuseを無効にし、secretを子processとlogへ渡さない。
4. **Observe cache; do not assume control**
  - 必要ならprompt先頭へ一意nonceを入れ、nonce本体ではなくhashだけ保存する。
  - zero-cache-read gateは診断用。失敗はprovider cacheの観測であり、benchmark失敗として隠さない。
5. **Record raw categories**
  - normal input、cache read、cache write、output、reasoningを別fieldで保存する。
  - provider schemaで包含・排他関係を確認するまでtoken区分を足さない。
6. **Repeat before claiming performance**
  - 単発差をcacheの因果効果にしない。median / p95 / rangeとaccuracyを報告する。
7. **Validate the artifact**
  ```powershell
  python scripts/validate_benchmark.py result.json `
    --require-cache-metadata `
    --report validation.json
  ```

## Reporting Rules

- `cache write`はcache hitではない。readと分け、該当modelの料金区分で費用を計算する。
- `uncached run`ではなく、観測どおり`cache read 0 run`または`cache-observed run`と書く。
- CLI version、model、reasoning、prompt hash、nonce hash、fresh-process条件、測定境界、usage schemaを記載する。
- cache read 0でも将来のwriteやhidden prefixの制御を保証しない。

## Done Criteria

- [ ] dataset/prompt/schema/model/reasoningが固定され、hashがある。
- [ ] 全providerでfresh processと一時homeを使う。
- [ ] cache read/writeを別fieldで保存する。
- [ ] 測定境界とaccuracyを一緒に報告する。
- [ ] 複数runなしの速度差へ因果を割り当てない。
- [ ] benchmark JSON validatorがPASSする。

## References

- OpenAI Prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching
- GitHub Copilot CLI command reference: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
