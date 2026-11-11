import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_summary.py")


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class CheckSummaryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.record = self.root / "record.json"
        self.record.write_text(
            json.dumps({"evidence": [{"id": "a"}, {"id": "b"}]}), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, text: str) -> Path:
        path = self.root / "summary.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_clean_summary_passes_with_matching_count(self) -> None:
        path = self.write("【先に結論】\n画面証跡2枚。https://example.com/a を参照。\n")
        result = run(str(path), "--evidence-record", str(self.record))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_forbidden_patterns_are_reported(self) -> None:
        text = "C:\\work\\a.md と user@example.com と <宛先> と ```\n"
        result = run(str(self.write(text)))
        self.assertEqual(result.returncode, 1)
        for name in ("absolute path", "email address", "placeholder", "code fence"):
            self.assertIn(name, result.stdout)

    def test_count_mismatch_is_reported(self) -> None:
        path = self.write("画面証跡5枚\n")
        result = run(str(path), "--evidence-record", str(self.record))
        self.assertEqual(result.returncode, 1)
        self.assertIn("record 2", result.stdout)

    def test_missing_summary_is_rejected(self) -> None:
        result = run(str(self.root / "missing.md"))
        self.assertEqual(result.returncode, 2)

    def test_missing_record_is_rejected(self) -> None:
        path = self.write("画面証跡2枚\n")
        result = run(str(path), "--evidence-record", str(self.root / "nope.json"))
        self.assertEqual(result.returncode, 2)

    def test_checker_does_not_modify_files(self) -> None:
        path = self.write("C:\\x\n")
        before = path.read_bytes()
        run(str(path), "--evidence-record", str(self.record))
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
