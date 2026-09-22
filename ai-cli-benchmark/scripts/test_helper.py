import json
import tempfile
import unittest
from pathlib import Path

from helper import validate


class HelperTests(unittest.TestCase):
    def write_fixture(self, directory: str, cached: int) -> Path:
        path = Path(directory) / "result.json"
        path.write_text(
            json.dumps(
                {
                    "test_design": {
                        "prompt_sha256": "a" * 64,
                        "cache_observation": {
                            "nonce_added_at_prompt_start": True,
                            "nonce_sha256": "b" * 64,
                        },
                    },
                    "providers": [
                        {
                            "provider": "copilot",
                            "elapsed_ms": 100,
                            "cases": 10,
                            "passed": 10,
                            "usage": {
                                "input_tokens": 1000,
                                "cached_input_tokens": cached,
                                "cache_write_tokens": 0,
                                "output_tokens": 100,
                                "reasoning_tokens": 0,
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_accepts_cache_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            result = validate(self.write_fixture(directory, 128), True, False)
            self.assertEqual(result["providers"][0]["cache_read"], 128)

    def test_zero_cache_gate_rejects_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "128 cached input tokens"):
                validate(self.write_fixture(directory, 128), True, True)

    def test_zero_cache_gate_ignores_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, 0)
            document = json.loads(path.read_text(encoding="utf-8"))
            document["providers"][0]["usage"]["cache_write_tokens"] = 256
            path.write_text(json.dumps(document), encoding="utf-8")
            result = validate(path, True, True)
            self.assertEqual(result["providers"][0]["cache_write"], 256)


if __name__ == "__main__":
    unittest.main()
