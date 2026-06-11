#!/usr/bin/env python3
"""Data quality checks for downloaded JSONL corpora in data/raw."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "raw" / "multieurlex"

REQUIRED_FIELDS = ("document_id", "language", "title", "text")
KNOWN_LANGUAGES = {"de", "en", "fr", "pl"}
MIN_TEXT_CHARS = 200


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate JSONL document records")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to JSONL file or directory (default: latest sample in data/raw/multieurlex)",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=MIN_TEXT_CHARS,
        help=f"Minimum text length in characters (default: {MIN_TEXT_CHARS})",
    )
    return parser.parse_args()


def resolve_input(path: Path | None) -> Path:
    if path is not None:
        return path
    candidates = sorted(DEFAULT_INPUT.glob("sample_*.jsonl"), reverse=True)
    if not candidates:
        raise SystemExit(
            f"No JSONL found in {DEFAULT_INPUT}. Run download_multieurlex.py first."
        )
    return candidates[0]


def iter_lines(path: Path):
    if path.is_dir():
        files = sorted(path.glob("*.jsonl"))
    else:
        files = [path]
    for file_path in files:
        with file_path.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if line:
                    yield file_path, line_no, line


def main() -> None:
    args = parse_args()
    input_path = resolve_input(args.input)

    total = 0
    errors: list[str] = []
    seen_ids: set[str] = set()
    languages: Counter[str] = Counter()
    text_lengths: list[int] = []

    for file_path, line_no, line in iter_lines(input_path):
        total += 1
        where = f"{file_path.name}:{line_no}"

        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{where}: invalid JSON ({exc})")
            continue

        missing = [f for f in REQUIRED_FIELDS if not record.get(f)]
        if missing:
            errors.append(f"{where}: missing fields {missing}")
            continue

        doc_id = str(record["document_id"])
        if doc_id in seen_ids:
            errors.append(f"{where}: duplicate document_id {doc_id!r}")
        seen_ids.add(doc_id)

        lang = str(record["language"])
        languages[lang] += 1
        if lang not in KNOWN_LANGUAGES:
            errors.append(f"{where}: unexpected language {lang!r}")

        text_len = len(str(record["text"]))
        text_lengths.append(text_len)
        if text_len < args.min_chars:
            errors.append(f"{where}: text too short ({text_len} < {args.min_chars} chars)")

    print(f"Validated {total} records from {input_path}")
    if languages:
        print("Languages:", dict(sorted(languages.items())))
    if text_lengths:
        print(
            f"Text length (chars): min={min(text_lengths)} "
            f"avg={sum(text_lengths) // len(text_lengths)} max={max(text_lengths)}"
        )

    if errors:
        print(f"\n{len(errors)} problem(s) found:")
        for error in errors[:50]:
            print(f"  - {error}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more")
        sys.exit(1)

    print("All checks passed.")


if __name__ == "__main__":
    main()
