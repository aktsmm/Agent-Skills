import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("analyze_session_metrics.py")
SPEC = importlib.util.spec_from_file_location("analyze_session_metrics", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CompareSessionMetricsTests(unittest.TestCase):
    def payload(
        self,
        model: str,
        effort: str,
        *,
        aiu: float | None,
        elapsed: float,
        active: float,
        unit_count: int,
        fingerprint: str,
        scope: str = "same-scope",
    ) -> dict:
        return {
            "source_format": "vscode-copilot-chat-debug-log",
            "session_id": model,
            "measurement_scope": scope,
            "primary_model": {"model": model, "reasoning_effort": effort},
            "workload": {
                "task_kind": "review",
                "unit_name": "question",
                "unit_count": unit_count,
                "fingerprint": fingerprint,
            },
            "timing": {"session_observed_seconds": elapsed, "active_llm_seconds": active},
            "cost": {"total_aiu": aiu},
            "operations": {"llm_calls": 10, "llm_errors": 0, "tool_calls": 20, "tool_errors": 1},
            "usage": [
                {
                    "role": "orchestrator",
                    "model": model,
                    "reasoning_effort": effort,
                    "llm_calls": 10,
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "cached_tokens": 50,
                    "nano_aiu": int(aiu * 1_000_000_000) if aiu is not None else 0,
                    "llm_duration_seconds": active,
                }
            ],
            "warnings": [],
        }

    def quality(self, level: str = "GATE_SUPPORTED", passed: bool = True, residual: int = 0) -> dict:
        return {
            "level": level,
            "passed": passed,
            "gate_count": 1,
            "failed_gate_count": 0 if passed else 1,
            "adjudicated_residual_defects": residual,
            "notes": [],
        }

    def test_same_workload_normalizes_per_unit_and_returns_pareto(self):
        sol = MODULE.normalize_run(
            self.payload("sol", "xhigh", aiu=100, elapsed=600, active=500, unit_count=10, fingerprint="same"),
            label="sol",
            quality=self.quality(),
        )
        terra = MODULE.normalize_run(
            self.payload("terra", "max", aiu=150, elapsed=300, active=400, unit_count=10, fingerprint="same"),
            label="terra",
            quality=self.quality(),
        )

        result = MODULE.compare_runs([sol, terra])

        self.assertEqual(result["comparability"]["level"], "HIGH")
        self.assertEqual(result["winners"]["lowest_cost_per_unit"]["label"], "sol")
        self.assertEqual(result["winners"]["fastest_elapsed_per_unit"]["label"], "terra")
        self.assertEqual(result["pareto_frontier"], ["sol", "terra"])

    def test_single_run_returns_session_analysis_without_comparison(self):
        run = MODULE.normalize_run(
            self.payload("sol", "xhigh", aiu=100, elapsed=600, active=500, unit_count=10, fingerprint="one"),
            label="single-run",
            quality=self.quality(),
        )

        result = MODULE.analyze_runs([run])

        self.assertEqual(result["analysis_mode"], "single-session")
        self.assertEqual(result["run_count"], 1)
        self.assertIsNone(result["comparison"])
        self.assertEqual(result["sessions"][0]["label"], "single-run")
        self.assertEqual(result["sessions"][0]["usage_summary"]["agent_role_count"], 1)
        configuration = result["sessions"][0]["usage_summary"]["model_configurations"][0]
        self.assertEqual(configuration["aiu"], 100.0)
        self.assertEqual(configuration["llm_duration_seconds"], 500.0)
        self.assertEqual(configuration["input_tokens"], 100)
        self.assertEqual(result["sessions"][0]["quality"]["level"], "GATE_SUPPORTED")

    def test_detailed_review_adapter_uses_question_count_and_existing_aiu_field(self):
        run = MODULE.normalize_run({
            "session_id": "review",
            "question_count": 20,
            "measurement_scope": {"included": "all worker calls"},
            "primary_model": {"model": "gpt-5.6-sol", "reasoning_effort": "xhigh"},
            "timing": {"review_elapsed_seconds": 1000, "active_llm_seconds": 800},
            "cost": {"total_aiu": 50, "aiu_per_question": 2.5},
            "operations": {"llm_calls": 5, "tool_calls": 5},
        }, label="review")

        self.assertEqual(run["workload"]["unit_name"], "question")
        self.assertEqual(run["workload"]["unit_count"], 20)
        self.assertEqual(run["metrics"]["aiu_per_unit"], 2.5)
        self.assertEqual(run["quality"]["level"], "UNMEASURED")

    def test_quality_requires_external_evidence_and_unknown_gate_does_not_pass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            gate = root / "gate.json"
            gate.write_text(json.dumps({"status": "UNKNOWN"}), encoding="utf-8")

            quality = MODULE.load_quality_evidence(root, {"gate_paths": ["gate.json"]})

            self.assertEqual(quality["level"], "GATE_SUPPORTED")
            self.assertFalse(quality["passed"])
            self.assertEqual(quality["failed_gate_count"], 1)

    def test_scope_mismatch_and_unmeasured_quality_lower_confidence(self):
        first = MODULE.normalize_run(
            self.payload("one", "high", aiu=10, elapsed=100, active=80, unit_count=10, fingerprint="one", scope="scope-a"),
            label="one",
            quality=self.quality(),
        )
        second = MODULE.normalize_run(
            self.payload("two", "high", aiu=20, elapsed=200, active=100, unit_count=20, fingerprint="two", scope="scope-b"),
            label="two",
        )

        result = MODULE.compare_runs([first, second])

        self.assertEqual(result["comparability"]["level"], "LOW")
        self.assertEqual(result["winners"]["strongest_quality_evidence"]["label"], "one")
        self.assertEqual(result["pareto_frontier"], ["one"])
        self.assertTrue(any("quality evidence" in reason for reason in result["comparability"]["reasons"]))

    def test_group_summary_reports_median_iqr_and_sample_size(self):
        runs = []
        for index, aiu in enumerate((10, 20, 100)):
            runs.append(MODULE.normalize_run(
                self.payload("same", "high", aiu=aiu, elapsed=aiu * 2, active=aiu, unit_count=10, fingerprint=str(index)),
                label=f"run-{index}",
                quality=self.quality(),
            ))

        result = MODULE.compare_runs(runs)

        group = result["groups"][0]
        self.assertEqual(group["sample_size"], 3)
        self.assertEqual(group["aiu_per_unit"]["median"], 2.0)
        self.assertGreater(group["aiu_per_unit"]["iqr"], 0)

    def test_outliers_are_labeled_and_weighted_ranking_requires_explicit_weights(self):
        runs = []
        for index, aiu in enumerate((10, 10, 10, 10, 100)):
            runs.append(MODULE.normalize_run(
                self.payload("same", "high", aiu=aiu, elapsed=aiu, active=aiu, unit_count=10, fingerprint="same"),
                label=f"run-{index}",
                quality=self.quality(),
            ))

        default_result = MODULE.compare_runs(runs)
        weighted_result = MODULE.compare_runs(runs, {"cost": 1.0, "time": 0.0, "quality": 0.0})

        self.assertIsNone(default_result["weighted_ranking"])
        self.assertEqual(default_result["groups"][0]["outliers"]["aiu_per_unit"], ["run-4"])
        self.assertEqual(weighted_result["weighted_ranking"]["status"], "AVAILABLE")
        self.assertIn(weighted_result["weighted_ranking"]["ranking"][0]["label"], {"run-0", "run-1", "run-2", "run-3"})


if __name__ == "__main__":
    unittest.main()