#!/usr/bin/env python3
"""Scan alembic/versions for duplicate revision IDs and broken down_revision links."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSIONS = HERE / "alembic" / "versions"

# One line per file is enough for our migrations (avoid brittle Union[...] parsing).
REV_LINE = re.compile(r"^revision[^\n=]*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)
DOWN_LINE = re.compile(r"^down_revision[^\n=]*=\s*(.+)\s*$", re.MULTILINE)


def parse_down_value(raw: str) -> str | tuple[str, ...] | None:
    raw = raw.strip()
    if raw == "None":
        return None
    if raw.startswith("("):
        inner = raw.strip("() \n")
        parts = [p.strip().strip("\"'") for p in inner.split(",") if p.strip()]
        return tuple(parts) if parts else None
    return raw.strip("\"'")


def main() -> int:
    if not VERSIONS.is_dir():
        print(f"Missing directory: {VERSIONS}", file=sys.stderr)
        return 1

    rev_to_files: dict[str, list[str]] = {}
    file_to_rev: dict[str, str] = {}
    file_to_down: dict[str, str | tuple[str, ...] | None] = {}

    for path in sorted(VERSIONS.glob("*.py")):
        if path.name.startswith("__"):
            continue
        text = path.read_text(encoding="utf-8")
        rm = REV_LINE.search(text)
        if not rm:
            print(f"SKIP (no revision id): {path.name}", file=sys.stderr)
            continue
        rev = rm.group(1)
        rev_to_files.setdefault(rev, []).append(path.name)
        file_to_rev[path.name] = rev

        dm = DOWN_LINE.search(text)
        if not dm:
            print(f"SKIP (no down_revision): {path.name}", file=sys.stderr)
            continue
        file_to_down[path.name] = parse_down_value(dm.group(1))

    dupes = {r: fs for r, fs in rev_to_files.items() if len(fs) > 1}
    if dupes:
        print("DUPLICATE revision ids (fix: keep one file per id, delete or rename extras):")
        for rev, files in sorted(dupes.items()):
            print(f"  {rev}: {', '.join(files)}")
        print()

    all_revs = set(rev_to_files.keys())
    missing_targets: list[tuple[str, str, str | tuple[str, ...]]] = []
    for fname, down in file_to_down.items():
        if down is None:
            continue
        targets = down if isinstance(down, tuple) else (down,)
        for t in targets:
            if t not in all_revs:
                missing_targets.append((fname, file_to_rev[fname], t))

    if missing_targets:
        print("down_revision points to MISSING revision (fix: add file or correct id):")
        for fname, rev, target in missing_targets:
            print(f"  {fname} (revision {rev}) -> {target!r} not found")
        print()

    if dupes or missing_targets:
        print(
            "Also remove stale bytecode: find alembic/versions -name '__pycache__' -type d -exec rm -rf {} +"
        )
        return 1

    print(f"OK: {len(file_to_rev)} migration files, unique revision ids, down_revision links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
