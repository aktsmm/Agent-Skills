#!/usr/bin/env python3

from __future__ import annotations

import os
import stat
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

from quick_validate import validate_skill


WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def should_package(file_path: Path, skill_path: Path) -> bool:
    relative = file_path.relative_to(skill_path)
    if file_path.is_symlink() or "__pycache__" in relative.parts:
        return False
    if file_path.suffix.lower() in {".pyc", ".pyo"}:
        return False
    return file_path.name not in {".DS_Store", "Thumbs.db"}


def validate_archive_path(name: str, root: str, seen: set[str]) -> str | None:
    if "\\" in name or not name:
        return "Archive entry must use a non-empty POSIX path"
    path = PurePosixPath(name)
    if path.is_absolute() or len(path.parts) < 2 or path.parts[0] != root:
        return "Archive entry is outside the expected Skill root"
    for component in path.parts:
        normalized = unicodedata.normalize("NFC", component)
        if component in {"", ".", ".."} or component != normalized:
            return "Archive entry has an unsafe path component"
        if component.endswith((".", " ")) or ":" in component or any(ord(char) < 32 for char in component):
            return "Archive entry has a Windows-unsafe path component"
        if component.split(".")[0].upper() in WINDOWS_RESERVED:
            return "Archive entry uses a reserved Windows device name"
    key = "/".join(unicodedata.normalize("NFC", part).casefold() for part in path.parts)
    if key in seen:
        return "Archive has a duplicate or case-fold-colliding entry"
    seen.add(key)
    return None


def validate_archive(archive: Path, skill_name: str) -> tuple[bool, str]:
    seen: set[str] = set()
    required_entries = {f"{skill_name}/SKILL.md"}
    with zipfile.ZipFile(archive) as packaged:
        for info in packaged.infolist():
            if info.is_dir():
                return False, "Archive must not contain directory entries"
            file_type = (info.external_attr >> 16) & 0o170000
            if file_type and not stat.S_ISREG(file_type):
                return False, "Archive must contain regular files only"
            error = validate_archive_path(info.filename, skill_name, seen)
            if error:
                return False, error
            required_entries.discard(info.filename)
    if required_entries:
        return False, "Archive is missing required Skill files"
    return True, "Archive is valid"


def package_skill(skill_path: str | Path, output_dir: str | Path | None = None) -> Path | None:
    supplied_skill_path = Path(skill_path)
    if supplied_skill_path.is_symlink():
        print(f"Error: Skill folder not found or unsafe: {supplied_skill_path}")
        return None
    skill_path = supplied_skill_path.resolve()
    if not skill_path.is_dir():
        print(f"Error: Skill folder not found or unsafe: {skill_path}")
        return None
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"Validation failed: {message}")
        return None
    print(message)

    supplied_output_path = Path(output_dir) if output_dir else Path.cwd()
    if supplied_output_path.is_symlink():
        print(f"Error: Output folder is unsafe: {supplied_output_path}")
        return None
    output_path = supplied_output_path.resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    archive = output_path / f"{skill_path.name}.skill"
    temporary_archive: Path | None = None
    try:
        handle, temporary_name = tempfile.mkstemp(prefix=f".{skill_path.name}-", suffix=".skill", dir=output_path)
        os.close(handle)
        Path(temporary_name).unlink(missing_ok=True)
        temporary_archive = Path(temporary_name)
        with zipfile.ZipFile(temporary_archive, "w", zipfile.ZIP_DEFLATED) as packaged:
            for file_path in skill_path.rglob("*"):
                if file_path.is_file() and should_package(file_path, skill_path):
                    packaged.write(file_path, file_path.relative_to(skill_path.parent).as_posix())
        valid, message = validate_archive(temporary_archive, skill_path.name)
        if not valid:
            print(f"Archive validation failed: {message}")
            return None
        temporary_archive.replace(archive)
        temporary_archive = None
        print(f"Successfully packaged Skill to: {archive}")
        return archive
    except (OSError, zipfile.BadZipFile) as error:
        print(f"Error creating Skill package: {error}")
        return None
    finally:
        if temporary_archive is not None:
            temporary_archive.unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) not in {2, 3}:
        print("Usage: python package_skill.py <skill-folder> [output-directory]")
        raise SystemExit(1)
    result = package_skill(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
    raise SystemExit(0 if result else 1)
