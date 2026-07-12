#!/usr/bin/env python3
"""Analyze normalized Copilot Chat session metrics without inventing accuracy."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


QUALITY_LEVELS = {
    "UNMEASURED": 0,
    "PROXY_ONLY": 1,
    "GATE_SUPPORTED": 2,
    "VERIFIED": 3,
}


for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Copilot session metrics; compare cost, time, and quality when multiple runs are supplied.",
    )
    parser.add_argument("inputs", nargs="*", help="Extractor JSON, existing metrics JSON, or analysis manifest")
    parser.add_argument("--manifest", help="Analysis manifest with run metrics and optional quality evidence")
    parser.add_argument(
        "--weights",
        help="Optional JSON object or JSON file with explicit cost/time/quality weights",
    )
    parser.add_argument("--output-json", help="Optional analysis JSON output path")
    parser.add_argument("--json-only", action="store_true", help="Print only JSON")
    parser.add_argument("--strict-exit-codes", action="store_true", help="Return 1 when analysis fails")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def resolve(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def status_from_payload(payload: dict[str, Any]) -> str:
    for key in ("final_verdict", "verdict", "status", "overall_status"):
        value = str(payload.get(key) or "").upper()
        if value in {"PASS", "FAIL"}:
            return value
    result = payload.get("result")
    if isinstance(result, dict):
        return status_from_payload(result)
    return "UNKNOWN"


def load_quality_evidence(base: Path, evidence: object) -> dict[str, Any]:
    if evidence is None:
        return {
            "level": "UNMEASURED",
            "passed": None,
            "gate_count": 0,
            "failed_gate_count": 0,
            "adjudicated_residual_defects": None,
            "notes": ["No external quality evidence was provided."],
        }
    if not isinstance(evidence, dict):
        raise ValueError("quality_evidence must be an object")
    requested_level = str(evidence.get("level") or "").upper()
    if requested_level and requested_level not in QUALITY_LEVELS:
        raise ValueError(f"unsupported quality level: {requested_level}")
    gate_paths = evidence.get("gate_paths") or []
    if not isinstance(gate_paths, list):
        raise ValueError("quality_evidence.gate_paths must be an array")
    statuses = []
    for value in gate_paths:
        path = resolve(base, str(value))
        if not path.is_file():
            raise ValueError(f"quality evidence file not found: {value}")
        statuses.append(status_from_payload(load_json(path)))
    explicit_passed = evidence.get("passed") if isinstance(evidence.get("passed"), bool) else None
    failed = sum(status == "FAIL" for status in statuses)
    unknown = sum(status == "UNKNOWN" for status in statuses)
    passed = explicit_passed
    if statuses:
        passed = failed == 0 and unknown == 0 and all(status == "PASS" for status in statuses)
    level = requested_level
    if not level:
        level = "GATE_SUPPORTED" if statuses else "PROXY_ONLY" if explicit_passed is not None else "UNMEASURED"
    if level == "VERIFIED" and not statuses:
        raise ValueError("VERIFIED quality requires gate_paths")
    residual = evidence.get("adjudicated_residual_defects")
    residual_value = int(residual) if isinstance(residual, int) and not isinstance(residual, bool) and residual >= 0 else None
    notes = evidence.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]
    return {
        "level": level,
        "passed": passed,
        "gate_count": len(statuses),
        "failed_gate_count": failed + unknown,
        "adjudicated_residual_defects": residual_value,
        "notes": [str(item) for item in notes],
    }


def adapter_workload(payload: dict[str, Any], override: dict[str, Any] | None) -> dict[str, Any]:
    source = payload.get("workload") if isinstance(payload.get("workload"), dict) else {}
    override = override or {}
    unit_count = override.get("unit_count", source.get("unit_count", payload.get("question_count")))
    unit_count = int(unit_count) if isinstance(unit_count, int) and not isinstance(unit_count, bool) and unit_count > 0 else None
    unit_name = str(override.get("unit_name") or source.get("unit_name") or ("question" if payload.get("question_count") else "unit"))
    workload = {
        "task_kind": str(override.get("task_kind") or source.get("task_kind") or ""),
        "revision": str(override.get("revision") or source.get("revision") or ""),
        "workflow_version": str(override.get("workflow_version") or source.get("workflow_version") or ""),
        "rubric_version": str(override.get("rubric_version") or source.get("rubric_version") or ""),
        "unit_name": unit_name,
        "unit_count": unit_count,
        "fingerprint": str(override.get("fingerprint") or source.get("fingerprint") or ""),
    }
    return workload


def normalize_run(
    payload: dict[str, Any],
    *,
    label: str,
    workload_override: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workload = adapter_workload(payload, workload_override)
    timing = payload.get("timing") if isinstance(payload.get("timing"), dict) else {}
    cost = payload.get("cost") if isinstance(payload.get("cost"), dict) else {}
    operations = payload.get("operations") if isinstance(payload.get("operations"), dict) else {}
    primary = payload.get("primary_model") if isinstance(payload.get("primary_model"), dict) else {}
    usage = [item for item in payload.get("usage", []) if isinstance(item, dict)]
    warnings = [item for item in payload.get("warnings", []) if isinstance(item, dict)]
    cost_coverage = cost.get("coverage") if isinstance(cost.get("coverage"), dict) else {}
    unit_count = workload["unit_count"]
    total_aiu = number(cost.get("total_aiu"))
    if total_aiu is None:
        total_nano = number(cost.get("total_nano_aiu"))
        total_aiu = total_nano / 1_000_000_000 if total_nano is not None else None
    aiu_per_unit = number(cost.get("aiu_per_unit"))
    if aiu_per_unit is None:
        aiu_per_unit = number(cost.get("aiu_per_question"))
    if aiu_per_unit is None and total_aiu is not None and unit_count:
        aiu_per_unit = total_aiu / unit_count
    observed = number(timing.get("session_observed_seconds"))
    elapsed = number(timing.get("review_elapsed_seconds"))
    active = number(timing.get("active_llm_seconds"))
    preferred_seconds = elapsed if elapsed is not None else observed if observed is not None else active
    llm_calls = int(operations.get("llm_calls") or 0)
    llm_errors = int(operations.get("llm_errors") or 0)
    tool_calls = int(operations.get("tool_calls") or 0)
    tool_errors = int(operations.get("tool_errors") or 0)
    error_total = llm_errors + tool_errors
    operation_total = llm_calls + tool_calls
    return {
        "label": label,
        "session_id": str(payload.get("session_id") or ""),
        "source_format": str(payload.get("source_format") or "detailed-review-run-metrics"),
        "measurement_scope": payload.get("measurement_scope"),
        "primary_model": {
            "model": str(primary.get("model") or "unknown"),
            "reasoning_effort": str(primary.get("reasoning_effort") or "default"),
        },
        "workload": workload,
        "usage_summary": {
            "agent_role_count": len({str(item.get("role") or "unknown") for item in usage}),
            "roles": sorted({str(item.get("role") or "unknown") for item in usage}),
            "model_configurations": [
                {
                    "role": str(item.get("role") or "unknown"),
                    "model": str(item.get("model") or "unknown"),
                    "reasoning_effort": str(item.get("reasoning_effort") or "default"),
                    "llm_calls": int(item.get("llm_calls") or 0),
                    "input_tokens": int(item.get("input_tokens") or 0),
                    "output_tokens": int(item.get("output_tokens") or 0),
                    "cached_tokens": int(item.get("cached_tokens") or 0),
                    "aiu": round(int(item.get("nano_aiu") or 0) / 1_000_000_000, 6),
                    "llm_duration_seconds": round(float(item.get("llm_duration_seconds") or 0), 3),
                }
                for item in usage
            ],
        },
        "metrics": {
            "total_aiu": round(total_aiu, 6) if total_aiu is not None else None,
            "aiu_per_unit": round(aiu_per_unit, 6) if aiu_per_unit is not None else None,
            "elapsed_seconds": round(preferred_seconds, 3) if preferred_seconds is not None else None,
            "elapsed_seconds_per_unit": round(preferred_seconds / unit_count, 6) if preferred_seconds is not None and unit_count else None,
            "active_llm_seconds": round(active, 3) if active is not None else None,
            "active_llm_seconds_per_unit": round(active / unit_count, 6) if active is not None and unit_count else None,
            "error_rate": round(error_total / operation_total, 6) if operation_total else None,
            "llm_errors": llm_errors,
            "tool_errors": tool_errors,
        },
        "data_quality": {
            "cost_coverage_complete": cost_coverage.get("complete") if isinstance(cost_coverage.get("complete"), bool) else total_aiu is not None,
            "llm_calls_with_aiu": int(cost_coverage.get("llm_calls_with_aiu") or 0),
            "llm_calls_missing_aiu": int(cost_coverage.get("llm_calls_missing_aiu") or 0),
            "warnings": warnings,
        },
        "quality": quality or load_quality_evidence(Path.cwd(), None),
    }


def load_runs_from_input(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload.get("sessions"), list):
        return [
            normalize_run(item, label=f"{path.stem}:{index + 1}")
            for index, item in enumerate(payload["sessions"])
            if isinstance(item, dict)
        ]
    return [normalize_run(payload, label=path.stem)]


def load_manifest(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    entries = payload.get("runs")
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest.runs must be a non-empty array")
    runs = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not entry.get("metrics_path"):
            raise ValueError(f"manifest run {index + 1} requires metrics_path")
        metrics_path = resolve(path.parent, str(entry["metrics_path"]))
        metrics_payload = load_json(metrics_path)
        if isinstance(metrics_payload.get("sessions"), list):
            sessions = [item for item in metrics_payload["sessions"] if isinstance(item, dict)]
            if len(sessions) != 1:
                raise ValueError("manifest metrics_path must resolve to one session")
            metrics_payload = sessions[0]
        quality = load_quality_evidence(path.parent, entry.get("quality_evidence"))
        runs.append(normalize_run(
            metrics_payload,
            label=str(entry.get("label") or metrics_path.stem),
            workload_override=entry.get("workload") if isinstance(entry.get("workload"), dict) else None,
            quality=quality,
        ))
    return runs


def comparability(runs: list[dict[str, Any]]) -> dict[str, Any]:
    fingerprints = {run["workload"]["fingerprint"] for run in runs if run["workload"]["fingerprint"]}
    task_kinds = {run["workload"]["task_kind"] for run in runs if run["workload"]["task_kind"]}
    unit_names = {run["workload"]["unit_name"] for run in runs if run["workload"]["unit_name"]}
    scopes = {
        json.dumps(run["measurement_scope"], sort_keys=True, ensure_ascii=True)
        for run in runs if run["measurement_scope"] is not None
    }
    quality_levels = {run["quality"]["level"] for run in runs}
    reasons = []
    if len(fingerprints) == 1 and len(fingerprints) > 0 and len(scopes) <= 1:
        level = "HIGH"
    elif len(task_kinds) == 1 and len(task_kinds) > 0 and len(unit_names) == 1 and len(scopes) <= 1:
        level = "MEDIUM"
        reasons.append("Runs share a task class and unit but not an identical workload fingerprint.")
    else:
        level = "LOW"
        reasons.append("Runs differ in task class, unit, measurement scope, or lack workload metadata.")
    if len(scopes) > 1:
        level = "LOW"
        reasons.append("Measurement scopes differ.")
    if "UNMEASURED" in quality_levels:
        reasons.append("At least one run has no external quality evidence.")
    if len(runs) < 3:
        reasons.append("Sample size is below three runs.")
    return {"level": level, "reasons": reasons}


def quality_sort_key(run: dict[str, Any]) -> tuple[int, int, float]:
    quality = run["quality"]
    passed = 1 if quality["passed"] is True else 0
    residual = quality["adjudicated_residual_defects"]
    residual_score = -float(residual) if residual is not None else float("-inf")
    return QUALITY_LEVELS[quality["level"]], passed, residual_score


def winner(runs: list[dict[str, Any]], metric: str, *, require_quality: bool = False) -> dict[str, Any]:
    candidates = []
    for run in runs:
        if require_quality:
            if run["quality"]["level"] == "UNMEASURED" or run["quality"]["passed"] is not True:
                continue
            candidates.append(run)
        elif run["metrics"].get(metric) is not None:
            candidates.append(run)
    if not candidates:
        return {"status": "UNMEASURED", "label": None, "value": None}
    if require_quality:
        selected = max(candidates, key=quality_sort_key)
        value = selected["quality"]
    else:
        selected = min(candidates, key=lambda item: item["metrics"][metric])
        value = selected["metrics"][metric]
    return {"status": "AVAILABLE", "label": selected["label"], "value": value}


def pareto_frontier(runs: list[dict[str, Any]]) -> list[str]:
    candidates = [
        run for run in runs
        if run["metrics"]["aiu_per_unit"] is not None
        and run["metrics"]["elapsed_seconds_per_unit"] is not None
        and run["quality"]["passed"] is True
        and run["quality"]["level"] != "UNMEASURED"
    ]
    frontier = []
    for candidate in candidates:
        dominated = False
        candidate_quality = QUALITY_LEVELS[candidate["quality"]["level"]]
        for other in candidates:
            if other is candidate:
                continue
            other_quality = QUALITY_LEVELS[other["quality"]["level"]]
            no_worse = (
                other["metrics"]["aiu_per_unit"] <= candidate["metrics"]["aiu_per_unit"]
                and other["metrics"]["elapsed_seconds_per_unit"] <= candidate["metrics"]["elapsed_seconds_per_unit"]
                and other_quality >= candidate_quality
            )
            strictly_better = (
                other["metrics"]["aiu_per_unit"] < candidate["metrics"]["aiu_per_unit"]
                or other["metrics"]["elapsed_seconds_per_unit"] < candidate["metrics"]["elapsed_seconds_per_unit"]
                or other_quality > candidate_quality
            )
            if no_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(candidate["label"])
    return sorted(frontier)


def quartiles(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        median = q1 = q3 = sorted_values[0]
    else:
        q1, median, q3 = statistics.quantiles(sorted_values, n=4, method="inclusive")
    return {
        "median": round(median, 6),
        "q1": round(q1, 6),
        "q3": round(q3, 6),
        "iqr": round(q3 - q1, 6),
    }


def outlier_labels(members: list[dict[str, Any]], metric: str) -> list[str]:
    measured = [
        (item["label"], item["metrics"][metric])
        for item in members
        if item["metrics"][metric] is not None
    ]
    if len(measured) < 4:
        return []
    summary = quartiles([value for _, value in measured])
    if summary is None:
        return []
    lower = summary["q1"] - 1.5 * summary["iqr"]
    upper = summary["q3"] + 1.5 * summary["iqr"]
    return sorted(label for label, value in measured if value < lower or value > upper)


def grouped_summary(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        primary = run["primary_model"]
        groups[(primary["model"], primary["reasoning_effort"])].append(run)
    summaries = []
    for (model, effort), members in sorted(groups.items()):
        aiu = [item["metrics"]["aiu_per_unit"] for item in members if item["metrics"]["aiu_per_unit"] is not None]
        elapsed = [item["metrics"]["elapsed_seconds_per_unit"] for item in members if item["metrics"]["elapsed_seconds_per_unit"] is not None]
        summaries.append({
            "model": model,
            "reasoning_effort": effort,
            "sample_size": len(members),
            "aiu_per_unit": quartiles(aiu),
            "elapsed_seconds_per_unit": quartiles(elapsed),
            "outliers": {
                "aiu_per_unit": outlier_labels(members, "aiu_per_unit"),
                "elapsed_seconds_per_unit": outlier_labels(members, "elapsed_seconds_per_unit"),
            },
            "quality_passed": sum(item["quality"]["passed"] is True for item in members),
            "quality_measured": sum(item["quality"]["level"] != "UNMEASURED" for item in members),
        })
    return summaries


def parse_weights(value: str | None) -> dict[str, float] | None:
    if not value:
        return None
    candidate = Path(value).expanduser()
    payload = load_json(candidate.resolve()) if candidate.is_file() else json.loads(value)
    if not isinstance(payload, dict):
        raise ValueError("weights must be a JSON object")
    allowed = {"cost", "time", "quality"}
    unexpected = set(payload) - allowed
    if unexpected:
        raise ValueError(f"unsupported weight keys: {', '.join(sorted(unexpected))}")
    weights: dict[str, float] = {}
    for key in allowed:
        metric = number(payload.get(key, 0))
        if metric is None or metric < 0:
            raise ValueError(f"weight {key} must be a non-negative number")
        weights[key] = metric
    if sum(weights.values()) <= 0:
        raise ValueError("at least one weight must be positive")
    return weights


def weighted_ranking(runs: list[dict[str, Any]], weights: dict[str, float] | None) -> dict[str, Any] | None:
    if weights is None:
        return None
    required = [key for key, value in weights.items() if value > 0]
    eligible = []
    for run in runs:
        if "cost" in required and run["metrics"]["aiu_per_unit"] is None:
            continue
        if "time" in required and run["metrics"]["elapsed_seconds_per_unit"] is None:
            continue
        if "quality" in required and (
            run["quality"]["level"] == "UNMEASURED" or run["quality"]["passed"] is not True
        ):
            continue
        eligible.append(run)
    if not eligible:
        return {"status": "UNMEASURED", "weights": weights, "ranking": []}

    cost_values = [run["metrics"]["aiu_per_unit"] for run in eligible if run["metrics"]["aiu_per_unit"] is not None]
    time_values = [run["metrics"]["elapsed_seconds_per_unit"] for run in eligible if run["metrics"]["elapsed_seconds_per_unit"] is not None]
    cost_max = max(cost_values) if cost_values else 0
    time_max = max(time_values) if time_values else 0
    weight_total = sum(weights.values())
    ranking = []
    for run in eligible:
        components = {
            "cost": 1 - run["metrics"]["aiu_per_unit"] / cost_max if cost_max else 1,
            "time": 1 - run["metrics"]["elapsed_seconds_per_unit"] / time_max if time_max else 1,
            "quality": QUALITY_LEVELS[run["quality"]["level"]] / max(QUALITY_LEVELS.values()),
        }
        score = sum(weights[key] * components[key] for key in weights) / weight_total
        ranking.append({
            "label": run["label"],
            "score": round(score, 6),
            "components": {key: round(value, 6) for key, value in components.items()},
        })
    ranking.sort(key=lambda item: (-item["score"], item["label"]))
    return {"status": "AVAILABLE", "weights": weights, "ranking": ranking}


def compare_runs(runs: list[dict[str, Any]], weights: dict[str, float] | None = None) -> dict[str, Any]:
    if len(runs) < 2:
        raise ValueError("at least two runs are required for comparison")
    return {
        "status": "PASS",
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_count": len(runs),
        "comparability": comparability(runs),
        "winners": {
            "lowest_cost_per_unit": winner(runs, "aiu_per_unit"),
            "fastest_elapsed_per_unit": winner(runs, "elapsed_seconds_per_unit"),
            "fastest_active_llm_per_unit": winner(runs, "active_llm_seconds_per_unit"),
            "strongest_quality_evidence": winner(runs, "", require_quality=True),
        },
        "pareto_frontier": pareto_frontier(runs),
        "weighted_ranking": weighted_ranking(runs, weights),
        "groups": grouped_summary(runs),
        "runs": runs,
        "interpretation": {
            "cost_metric": "AIU is relative usage, not currency.",
            "quality_rule": "Log-only runs never receive an accuracy verdict.",
            "ranking_rule": "No weighted overall score is produced unless the caller supplies explicit weights.",
        },
    }


def session_analysis(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": run["label"],
        "session_id": run["session_id"],
        "source_format": run["source_format"],
        "primary_model": run["primary_model"],
        "workload": run["workload"],
        "metrics": run["metrics"],
        "usage_summary": run["usage_summary"],
        "data_quality": run["data_quality"],
        "quality": run["quality"],
    }


def analyze_runs(runs: list[dict[str, Any]], weights: dict[str, float] | None = None) -> dict[str, Any]:
    if not runs:
        raise ValueError("at least one run is required for analysis")
    comparison = compare_runs(runs, weights) if len(runs) >= 2 else None
    return {
        "status": "PASS",
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analysis_mode": "multi-session-comparison" if comparison is not None else "single-session",
        "run_count": len(runs),
        "sessions": [session_analysis(run) for run in runs],
        "comparison": comparison,
        "interpretation": {
            "cost_metric": "AIU is relative usage, not currency.",
            "quality_rule": "Log-only runs never receive an accuracy verdict.",
            "comparison_rule": "Winner and Pareto analysis are emitted only for two or more runs.",
        },
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def render(payload: dict[str, Any], json_only: bool) -> None:
    if not json_only:
        print("=== Copilot Session Analysis ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()
    try:
        if bool(args.manifest) == bool(args.inputs):
            raise ValueError("use either --manifest or positional inputs")
        if args.manifest:
            runs = load_manifest(Path(args.manifest).expanduser().resolve())
        else:
            runs = []
            for value in args.inputs:
                runs.extend(load_runs_from_input(Path(value).expanduser().resolve()))
        payload = analyze_runs(runs, parse_weights(args.weights))
        if args.output_json:
            atomic_write_json(Path(args.output_json), payload)
        render(payload, args.json_only)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {"status": "FAIL", "error": {"type": type(exc).__name__, "message": str(exc)}}
        render(payload, args.json_only)
        return 1 if args.strict_exit_codes else 0


if __name__ == "__main__":
    raise SystemExit(main())