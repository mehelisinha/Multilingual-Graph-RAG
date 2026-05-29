#!/usr/bin/env python3
"""Normalize Python sources for CI: UTF-8 without BOM, LF line endings."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def normalize_file(path: Path) -> bool:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    text = raw.decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    new_bytes = normalized.encode("utf-8")
    if new_bytes != raw:
        path.write_bytes(new_bytes)
        return True
    return False


def main() -> None:
    changed = 0
    for path in BACKEND_ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if normalize_file(path):
            changed += 1
            print(f"normalized: {path.relative_to(BACKEND_ROOT)}")
    print(f"done ({changed} file(s) updated)")


if __name__ == "__main__":
    main()
