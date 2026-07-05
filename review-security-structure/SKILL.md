---
name: review-security-structure
description: "Review owned or authorized code for security using structure-first evidence: AST/structure maps, call graphs, complexity, Source/Sink flow, and defensive findings. Use when asked for security review, vulnerability review, AST structure map review, SAST triage, Source/Sink, taint flow, parser/scanner hardening, CI/CD security, LLM/agent tool boundary review, 脆弱性レビュー, 構造マップ, セキュリティレビュー."
argument-hint: "対象パス、構造マップ、ASTレポート、call graph、scan結果など"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Review Security Structure

Defensively review code or structure artifacts by reading architecture and data flow before reading full source. Use structural signals to identify vulnerabilities, logic flaws, parser/scanner risks, CI/CD risks, and LLM/agent tool-boundary risks.

## When to Use

- **security review**, **vulnerability review**, **SAST triage**, **AST**, **structure map**, **call graph**, **Source/Sink**, **taint flow**
- **脆弱性レビュー**, **セキュリティレビュー**, **構造マップ**, **AST レポート**, **依存関係**, **複雑度**
- Reviewing owned or explicitly authorized code, design docs, scan results, or generated structure maps
- Hardening parsers, scanners, CI/CD tools, file walkers, and agent/tool-call boundaries against malformed or adversarial input

## Safety Scope

- Keep the work defensive: review, risk explanation, safe verification ideas, and minimal fixes.
- Do not provide unauthorized testing, intrusion, persistence, evasion, credential theft, weaponized PoC, or destructive external steps.
- If exploitability is uncertain, place the item in Hypotheses rather than Findings.
- If code changes are requested, keep them minimal and verify with existing tests or a focused local check.

## Inputs to Prefer

Use provided structure artifacts first, then inspect the smallest code/config range needed.

| Input          | Examples                                                            |
| -------------- | ------------------------------------------------------------------- |
| Structure      | AST summaries, class/function lists, Mermaid graphs, JSON reports   |
| Data flow      | Source, Propagator, Sanitizer, Sink, taint flow                     |
| Call graph     | caller -> callee edges, boundary-crossing calls, fallback paths     |
| Complexity     | large functions, branch concentration, exception density            |
| Scope/state    | variable scope, global state, shared mutable state, auth boundaries |
| Static results | secret scan, dependency scan, lint/type/SAST warnings               |
| Context        | README, design notes, CI workflow, deployment config                |

## Structure Map Build

同等の成果物がない場合は、findings review に入る前に最小で read-only の structure map を作る。手順（8 steps）と minimum map contract (entry_points / files / symbols / imports / call_edges / complexity / sources / sinks / sanitizers / scan_limits) は [references/structure-map.md](references/structure-map.md)。生成ができない場合は Structure Map Summary に blocker と limits を記録する。

## Review Flow

1. Gate the target: assume review is allowed for current workspace/user-provided artifacts; ask only if ownership or authorization is unclear.
2. Classify the target: web app, CLI, library, scanner, CI/CD tool, infrastructure definition, data processor, extension, or agent tool.
3. Read an existing structure map, or build the minimal map from the contract above before full source reading.
4. Model trust boundaries: who controls which input, where it flows, what authority the Sink has, and what data is sensitive.
5. Trace Source -> Propagator -> Sanitizer -> Sink. Look for missing validation, wrong order, branch gaps, implicit deserialization, and type-conversion surprises.
6. Review call graph paths that bypass authn/authz, validation, initialization, feature flags, or normal handlers.
7. Review complexity and logic risks: giant functions, broad try/catch, deep nesting, fallback behavior, shared state, TOCTOU, and cache races.
8. For parsers/scanners/file walkers, prioritize crash, unbounded recursion, symlink loops, huge/deep ASTs, encoding edge cases, dependency resolution failures, and detection bypass.
9. For CI/CD, review workflow inputs, artifact/cache trust, token permissions, PR boundaries, release gates, and secret exposure.
10. For LLM/agent code, review prompt injection paths, external document trust, tool-call authorization, path safety, command policy, and log redaction.

## Evidence Rules

- Findings require structural signal, reachability, impact, and a defensive verification or fix direction.
- Confidence is High, Medium, or Low. Avoid certainty language unless verified.
- Keep unsupported ideas in Hypotheses with the missing evidence and next check.
- Reference local files with precise paths and line links when possible. Do not paste full source files.

## Output Format

Findings -> Structure Map Summary -> Hypotheses -> Code to Inspect -> Recommended Fix Plan -> Verification Summary の順で返す。全テーブルスキーマと Recommended Fix Plan 本文は [references/output-format.md](references/output-format.md)。Findings がゼロの場合はその旨を先頭に明示する。

## Thanks to / References

Inspired by these structure-first review resources. Treat them as references, not required dependencies.

- https://github.com/harumaki4649/ast-structure-map
- https://qiita.com/harupython/items/ed256553d10578cfec2a
- https://qiita.com/harupython/items/4d572a384c62016c51f2
