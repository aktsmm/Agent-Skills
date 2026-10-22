import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from verify_library import ValidationError, digest, verify


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.library = self.root / "library"
        self.originals = self.root / "sources"
        self.library.mkdir()
        self.originals.mkdir()
        (self.library / "extracted").mkdir()
        (self.library / "notes").mkdir()
        original = self.originals / "chapter.md"
        original.write_text("# Design\nSmall inputs\nCheck outputs\n", encoding="utf-8")
        extracted = self.library / "extracted/chapter.md"
        extracted.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")
        (self.library / "notes/topic.md").write_text("# Design\nRead document-a lines 1-3.\n[Evidence](../extracted/chapter.md)\n", encoding="utf-8")
        self.ledger = {"version": 1, "sources": [{"id": "source-a"}], "documents": [{"id": "document-a", "source_id": "source-a", "relative_path": "chapter.md", "role": "original", "status": "extracted", "source_sha256": digest(original), "extraction": {"path": "extracted/chapter.md", "sha256": digest(extracted)}, "units": {"kind": "line", "count": 3}, "reading": {"status": "full", "ranges": [[1, 3]]}}], "notes": [{"path": "notes/topic.md", "sources": ["document-a"]}], "ocr": []}
        self.path = self.library / "source-ledger.json"

    def run_check(self, roots=None, complete=False):
        self.path.write_text(json.dumps(self.ledger), encoding="utf-8")
        return verify(self.path, roots, complete)

    def test_valid_complete_scope(self):
        result = self.run_check({"source-a": self.originals}, True)
        self.assertTrue(result["complete_declared_scope"])
        self.assertEqual(result["fresh_sources_checked"], 1)

    def test_without_roots_does_not_claim_freshness(self):
        self.assertFalse(self.run_check()["complete_declared_scope"])
        self.assertEqual(self.run_check()["source_ids_unchecked"], ["source-a"])
        with self.assertRaises(ValidationError):
            self.run_check(complete=True)

    def test_empty_notes_or_scope_rejected(self):
        for field in ("sources", "documents", "notes"):
            with self.subTest(field=field):
                saved = self.ledger[field]
                self.ledger[field] = []
                with self.assertRaises(ValidationError):
                    self.run_check()
                self.ledger[field] = saved

    def test_missing_or_changed_extract_rejected(self):
        (self.library / "extracted/chapter.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "hash mismatch"):
            self.run_check()
        (self.library / "extracted/chapter.md").unlink()
        with self.assertRaises(ValidationError):
            self.run_check()

    def test_changed_original_rejected(self):
        (self.originals / "chapter.md").write_text("new version", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "source changed"):
            self.run_check({"source-a": self.originals})

    def test_reading_claims_match_actual_ranges(self):
        for ranges in ([[1, 1], [3, 3]], [[1, 2], [2, 3]], [[1, 4]], [[0, 3]], []):
            with self.subTest(ranges=ranges):
                self.ledger["documents"][0]["reading"]["ranges"] = ranges
                with self.assertRaises(ValidationError):
                    self.run_check()

    def test_partial_reading_is_reported_not_promoted(self):
        self.ledger["documents"][0]["reading"] = {"status": "partial", "ranges": [[1, 2]]}
        self.assertEqual(self.run_check()["reading_states"], {"partial": 1})
        with self.assertRaises(ValidationError):
            self.run_check({"source-a": self.originals}, True)

    def test_note_cannot_cite_unread_document(self):
        self.ledger["documents"][0]["reading"] = {"status": "unread", "ranges": []}
        with self.assertRaises(ValidationError):
            self.run_check()

    def test_source_and_output_paths_are_confined(self):
        for invalid in ("../secret.md", "/absolute.md", "C:/secret.md", "sub\\secret.md"):
            with self.subTest(path=invalid):
                self.ledger["documents"][0]["relative_path"] = invalid
                with self.assertRaises(ValidationError):
                    self.run_check()

    def test_note_links_reject_escape_and_missing_targets(self):
        for target in ("../../outside.md", "missing.md", "file:///secret.md", "%2E%2E/%2E%2E/outside.md"):
            (self.library / "notes/topic.md").write_text(f"[Bad]({target})", encoding="utf-8")
            with self.assertRaises(ValidationError):
                self.run_check()

    def test_code_fences_are_not_links(self):
        (self.library / "notes/topic.md").write_text("# Evidence\n```text\n[example](nonexistent.md)\n```\n", encoding="utf-8")
        self.assertEqual(self.run_check()["result"], "PASS")

    def test_blockers_have_reasons_and_remain_incomplete(self):
        blocked = {"id": "document-b", "source_id": "source-a", "relative_path": "locked.pptx", "role": "original", "status": "blocked", "reason": "Protected input"}
        self.ledger["documents"].append(blocked)
        self.assertEqual(self.run_check()["extraction_states"]["blocked"], 1)
        with self.assertRaises(ValidationError):
            self.run_check({"source-a": self.originals}, True)
        blocked["reason"] = ""
        with self.assertRaises(ValidationError):
            self.run_check()

    def test_duplicate_ids_rejected(self):
        self.ledger["documents"].append(copy.deepcopy(self.ledger["documents"][0]))
        with self.assertRaises(ValidationError):
            self.run_check()

    def test_ocr_checked_is_separate_from_processed(self):
        item = {"document_id": "document-a", "unit": 1, "status": "no-text", "review": "machine", "reason": "No text recognized"}
        self.ledger["ocr"].append(item)
        self.assertEqual(self.run_check()["ocr_states"], {"no-text": 1})
        with self.assertRaises(ValidationError):
            self.run_check({"source-a": self.originals}, True)
        item["review"] = "checked"
        self.assertTrue(self.run_check({"source-a": self.originals}, True)["complete_declared_scope"])

    def test_recognized_ocr_requires_saved_nonempty_text(self):
        self.ledger["ocr"].append({"document_id": "document-a", "unit": 1, "status": "recognized", "review": "machine"})
        with self.assertRaises(ValidationError):
            self.run_check()

    def test_no_text_ocr_requires_explanation(self):
        self.ledger["ocr"].append({"document_id": "document-a", "unit": 1, "status": "no-text", "review": "checked", "reason": ""})
        with self.assertRaisesRegex(ValidationError, "OCR outcome needs reason"):
            self.run_check({"source-a": self.originals}, True)

    def test_cli_success_and_failure_outputs(self):
        self.run_check()
        script = Path(__file__).with_name("verify_library.py")
        command = [sys.executable, "-B", str(script), str(self.path), "--source-root", f"source-a={self.originals}", "--require-complete"]
        before = {path.relative_to(self.root): digest(path) for path in self.root.rglob("*") if path.is_file()}
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["complete_declared_scope"])
        after = {path.relative_to(self.root): digest(path) for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.ledger["notes"] = []
        self.path.write_text(json.dumps(self.ledger), encoding="utf-8")
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["result"], "FAIL")

    def test_multiple_roots_and_reviewed_ocr(self):
        other_root = self.root / "other-source"
        other_root.mkdir()
        original = other_root / "\u8cc7\u6599.txt"
        original.write_text("Example workflow\nCheck the source\n", encoding="utf-8")
        extracted = self.library / "extracted/other.md"
        extracted.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")
        self.ledger["sources"].append({"id": "source-b"})
        self.ledger["documents"].append({"id": "document-b", "source_id": "source-b", "relative_path": original.name, "role": "original", "status": "extracted", "source_sha256": digest(original), "extraction": {"path": "extracted/other.md", "sha256": digest(extracted)}, "units": {"kind": "line", "count": 2}, "reading": {"status": "full", "ranges": [[1, 2]]}})
        self.ledger["notes"][0]["sources"].append("document-b")
        result_path = self.library / "extracted/ocr.md"
        result_path.write_text("Diagram label", encoding="utf-8")
        self.ledger["ocr"].append({"document_id": "document-b", "unit": 2, "status": "recognized", "review": "checked", "result": {"path": "extracted/ocr.md", "sha256": digest(result_path)}})
        result = self.run_check({"source-a": self.originals, "source-b": other_root}, True)
        self.assertTrue(result["complete_declared_scope"])
        self.assertEqual(result["fresh_sources_checked"], 2)
        self.assertEqual(result["reading_states"], {"full": 2})
        self.assertEqual(result["ocr_states"], {"recognized": 1})


if __name__ == "__main__":
    unittest.main()