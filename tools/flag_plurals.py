#!/usr/bin/env python3
"""Flag suspicious plural forms in vocabulary tables.

Heuristics (German):
  - Mass/abstract nouns that normally have no plural listed with a fabricated -e/-n/-en plural
  - English-style -s plurals on nouns that do not take -s in German (Software, Internet…)
  - Known wrong pairs from earlier audits

Usage: python tools/flag_plurals.py [--root PATH]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# Nouns that normally have **no** plural (or only special/technical senses).
# Invented forms like die Mute / die Stolze / die Glücke must become —.
NO_PLURAL = {
    "mut", "stolz", "wut", "trauer", "glück", "glueck", "fleisch", "mehl",
    "milch", "wasser", "käse", "kaese", "honig", "zucker", "butter", "öl",
    "reis", "software", "hardware", "internet", "chat", "programm",
    "interesse", "wissen", "vertrauen", "kummer", "schuld", "angst",
    "liebe", "hass", "neid", "zorn", "furcht", "geduld", "ehrgeiz",
    "sinn", "recht", "unrecht", "recht", "glück",
}

# Explicit corrections: (level-agnostic) lemma_key -> correct plural cell or —
# Only high-confidence fixes.
CORRECTIONS = {
    # mass / abstract — no plural
    "mut": "—",
    "stolz": "—",
    "wut": "—",
    "trauer": "—",
    "glück": "—",
    "glueck": "—",
    "fleisch": "—",
    "mehl": "—",
    "milch": "—",
    "wasser": "—",
    "käse": "—",
    "kaese": "—",
    "honig": "—",
    "zucker": "—",
    "butter": "—",
    "öl": "—",
    "oel": "—",
    "reis": "—",
    "software": "—",
    "hardware": "—",
    "internet": "—",
    "chat": "—",
    "interesse": "die Interessen",
    "wissen": "—",
    "vertrauen": "—",
    "kummer": "—",
    "schuld": "die Schulden",  # only in the sense "debts"; guilt is singular — keep plural as debts
    "angst": "die Ängste",
    "liebe": "—",
    "hass": "—",
    "neid": "—",
    "zorn": "—",
    "furcht": "—",
    "geduld": "—",
    "ehrgeiz": "—",
    # previously audited wrong plurals
    "beispiel": "die Beispiele",
    "fußball": "die Fußballspiele",  # or — for the sport; ball: die Fußbälle
    "fussball": "die Fußballspiele",
    "trinkgeld": "die Trinkgelder",
    "arbeitsamt": "die Arbeitsämter",
    "kino": "die Kinos",
    "mai": "—",
    "herbst": "die Herbste",
    "medizin": "—",
    "salz": "die Salze",
    "pfeffer": "die Pfeffer",
    "eigenschaft": "die Eigenschaften",
    "intelligenz": "die Intelligenzen",
    "these": "die Thesen",
    "dissertation": "die Dissertationen",
}

# Pattern: die Mute / die Stolze / die Wuten / die Trauern / die Glücke / die Hässe / die Neide
INVENTED = re.compile(
    r"^die (Mute|Stolze|Wuten|Trauern|Glücke|Hässe|Neide|Zorne|Kummer|"
    r"Vertrauen|Wissen|Softwares|Big Datas|Lusten|Bewusstseins)$",
    re.I,
)


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    flagged = 0
    applied = 0
    for level in ("A1", "A2", "B1", "B2"):
        path = root / level / "vocabulary" / "words.md"
        if not path.exists():
            continue
        out_lines = []
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(True), 1):
            cells = split_row(line)
            if not cells or is_header(cells) or len(cells) < 6:
                out_lines.append(line)
                continue
            key = lemma_key(cells[0])
            plural = cells[5].strip()
            # find plural column more robustly: often index 5
            # header: German English Persian Gender Article Plural Cases
            if plural.lower() in {"plural", "—", "-", ""}:
                out_lines.append(line)
                continue
            suspicious = False
            reason = ""
            if INVENTED.match(plural):
                suspicious = True
                reason = "invented pattern"
            elif key in CORRECTIONS and plural != CORRECTIONS[key] and CORRECTIONS[key] == "—":
                if plural not in {"—", "-", ""}:
                    suspicious = True
                    reason = "should have no plural"
            elif key in NO_PLURAL and plural not in {"—", "-", ""} and key not in {"interesse", "angst", "schuld"}:
                # mass-like: flag for review
                if re.search(r"(en|e|n|s)$", plural, re.I) and "die" in plural.lower():
                    suspicious = True
                    reason = "mass/abstract noun with plural?"
            if suspicious:
                flagged += 1
                print(f"{path.name}:{i}: {key} | plural={plural!r} ({reason})")
                if args.apply and key in CORRECTIONS:
                    cells[5] = CORRECTIONS[key]
                    out_lines.append("| " + " | ".join(cells) + " |")
                    if not line.endswith("\n"):
                        pass
                    else:
                        out_lines[-1] = out_lines[-1] + "\n"
                    applied += 1
                    continue
            out_lines.append(line)
        if args.apply and applied:
            path.write_text("".join(out_lines), encoding="utf-8", newline="\n")
    print(f"flagged={flagged} applied={applied}")


if __name__ == "__main__":
    main()
