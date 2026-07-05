# Structure Map Build

If no equivalent structure artifact exists, create a minimal read-oriented structure map before starting findings review. Do not skip this step unless generation is genuinely blocked; record blockers and limits in the Structure Map Summary.

## Build Steps

1. Look for existing artifacts in reports, manifest, tmp, CI output, README, package scripts, Makefile, or workflows.
2. Prefer existing language-aware tools: TypeScript compiler, eslint, dependency graph scripts, language server data, test/coverage config, or standard-library parsers.
3. Favor maps that include summaries, class/call graphs, function metrics, variable scopes, imports, taint flow, static findings, dependency audit, and high-complexity hotspots.
4. Avoid installing new dependencies unless clearly justified. Prefer lockfile-backed local tools.
5. Do not execute the target application behavior just to map it. Keep extraction static or read-only when possible.
6. Redact secret values. Record only kind and location, not token/password/key material.
7. For large repos, map entry points, changed files, public APIs, trust boundaries, and dangerous Sink neighborhoods first.

## Minimum Map Contract

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
