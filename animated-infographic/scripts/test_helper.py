import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


class HelperTests(unittest.TestCase):
    def test_illustrative_gif_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gif_path = root / "test.gif"
            report_path = root / "report.json"
            sheet_path = root / "sheet.jpg"
            frames = [
                Image.new("RGB", (120, 68), color) for color in ("red", "green", "blue")
            ]
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=100,
                loop=0,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("helper.py")),
                    str(gif_path),
                    "--expected-width",
                    "120",
                    "--expected-height",
                    "68",
                    "--timing-mode",
                    "illustrative",
                    "--contact-sheet",
                    str(sheet_path),
                    "--report",
                    str(report_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(sheet_path.exists())

    def test_measured_duration_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            gif_path = Path(directory) / "test.gif"
            frames = [Image.new("RGB", (80, 45), color) for color in ("red", "blue")]
            frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=100)
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("helper.py")),
                    str(gif_path),
                    "--timing-mode",
                    "measured",
                    "--measured-ms",
                    "1000",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
