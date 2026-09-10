#!/usr/bin/env python3
"""Apply high-confidence plural corrections across A1–B2 vocabulary tables."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# lemma_key -> plural cell (or —)
FIX = {
    # mass / abstract: no plural
    "mut": "—",
    "stolz": "—",
    "zorn": "—",
    "hass": "—",
    "neid": "—",
    "trauer": "—",
    "wut": "—",
    "glück": "—",
    "glueck": "—",
    "kummer": "—",
    "vertrauen": "—",
    "wissen": "—",
    "lust": "—",  # Lust as desire; plural Lüste is literary — for A1 list use —
    "ehrgeiz": "—",
    "geduld": "—",
    "furcht": "—",
    "liebe": "—",
    "milch": "—",
    "wasser": "—",
    "käse": "—",
    "kaese": "—",
    "reis": "—",
    "honig": "—",
    "zucker": "—",
    "butter": "—",
    "fleisch": "—",
    "mehl": "—",
    "software": "—",
    "hardware": "—",
    "internet": "—",
    "medizin": "—",
    "mai": "—",
    # correct plurals that were wrong
    "beispiel": "die Beispiele",
    "trinkgeld": "die Trinkgelder",
    "arbeitsamt": "die Arbeitsämter",
    "kino": "die Kinos",
    "herbst": "die Herbste",
    "salz": "die Salze",
    "pfeffer": "—",
    "eigenschaft": "die Eigenschaften",
    "intelligenz": "die Intelligenzen",
    "these": "die Thesen",
    "interesse": "die Interessen",
    "angst": "die Ängste",
    "sinn": "die Sinne",
    "recht": "die Rechte",
    "programm": "die Programme",
    "chat": "die Chats",
    "öl": "die Öle",
    "oel": "die Öle",
    "big data": "—",
    "lust": "—",
}


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


def lemma_key(cell: str) -> str:
    c = re.sub(r"[🔵🔴🟢🟡⭐💡]\s*", "", cell).strip()
    c = re.sub(r"^(der|die|das)\s+", "", c, flags=re.I)
    return c.casefold().strip()


def is_header(cells: list[str]) -> bool:
    j = " ".join(cells).lower()
    return "german" in j and "plural" in j


def process(path: Path) -> int:
    changed = 0
    out: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines(True):
        cells = split_row(line)
        if not cells or is_header(cells) or len(cells) < 6:
            out.append(line)
            continue
        key = lemma_key(cells[0])
        if key not in FIX:
            out.append(line)
            continue
        if cells[5] == FIX[key]:
            out.append(line)
            continue
        cells[5] = FIX[key]
        ending = "\n" if line.endswith("\n") else ""
        out.append("| " + " | ".join(cells) + " |" + ending)
        changed += 1
    if changed:
        path.write_text("".join(out), encoding="utf-8", newline="\n")
    return changed


def main() -> None:
    total = 0
    for level in ("A1", "A2", "B1", "B2"):
        path = ROOT / level / "vocabulary" / "words.md"
        n = process(path)
        print(f"{path.relative_to(ROOT)}: {n} plural cells fixed")
        total += n
    print(f"total={total}")


if __name__ == "__main__":
    main()
