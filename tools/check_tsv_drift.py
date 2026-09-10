#!/usr/bin/env python3
"""Fail if committed TSV decks differ from a fresh Markdown export.

Regenerates vocabulary/verb TSV content in memory (via export_tsv helpers)
and compares to files on disk under ``<level>/flashcards/``.

Usage:
  python tools/check_tsv_drift.py [--root PATH]

Exit codes: 0 in sync, 1 drift or missing file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_tsv import (  # noqa: E402
    LEVELS,
    VERB_FIELDS,
    WORD_FIELDS,
    parse_verbs,
    parse_words,
)


def render(rows: list[dict[str, str]], fields: list[str]) -> str:
    lines = ["\t".join(fields)]
    for row in rows:
        lines.append("\t".join(row.get(f, "").replace("\t", " ").strip() for f in fields))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    root = args.root.resolve()
    drift = 0
    for level in LEVELS:
        pairs = (
            (
                root / level / "vocabulary" / "verbs.md",
                root / level / "flashcards" / "verbs-anki.tsv",
                parse_verbs,
                VERB_FIELDS,
            ),
            (
                root / level / "vocabulary" / "words.md",
                root / level / "flashcards" / "vocabulary-anki.tsv",
                parse_words,
                WORD_FIELDS,
            ),
        )
        for md, tsv, parser_fn, fields in pairs:
            if not md.exists():
                print(f"ERROR missing markdown: {md}")
                drift += 1
                continue
            if not tsv.exists():
                print(f"ERROR missing TSV: {tsv}")
                drift += 1
                continue
            expected = render(parser_fn(md), fields)
            actual = tsv.read_text(encoding="utf-8")
            # normalize newlines
            if expected.replace("\r\n", "\n") != actual.replace("\r\n", "\n"):
                print(f"DRIFT {tsv.relative_to(root)} — run: python tools/export_tsv.py --root . --level {level}")
                drift += 1
            else:
                print(f"OK    {tsv.relative_to(root)}")
    if drift:
        print(f"\n{drift} file(s) out of sync with Markdown sources.")
        return 1
    print("\nAll generated TSV decks match Markdown.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
