import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("extract_session_metrics.py")
SPEC = importlib.util.spec_from_file_location("extract_session_metrics", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ExtractSessionMetricsTests(unittest.TestCase):
    def write_event(self, path: Path, event: dict) -> None:
        with path.open("ab") as handle:
            handle.write((json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8"))

    def create_session(self, root: Path, session_id: str = "11111111-1111-4111-8111-111111111111") -> Path:
        session = root / session_id
        session.mkdir()
        main = session / "main.jsonl"
        self.write_event(main, {
            "ts": 1000,
            "dur": 2000,
            "type": "llm_request",
            "status": "ok",
            "spanId": "main-1",
            "attrs": {
                "model": "gpt-5.6-sol",
                "requestOptions": json.dumps({"reasoning": {"effort": "xhigh"}}),
                "inputTokens": 100,
                "outputTokens": 20,
                "cachedTokens": 50,
                "copilotUsageNanoAiu": 2_000_000_000,
                "userRequest": "secret prompt that must not be emitted",
            },
        })
        self.write_event(main, {
            "ts": 6000,
            "dur": 0,
            "type": "agent_response",
            "status": "ok",
            "spanId": "main-response",
            "attrs": {"response": "private response"},
        })
        self.write_event(main, {
            "ts": 5000,
            "dur": 100,
            "type": "tool_call",
            "status": "error",
            "spanId": "tool-1",
            "attrs": {"args": "secret command"},
        })
        child = session / "runSubagent-Chunk Reviewer-call_ABC123.jsonl"
        self.write_event(child, {
            "ts": 2000,
            "dur": 3000,
            "type": "llm_request",
            "status": "ok",
            "spanId": "child-1",
            "attrs": {
                "model": "gpt-5.6-terra",
                "requestOptions": {"output_config": {"effort": "medium"}},
                "inputTokens": 80,
                "outputTokens": 10,
                "cachedTokens": 40,
                "copilotUsageNanoAiu": 1_000_000_000,
            },
        })
        return session

    def test_aggregates_main_child_reasoning_aiu_and_privacy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = self.create_session(Path(tmpdir))

            metrics = MODULE.extract_session(
                session,
                workload={"unit_count": 10, "unit_name": "question", "task_kind": "review"},
            )

            self.assertEqual(metrics["primary_model"], {"model": "gpt-5.6-sol", "reasoning_effort": "xhigh"})
            self.assertEqual(metrics["cost"]["total_aiu"], 3.0)
            self.assertEqual(metrics["cost"]["aiu_per_unit"], 0.3)
            self.assertEqual(metrics["timing"]["session_observed_seconds"], 5.0)
            self.assertEqual({item["role"] for item in metrics["usage"]}, {"orchestrator", "Chunk Reviewer"})
            self.assertEqual(metrics["operations"]["tool_errors"], 1)
            serialized = json.dumps(metrics, ensure_ascii=False)
            self.assertNotIn("secret prompt", serialized)
            self.assertNotIn("private response", serialized)
            self.assertNotIn(str(session.parent), serialized)

    def test_missing_aiu_invalid_lines_duplicates_and_cutoff_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = self.create_session(Path(tmpdir))
            main = session / "main.jsonl"
            duplicate = {
                "ts": 3000,
                "dur": 1000,
                "type": "llm_request",
                "status": "ok",
                "spanId": "missing-aiu",
                "attrs": {"model": "gpt-5.6-sol", "inputTokens": 5, "outputTokens": 1},
            }
            self.write_event(main, duplicate)
            self.write_event(main, duplicate)
            with main.open("ab") as handle:
                handle.write(b'{"partial":\n')
                handle.write(b'\xff\n')

            metrics = MODULE.extract_session(session, after=1500, before=5000)

            self.assertIsNone(metrics["cost"]["total_aiu"])
            self.assertFalse(metrics["cost"]["coverage"]["complete"])
            warning_codes = {item["code"]: item["count"] for item in metrics["warnings"]}
            self.assertEqual(warning_codes["duplicate_events_skipped"], 1)
            self.assertGreaterEqual(warning_codes["invalid_json_lines_skipped"], 2)
            self.assertGreaterEqual(warning_codes["invalid_utf8_replaced"], 1)
            self.assertEqual(metrics["operations"]["llm_calls"], 2)

    def test_recent_and_contains_filter_sessions_without_emitting_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = self.create_session(root, "11111111-1111-4111-8111-111111111111")
            second = self.create_session(root, "22222222-2222-4222-8222-222222222222")
            second_main = second / "main.jsonl"
            text = second_main.read_text(encoding="utf-8").replace("secret prompt", "comparison target")
            second_main.write_text(text, encoding="utf-8")
            first_main = first / "main.jsonl"
            first_main.touch()

            args = type("Args", (), {
                "session_dir": [],
                "debug_root": [str(root)],
                "session_id": [],
                "recent": 2,
                "contains": "comparison target",
            })()

            selected = MODULE.select_session_dirs(args)

            self.assertEqual(selected, [second.resolve()])


if __name__ == "__main__":
    unittest.main()