---
name: review-security-structure
description: "Review owned or authorized code for security using structure-first evidence: AST/structure maps, call graphs, complexity, Source/Sink flow, and defensive findings. Use when asked for security review, vulnerability review, AST structure map review, SAST triage, Source/Sink, taint flow, parser/scanner hardening, CI/CD security, LLM/agent tool boundary review, 脆弱性レビュー, 構造マップ, セキュリティレビュー."
argument-hint: "対象パス、構造マップ、ASTレポート、call graph、scan結果など"
user-invocable: true
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

If no equivalent structure artifact exists, create a minimal read-oriented structure map before starting findings review. Do not skip this step unless generation is genuinely blocked; record blockers and limits in the Structure Map Summary.

1. Look for existing artifacts in reports, manifest, tmp, CI output, README, package scripts, Makefile, or workflows.
2. Prefer existing language-aware tools: TypeScript compiler, eslint, dependency graph scripts, language server data, test/coverage config, or standard-library parsers.
3. Favor maps that include summaries, class/call graphs, function metrics, variable scopes, imports, taint flow, static findings, dependency audit, and high-complexity hotspots.
4. Avoid installing new dependencies unless clearly justified. Prefer lockfile-backed local tools.
5. Do not execute the target application behavior just to map it. Keep extraction static or read-only when possible.
6. Redact secret values. Record only kind and location, not token/password/key material.
7. For large repos, map entry points, changed files, public APIs, trust boundaries, and dangerous Sink neighborhoods first.

Minimum map contract:

| Item         | Requirement                                                                    |
| ------------ | ------------------------------------------------------------------------------ |
| entry_points | CLI, API handlers, commands, jobs, public APIs, workflows                      |
| files        | reviewed files, language, inferred role                                        |
| symbols      | classes/functions/methods and inferred responsibility                          |
| imports      | external deps, dangerous APIs, security-boundary deps                          |
| call_edges   | caller -> callee edges when practical                                          |
| complexity   | large or high-branch functions when practical                                  |
| sources      | HTTP, CLI args, env, files, network, deserialization, LLM input                |
| sinks        | command, SQL, eval, template, path, file write, network, secret/log, tool call |
| sanitizers   | validate, escape, normalize, authn/authz, schema checks                        |
| scan_limits  | missing, approximate, unsupported, or unparsed areas                           |

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

Lead with Findings. If there are no confirmed findings, state that clearly first.

### Findings

| #   | Severity | Confidence | Target | Structural Signal | Reachability | Impact | Defensive Verification | Minimal Fix |
| --- | -------- | ---------- | ------ | ----------------- | ------------ | ------ | ---------------------- | ----------- |

### Structure Map Summary

| Item      | Value                                                                |
| --------- | -------------------------------------------------------------------- |
| Source    | existing artifact / newly generated / quick extraction / unavailable |
| Artifact  | saved path, or none                                                  |
| Scope     | reviewed paths and boundaries                                        |
| Method    | tools, scripts, or manual extraction used                            |
| Limits    | unparsed or approximate areas                                        |
| Redaction | redacted secret values, or none applicable                           |

### Hypotheses

| #   | Hypothesis | Missing Evidence | Next Check |
| --- | ---------- | ---------------- | ---------- |

### Code to Inspect

| Priority | Path / Symbol | Why |
| -------- | ------------- | --- |

### Recommended Fix Plan

1. Fix clear, reachable, high-impact issues first.
2. Add safety guards such as size limits, timeouts, input validation, path normalization, auth checks, and log redaction.
3. Split high-complexity code only where it reduces risk or enables tests.
4. Verify the Source -> Sink path is blocked or constrained after the fix.

### Verification Summary

- Checks run: command/tool/read-only review performed, or not run with reason
- Remaining risk: unresolved items, or none
- External references: URLs used, or none

## Thanks to / References

Inspired by these structure-first review resources. Treat them as references, not required dependencies.

- https://github.com/harumaki4649/ast-structure-map
- https://qiita.com/harupython/items/ed256553d10578cfec2a
- https://qiita.com/harupython/items/4d572a384c62016c51f2
