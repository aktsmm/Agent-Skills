import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value)


def relative_file(root, value):
    require(isinstance(value, str) and value and "\\" not in value and ":" not in value, "invalid relative path")
    relative = PurePosixPath(value)
    require(not relative.is_absolute() and ".." not in relative.parts, "unsafe relative path")
    target = (root / value).resolve()
    require(target.is_relative_to(root) and target.is_file(), "file missing or outside approved root: " + value)
    return target


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)


def artifact(root, record):
    require(isinstance(record, dict), "missing artifact record")
    path = relative_file(root, record.get("path"))
    require(valid_hash(record.get("sha256")), "invalid artifact hash")
    require(digest(path) == record["sha256"], "artifact hash mismatch: " + record["path"])
    text = path.read_text(encoding="utf-8")
    require(bool(text.strip()), "empty saved artifact: " + record["path"])
    return text


def reading_coverage(document):
    units, reading = document.get("units", {}), document.get("reading", {})
    require(isinstance(units, dict) and isinstance(reading, dict), "invalid units or reading record")
    count = units.get("count")
    require(units.get("kind") in {"line", "page", "slide"} and type(count) is int and count > 0, "unknown unit count")
    status, ranges = reading.get("status"), reading.get("ranges")
    require(status in {"unread", "partial", "full"} and isinstance(ranges, list), "invalid reading state")
    previous, covered = 0, 0
    for span in ranges:
        require(isinstance(span, list) and len(span) == 2 and all(type(value) is int for value in span), "invalid read range")
        first, last = span
        require(previous < first <= last <= count, "overlapping, unsorted, or out-of-bounds read range")
        covered += last - first + 1
        previous = last
    require((status == "unread" and covered == 0) or (status == "partial" and 0 < covered < count) or (status == "full" and covered == count), "reading claim does not match ranges")
    return status


def note_links(root, path, text):
    prose = re.sub(r"(?ms)^(`{3,})[^\n]*\n.*?^\1[ \t]*$", "", text)
    for target in re.findall(r"\]\(([^)]+)\)", prose):
        if target.startswith(("https://", "http://", "#")):
            continue
        value = unquote(target.split("#", 1)[0])
        require(value and "\\" not in value and ":" not in value and not value.startswith("/"), "unsafe note link")
        linked = (path.parent / value).resolve()
        require(linked.is_relative_to(root) and linked.is_file(), "missing or external local note link: " + value)


