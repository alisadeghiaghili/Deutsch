#!/usr/bin/env python3
"""Report exact duplicate German lemmas in vocabulary/verb tables."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path


def split_row(line: str) -> list[str] | None:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|") and s.count("|") >= 3):
        return None
    if re.match(r"^\|[\s|:-]+\|$", s):
        return None
    cells = [c.strip() for c in s.strip("|").split("|")]
    if all(set(c) <= set("-: ") and c for c in cells):
        return None
    return cells


def lemma_of(cell: str) -> str:
    c = re.sub(r"[🔵🔴🟢🟡⭐💡]\s*", "", cell).strip()
    c = re.sub(r"^(der|die|das)\s+", "", c, flags=re.I)
    c = re.sub(r"\s*\(Adj\.\).*$", "", c)
    c = re.sub(r"\s*\(sich\).*$", "", c)
    return c.lower().strip()


def scan(path: Path) -> dict[str, list[int]]:
    hits: dict[str, list[int]] = defaultdict(list)
    header = False
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        cells = split_row(line)
        if not cells:
            continue
        joined = " ".join(cells).lower()
        if "german" in joined and not header:
            header = True
            continue
        if not header or len(cells) < 3:
            continue
        lem = lemma_of(cells[0])
        if not lem or lem == "german":
            continue
        hits[lem].append(i)
    return {k: v for k, v in hits.items() if len(v) > 1}


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    total = 0
    for level in ("A1", "A2", "B1", "B2"):
        for rel in ("vocabulary/words.md", "vocabulary/verbs.md"):
            path = root / level / rel
            if not path.exists():
                continue
            dups = scan(path)
            if not dups:
                continue
            print(f"\n{path}: {len(dups)} duplicated lemmas")
            for lem, lines in sorted(dups.items(), key=lambda x: -len(x[1])):
                print(f"  {lem}: lines {lines}")
                total += 1
    print(f"\nTotal duplicated lemma keys: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