def verify(ledger_path, source_roots=None, require_complete=False):
    root = ledger_path.resolve().parent
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    require(isinstance(ledger, dict) and ledger.get("version") == 1, "unsupported ledger version")
    sources, documents, notes, ocr = (ledger.get(key) for key in ("sources", "documents", "notes", "ocr"))
    require(all(isinstance(value, list) for value in (sources, documents, notes, ocr)), "ledger lists required")
    require(sources and documents and notes, "empty scope or no knowledge notes saved")
    source_ids = []
    for source in sources:
        require(isinstance(source, dict) and identifier(source.get("id")), "invalid source alias")
        source_ids.append(source["id"])
    require(len(set(source_ids)) == len(source_ids), "duplicate source alias")
    roots = {alias: Path(path).resolve() for alias, path in (source_roots or {}).items()}
    require(set(roots) <= set(source_ids) and all(path.is_dir() for path in roots.values()), "unknown or missing source root")
    by_id, reading, freshness = {}, Counter(), set()
    for document in documents:
        require(isinstance(document, dict) and identifier(document.get("id")), "invalid document ID")
        doc_id, source_id = document["id"], document.get("source_id")
        require(doc_id not in by_id and source_id in source_ids, "duplicate document or unknown source")
        by_id[doc_id] = document
        relative = document.get("relative_path")
        require(isinstance(relative, str) and relative and "\\" not in relative and ":" not in relative and not PurePosixPath(relative).is_absolute() and ".." not in PurePosixPath(relative).parts, "unsafe source-relative path")
        require(document.get("role") in {"original", "derived", "auxiliary"}, "invalid document role")
        status = document.get("status")
        require(status in {"pending", "extracted", "empty", "blocked", "excluded"}, "invalid extraction status")
        if status != "extracted":
            require(isinstance(document.get("reason"), str) and document["reason"].strip(), "non-extracted state needs reason")
        else:
            require(valid_hash(document.get("source_sha256")), "extracted source needs hash")
            artifact(root, document.get("extraction"))
            reading[reading_coverage(document)] += 1
        if source_id in roots and document.get("source_sha256") is not None:
            require(valid_hash(document["source_sha256"]), "invalid source hash")
            path = relative_file(roots[source_id], relative)
            require(digest(path) == document["source_sha256"], "source changed: " + doc_id)
            freshness.add(doc_id)
    cited, note_paths = set(), set()
    for note in notes:
        require(isinstance(note, dict), "invalid note record")
        path = relative_file(root, note.get("path"))
        require(path not in note_paths, "duplicate note path")
        note_paths.add(path)
        text = path.read_text(encoding="utf-8")
        require(bool(text.strip()), "empty note")
        citations = note.get("sources")
        require(isinstance(citations, list) and citations and all(isinstance(doc_id, str) for doc_id in citations), "note needs source IDs")
        for doc_id in citations:
            require(doc_id in by_id and by_id[doc_id]["status"] == "extracted" and by_id[doc_id]["reading"]["status"] != "unread", "note cites unread or unavailable source")
            cited.add(doc_id)
        note_links(root, path, text)
    ocr_complete = True
    for item in ocr:
        require(isinstance(item, dict), "invalid OCR record")
        doc_id, unit = item.get("document_id"), item.get("unit")
        require(doc_id in by_id, "unknown OCR source")
        count = by_id[doc_id].get("units", {}).get("count")
        require(type(unit) is int and type(count) is int and 1 <= unit <= count, "OCR unit out of bounds")
        status, review = item.get("status"), item.get("review")
        require(status in {"pending", "recognized", "no-text", "failed"} and review in {"machine", "checked"}, "invalid OCR state")
        if status == "recognized":
            artifact(root, item.get("result"))
        else:
            require(isinstance(item.get("reason"), str) and item["reason"].strip(), "OCR outcome needs reason")
        ocr_complete &= status in {"recognized", "no-text"} and review == "checked"
    included = [document for document in documents if document["status"] != "excluded"]
    complete = bool(included) and all(document["status"] == "extracted" and document["reading"]["status"] == "full" and document["id"] in cited and document["id"] in freshness for document in included) and ocr_complete and set(roots) == set(source_ids)
    require(not require_complete or complete, "declared scope is incomplete or sources are not freshly checked")
    return {"result": "PASS", "complete_declared_scope": complete, "documents": len(documents), "extraction_states": dict(Counter(document["status"] for document in documents)), "reading_states": dict(reading), "notes": len(notes), "cited_documents": len(cited), "fresh_sources_checked": len(freshness), "source_ids_unchecked": sorted(set(source_ids) - set(roots)), "document_ids_unchecked": sorted(set(by_id) - freshness), "ocr_states": dict(Counter(item["status"] for item in ocr))}


def main():
    parser = argparse.ArgumentParser(description="Read-only checks for a populated document knowledge ledger")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--source-root", action="append", default=[], metavar="ALIAS=PATH")
    parser.add_argument("--require-complete", action="store_true")
    arguments = parser.parse_args()
    try:
        roots = {}
        for assignment in arguments.source_root:
            alias, separator, path = assignment.partition("=")
            require(separator and alias not in roots and path, "invalid or duplicate source-root assignment")
            roots[alias] = path
        result = verify(arguments.ledger, roots, arguments.require_complete)
    except (ValidationError, OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
        message = str(error) if isinstance(error, ValidationError) else type(error).__name__
        print(json.dumps({"result": "FAIL", "reason": message}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())